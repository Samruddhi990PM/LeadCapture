import json
from http.server import BaseHTTPRequestHandler

import vercel_blob

LEADS_PATHNAME = "strive-leads/leads.json"


def _fetch_leads():
    result = vercel_blob.list({"prefix": LEADS_PATHNAME, "limit": "1"})
    blobs = result.get("blobs", [])
    if not blobs:
        return []
    data = vercel_blob.download_file_content(blobs[0]["url"])
    return json.loads(data.decode("utf-8"))


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
