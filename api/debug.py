import json
import os
from http.server import BaseHTTPRequestHandler

import vercel_blob

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

        # Test LIST
        try:
            list_result = vercel_blob.list({"prefix": LEADS_PATHNAME, "limit": "1"})
            result["2_list_ok"] = True
            result["2_blobs_found"] = len(list_result.get("blobs", []))
        except Exception as e:
            result["2_list_ok"] = False
            result["2_list_error"] = str(e)

        # Test PUT upload
        try:
            test_payload = json.dumps({"test": True}).encode("utf-8")
            put_result = vercel_blob.put(
                "strive-leads/debug-test.json",
                test_payload,
                {"addRandomSuffix": "false", "contentType": "application/json"},
            )
            result["3_upload_ok"] = True
            result["3_upload_url"] = put_result.get("url", "")
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
