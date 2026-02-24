import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone

BLOB_BASE = "https://blob.vercel-storage.com"
LEADS_KEY = "strive-leads/leads.json"


def _token():
    t = os.environ.get("BLOB_READ_WRITE_TOKEN", "")
    if not t:
        raise RuntimeError("BLOB_READ_WRITE_TOKEN not set")
    return t


def _fetch_leads():
    """Download current leads list from Blob, return [] if not found."""
    url = f"{BLOB_BASE}?prefix={LEADS_KEY}&limit=1"
    req = urllib.request.Request(url, headers={"authorization": f"Bearer {_token()}"})
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        blobs = data.get("blobs", [])
        if not blobs:
            return []
        req2 = urllib.request.Request(blobs[0]["url"], headers={"authorization": f"Bearer {_token()}"})
        with urllib.request.urlopen(req2) as r2:
            return json.loads(r2.read())
    except Exception:
        return []


def _save_leads(leads):
    """Upload full leads list back to Blob (overwrites)."""
    payload = json.dumps(leads, ensure_ascii=False).encode()
    req = urllib.request.Request(
        f"{BLOB_BASE}/{LEADS_KEY}",
        data=payload,
        headers={
            "authorization": f"Bearer {_token()}",
            "content-type": "application/json",
            "x-content-type": "application/json",
            "x-add-random-suffix": "0",
        },
        method="PUT",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            leads = _fetch_leads()
            new_id = (leads[-1]["id"] + 1) if leads else 1
            record = {
                "id": new_id,
                "company_name":    body.get("companyName", ""),
                "contact_number":  body.get("contactNumber", ""),
                "email":           body.get("email", ""),
                "number_of_units": body.get("numberOfUnits", ""),
                "comments":        body.get("comments", ""),
                "created_at":      datetime.now(timezone.utc).isoformat(),
            }
            leads.append(record)
            _save_leads(leads)
            self._respond(200, {"success": True, "id": new_id})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_OPTIONS(self):
        self._respond(200, {})

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
