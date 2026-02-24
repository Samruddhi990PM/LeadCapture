import json
import os
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone

import vercel_blob


LEADS_PATHNAME = "strive-leads/leads.json"


def _fetch_leads():
    """List blobs, find the leads file, return its parsed JSON."""
    result = vercel_blob.list({"prefix": LEADS_PATHNAME, "limit": "1"})
    blobs = result.get("blobs", [])
    if not blobs:
        return []
    # Download raw bytes from the CDN URL
    data = vercel_blob.download_file_content(blobs[0]["url"])
    return json.loads(data.decode("utf-8"))


def _save_leads(leads):
    """Upload (overwrite) the leads JSON file to Vercel Blob."""
    payload = json.dumps(leads, ensure_ascii=False, indent=2).encode("utf-8")
    return vercel_blob.put(
        LEADS_PATHNAME,
        payload,
        {"addRandomSuffix": "false", "contentType": "application/json"},
    )


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8"))

            leads = _fetch_leads()
            new_id = (leads[-1]["id"] + 1) if leads else 1

            record = {
                "id":             new_id,
                "company_name":   body.get("companyName", "").strip(),
                "contact_number": body.get("contactNumber", "").strip(),
                "email":          body.get("email", "").strip(),
                "number_of_units": body.get("numberOfUnits", ""),
                "comments":       body.get("comments", "").strip(),
                "created_at":     datetime.now(timezone.utc).isoformat(),
            }
            leads.append(record)
            result = _save_leads(leads)
            self._respond(200, {"success": True, "id": new_id, "url": result.get("url", "")})

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
