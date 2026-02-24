import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone

BLOB_API = "https://blob.vercel-storage.com"
LEADS_PATH = "strive-leads/leads.json"


def _token():
    t = os.environ.get("BLOB_READ_WRITE_TOKEN", "")
    if not t:
        raise RuntimeError("BLOB_READ_WRITE_TOKEN not set")
    return t


def _auth_headers():
    return {
        "authorization": f"Bearer {_token()}",
        "x-api-version": "7",
        "accept": "application/json",
    }


def _fetch_leads():
    # List blobs to find the file
    req = urllib.request.Request(
        f"{BLOB_API}?prefix={LEADS_PATH}&limit=1",
        headers=_auth_headers()
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
        blobs = data.get("blobs", [])
        if not blobs:
            return []
        # Private store download requires auth token
        req2 = urllib.request.Request(blobs[0]["url"], headers=_auth_headers())
        with urllib.request.urlopen(req2, timeout=10) as r2:
            return json.loads(r2.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise RuntimeError(f"Fetch error {e.code}: {e.read().decode()}")


def _save_leads(leads):
    payload = json.dumps(leads, ensure_ascii=False, indent=2).encode("utf-8")
    headers = _auth_headers()
    headers.update({
        "content-type": "application/octet-stream",
        "x-content-type": "application/json",
        "x-add-random-suffix": "0"
    })
    req = urllib.request.Request(
        f"{BLOB_API}/{LEADS_PATH}",
        data=payload,
        method="PUT",
        headers=headers
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"PUT error {e.code}: {body}")


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
