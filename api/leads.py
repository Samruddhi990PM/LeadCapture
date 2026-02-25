"""
Single API file:
  POST /api/leads  — save a new lead
  GET  /api/leads  — return all leads

Requires a PUBLIC Vercel Blob store (public is the default when creating).
The BLOB_READ_WRITE_TOKEN is still required to write — only reads are public.
"""
import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone
from urllib.parse import urlparse

BLOB_API = "https://blob.vercel-storage.com"
LEADS_PATH = "leads/leads.json"


def _token():
    t = os.environ.get("BLOB_READ_WRITE_TOKEN", "")
    if not t:
        raise RuntimeError("BLOB_READ_WRITE_TOKEN not set — connect Blob store in Vercel dashboard")
    return t


def _read_leads() -> list:
    # Step 1: find the file
    req = urllib.request.Request(
        f"{BLOB_API}?prefix={LEADS_PATH}&limit=1",
        headers={"authorization": f"Bearer {_token()}", "x-api-version": "7"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        blobs = json.loads(r.read()).get("blobs", [])
    if not blobs:
        return []
    # Step 2: fetch file from public CDN URL (no auth needed for public store)
    with urllib.request.urlopen(blobs[0]["url"], timeout=10) as r:
        return json.loads(r.read())


def _write_leads(leads: list):
    payload = json.dumps(leads, ensure_ascii=False, indent=2).encode("utf-8")
    req = urllib.request.Request(
        f"{BLOB_API}/{LEADS_PATH}",
        data=payload,
        method="PUT",
        headers={
            "authorization": f"Bearer {_token()}",
            "x-api-version": "7",
            "x-content-type": "application/json",
            "x-add-random-suffix": "0",
            "content-type": "application/octet-stream",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self._path() != "/api/leads":
            return self._respond(404, {"error": "not found"})
        try:
            leads = _read_leads()
            leads.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            self._respond(200, {"leads": leads, "count": len(leads)})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_POST(self):
        if self._path() != "/api/leads":
            return self._respond(404, {"error": "not found"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            leads = _read_leads()
            record = {
                "id":              (leads[-1]["id"] + 1) if leads else 1,
                "company_name":    body.get("companyName", "").strip(),
                "contact_number":  body.get("contactNumber", "").strip(),
                "email":           body.get("email", "").strip(),
                "number_of_units": body.get("numberOfUnits", ""),
                "comments":        body.get("comments", "").strip(),
                "created_at":      datetime.now(timezone.utc).isoformat(),
            }
            leads.append(record)
            _write_leads(leads)
            self._respond(200, {"success": True, "id": record["id"]})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_OPTIONS(self):
        self._respond(200, {})

    def _path(self):
        return urlparse(self.path).path

    def _respond(self, status, body):
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass
