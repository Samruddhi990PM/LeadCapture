import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone

BLOB_API = "https://blob.vercel-storage.com"
LEADS_PATHNAME = "strive-leads/leads.json"


def _token():
    t = os.environ.get("BLOB_READ_WRITE_TOKEN", "")
    if not t:
        raise RuntimeError("BLOB_READ_WRITE_TOKEN not set")
    return t


def _fetch_leads():
    """List blobs, then fetch the JSON from the CDN URL."""
    token = _token()
    list_url = f"{BLOB_API}?prefix={LEADS_PATHNAME}&limit=1"
    req = urllib.request.Request(
        list_url,
        headers={"authorization": f"Bearer {token}", "accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
        blobs = data.get("blobs", [])
        if not blobs:
            return []
        # CDN URL is public — no auth needed
        req2 = urllib.request.Request(blobs[0]["url"])
        with urllib.request.urlopen(req2, timeout=10) as r2:
            return json.loads(r2.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise RuntimeError(f"Fetch error {e.code}: {e.read().decode()}")


def _save_leads(leads):
    """
    Vercel Blob upload — correct method:
    POST https://blob.vercel-storage.com/{pathname}
    with the raw bytes as body and the token + content-type as headers.
    The x-add-random-suffix: 0 header keeps the exact pathname.
    """
    token = _token()
    payload = json.dumps(leads, ensure_ascii=False, indent=2).encode("utf-8")

    # Correct: POST (not PUT) to the blob API
    req = urllib.request.Request(
        f"{BLOB_API}/{LEADS_PATHNAME}",
        data=payload,
        method="POST",
        headers={
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
            "x-add-random-suffix": "0",
            "accept": "application/json",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Blob upload error {e.code}: {body}")


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
