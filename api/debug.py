import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

BLOB_API = "https://blob.vercel-storage.com"
LEADS_PATH = "strive-leads/leads.json"


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        result = {}
        token = os.environ.get("BLOB_READ_WRITE_TOKEN", "")
        result["1_token_set"] = bool(token)
        result["1_token_preview"] = (token[:24] + "...") if token else "MISSING"

        if not token:
            self._respond(200, result)
            return

        headers = {
            "authorization": f"Bearer {token}",
            "x-api-version": "7",
            "accept": "application/json",
        }

        # Test LIST
        try:
            req = urllib.request.Request(
                f"{BLOB_API}?prefix={LEADS_PATH}&limit=1",
                headers=headers
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                list_data = json.loads(r.read().decode())
            result["2_list_ok"] = True
            result["2_blobs_found"] = len(list_data.get("blobs", []))
        except urllib.error.HTTPError as e:
            result["2_list_ok"] = False
            result["2_list_error"] = f"HTTP {e.code}: {e.read().decode()}"
        except Exception as e:
            result["2_list_ok"] = False
            result["2_list_error"] = str(e)

        # Test PUT — write a small test file
        try:
            payload = json.dumps({"test": True}).encode("utf-8")
            put_headers = dict(headers)
            put_headers.update({
                "content-type": "application/octet-stream",
                "x-content-type": "application/json",
                "x-add-random-suffix": "0",
            })
            req2 = urllib.request.Request(
                f"{BLOB_API}/strive-leads/debug-test.json",
                data=payload,
                method="PUT",
                headers=put_headers
            )
            with urllib.request.urlopen(req2, timeout=10) as r2:
                put_data = json.loads(r2.read().decode())
            result["3_put_ok"] = True
            result["3_put_url"] = put_data.get("url", "")

            # Test reading back the file with auth (private store)
            req3 = urllib.request.Request(put_data["url"], headers=headers)
            with urllib.request.urlopen(req3, timeout=10) as r3:
                read_back = json.loads(r3.read().decode())
            result["4_read_back_ok"] = True
            result["4_read_back"] = read_back

        except urllib.error.HTTPError as e:
            result["3_put_ok"] = False
            result["3_put_error"] = f"HTTP {e.code}: {e.reason}"
            result["3_put_body"] = e.read().decode()
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
