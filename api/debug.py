"""
Debug endpoint — visit /api/debug to diagnose Blob connectivity.
Shows token status, list API response, and tests a PUT write.
Delete this file once everything is working.
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
        token = os.environ.get("BLOB_READ_WRITE_TOKEN", "")

        # 1. Token check
        result["1_token_set"] = bool(token)
        result["1_token_prefix"] = (token[:20] + "...") if token else "MISSING"

        if not token:
            self._respond(200, result)
            return

        # 2. Test LIST
        try:
            list_url = f"{BLOB_API}?prefix={LEADS_PATHNAME}&limit=1"
            req = urllib.request.Request(
                list_url,
                headers={"authorization": f"Bearer {token}", "accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                list_data = json.loads(r.read().decode())
            result["2_list_ok"] = True
            result["2_blobs_found"] = len(list_data.get("blobs", []))
            result["2_list_response"] = list_data
        except urllib.error.HTTPError as e:
            result["2_list_ok"] = False
            result["2_list_error"] = f"HTTP {e.code}: {e.reason}"
            try:
                result["2_list_error_body"] = e.read().decode()
            except Exception:
                pass

        # 3. Test PUT write
        try:
            test_payload = json.dumps({"debug": True}).encode("utf-8")
            put_url = f"{BLOB_API}/strive-leads/debug-test.json"
            req2 = urllib.request.Request(
                put_url,
                data=test_payload,
                method="PUT",
                headers={
                    "authorization": f"Bearer {token}",
                    "x-content-type": "application/json",
                    "x-add-random-suffix": "0",
                    "content-type": "application/octet-stream",
                    "content-length": str(len(test_payload)),
                    "accept": "application/json",
                }
            )
            with urllib.request.urlopen(req2, timeout=10) as r2:
                put_data = json.loads(r2.read().decode())
            result["3_put_ok"] = True
            result["3_put_url"] = put_data.get("url", "")
        except urllib.error.HTTPError as e:
            result["3_put_ok"] = False
            result["3_put_error"] = f"HTTP {e.code}: {e.reason}"
            try:
                result["3_put_error_body"] = e.read().decode()
            except Exception:
                pass
        except Exception as e:
            result["3_put_ok"] = False
            result["3_put_error"] = str(e)

        self._respond(200, result)

    def _respond(self, status, body):
        payload = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass
