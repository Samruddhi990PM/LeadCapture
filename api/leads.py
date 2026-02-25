"""
Single API file handling:
  POST /api/leads  — save a new lead
  GET  /api/leads  — return all leads

Uses vercel_blob package (pip install vercel_blob).
Confirmed working signature: vercel_blob.put(pathname, body, options_dict)
"""
import json
import os
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone
from urllib.parse import urlparse

import vercel_blob

LEADS_PATH = "leads/leads.json"


def _read_leads() -> list:
    try:
        result = vercel_blob.list({"prefix": LEADS_PATH, "limit": 1})
        blobs = result.get("blobs", [])
        if not blobs:
            return []
        data = vercel_blob.get(blobs[0]["url"])
        return json.loads(data)
    except Exception:
        return []


def _write_leads(leads: list):
    payload = json.dumps(leads, ensure_ascii=False, indent=2).encode("utf-8")
    vercel_blob.put(LEADS_PATH, payload, {
        "access": "private",
        "addRandomSuffix": False,
        "contentType": "application/json",
    })


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
