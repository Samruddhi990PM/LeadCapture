"""
Temporary debug endpoint — visit /api/debug in your browser to verify:
- BLOB_READ_WRITE_TOKEN is set
- Blob API is reachable
- The leads file exists (or not yet)

DELETE this file once everything is confirmed working.
"""
import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

BLOB_API = "https://blob.vercel-storage.com"
LEADS_PATHNAME = "strive-leads/leads.json"


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        result = {}

        # 1. Check token
        token = os.environ.get("BLOB_READ_WRITE_TOKEN", "")
        result["token_set"] = bool(token)
        result["token_prefix"] = token[:12] + "..." if token else "MISSING"

        # 2. Try listing blobs
        if token:
            try:
                list_url = f"{BLOB_API}?prefix={LEADS_PATHNAME}&limit=1&mode=folded"
                req = urllib.request.Request(
                    list_url,
                    headers={"authorization": f"Bearer {token}"}
                )
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.loads(r.read().decode())
                result["blob_list_ok"] = True
                result["blobs_found"] = len(data.get("blobs", []))
                result["blob_data"] = data
            except urllib.error.HTTPError as e:
                result["blob_list_ok"] = False
                result["blob_error"] = f"HTTP {e.code}: {e.reason}"
                try:
                    result["blob_error_body"] = e.read().decode()
                except Exception:
                    pass
            except Exception as e:
                result["blob_list_ok"] = False
                result["blob_error"] = str(e)

        payload = json.dumps(result, indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass
