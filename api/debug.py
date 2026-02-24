"""
Debug endpoint - tests both LIST and POST (upload) to Vercel Blob.
Visit /api/debug after deploying to diagnose issues.
Delete once everything works.
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

        result["1_token_set"] = bool(token)
        result["1_token_preview"] = (token[:24] + "...") if token else "MISSING"

        if not token:
            self._respond(200, result)
            return

        # Test 1: LIST
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
        except urllib.error.HTTPError as e:
            result["2_list_ok"] = False
            result["2_list_error"] = f"HTTP {e.code}"
            result["2_list_error_body"] = e.read().decode()
        except Exception as e:
            result["2_list_ok"] = False
            result["2_list_error"] = str(e)

        # Test 2: POST (upload) a tiny test file
        try:
            test_payload = json.dumps({"test": True}).encode("utf-8")
            post_url = f"{BLOB_API}/strive-leads/debug-test.json"
            req2 = urllib.request.Request(
                post_url,
                data=test_payload,
                method="POST",
                headers={
                    "authorization": f"Bearer {token}",
                    "content-type": "application/json",
                    "x-add-random-suffix": "0",
                    "accept": "application/json",
                }
            )
            with urllib.request.urlopen(req2, timeout=10) as r2:
                put_data = json.loads(r2.read().decode())
            result["3_upload_ok"] = True
            result["3_upload_url"] = put_data.get("url", "")
            result["3_upload_response"] = put_data
        except urllib.error.HTTPError as e:
            result["3_upload_ok"] = False
            result["3_upload_error"] = f"HTTP {e.code}: {e.reason}"
            try:
                result["3_upload_error_body"] = e.read().decode()
            except Exception:
                pass
        except Exception as e:
            result["3_upload_ok"] = False
            result["3_upload_error"] = str(e)

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
