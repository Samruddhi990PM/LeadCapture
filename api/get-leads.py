import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler

BLOB_BASE = "https://blob.vercel-storage.com"
LEADS_KEY = "strive-leads/leads.json"


def _token():
    t = os.environ.get("BLOB_READ_WRITE_TOKEN", "")
    if not t:
        raise RuntimeError("BLOB_READ_WRITE_TOKEN not set")
    return t


def _fetch_leads():
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


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            leads = _fetch_leads()
            # Sort newest first
            leads_sorted = sorted(leads, key=lambda x: x.get("created_at", ""), reverse=True)
            self._respond(200, {"leads": leads_sorted})
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
