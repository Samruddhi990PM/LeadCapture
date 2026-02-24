import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

BLOB_API = "https://blob.vercel-storage.com"
LEADS_PATH = "strive-leads/leads.json"


def _token():
    t = os.environ.get("BLOB_READ_WRITE_TOKEN", "")
    if not t:
        raise RuntimeError("BLOB_READ_WRITE_TOKEN not set")
    return t


def _blob_headers():
    return {
        "authorization": f"Bearer {_token()}",
        "x-api-version": "7",
        "accept": "application/json",
    }


def _fetch_leads():
    req = urllib.request.Request(
        f"{BLOB_API}?prefix={LEADS_PATH}&limit=1",
        headers=_blob_headers()
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
        blobs = data.get("blobs", [])
        if not blobs:
            return []
        with urllib.request.urlopen(blobs[0]["url"], timeout=10) as r2:
            return json.loads(r2.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise RuntimeError(f"Fetch error {e.code}: {e.read().decode()}")


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            leads = _fetch_leads()
            leads_sorted = sorted(leads, key=lambda x: x.get("created_at", ""), reverse=True)
            self._respond(200, {"leads": leads_sorted, "count": len(leads_sorted)})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_OPTIONS(self):
        self._respond(200, {})

    def _respond(self, status, body):
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass
