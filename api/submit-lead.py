import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone

# Vercel Blob REST API — correct endpoints
BLOB_API = "https://blob.vercel-storage.com"
LEADS_PATHNAME = "strive-leads/leads.json"


def _token():
    t = os.environ.get("BLOB_READ_WRITE_TOKEN", "")
    if not t:
        raise RuntimeError("BLOB_READ_WRITE_TOKEN env var not set")
    return t


def _fetch_leads():
    """
    List blobs with the given prefix, then download the JSON.
    Vercel Blob list API: GET https://blob.vercel-storage.com?prefix=...
    Returns [] if file doesn't exist yet.
    """
    token = _token()
    list_url = f"{BLOB_API}?prefix={LEADS_PATHNAME}&limit=1&mode=folded"
    req = urllib.request.Request(
        list_url,
        headers={"authorization": f"Bearer {token}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())

        blobs = data.get("blobs", [])
        if not blobs:
            return []

        # Download the actual file via its public URL
        file_url = blobs[0]["url"]
        req2 = urllib.request.Request(file_url, headers={"authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req2, timeout=10) as r2:
            return json.loads(r2.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise
    except Exception:
        return []


def _save_leads(leads):
    """
    Upload (PUT) the full leads list to Vercel Blob.
    Correct endpoint: PUT https://blob.vercel-storage.com/{pathname}
    Headers needed: authorization, x-content-type, x-add-random-suffix=0
    """
    token = _token()
    payload = json.dumps(leads, ensure_ascii=False, indent=2).encode("utf-8")

    # Vercel Blob PUT: the pathname goes in the URL
    put_url = f"{BLOB_API}/{LEADS_PATHNAME}"
    req = urllib.request.Request(
        put_url,
        data=payload,
        method="PUT",
        headers={
            "authorization": f"Bearer {token}",
            "x-content-type": "application/json",
            "x-add-random-suffix": "0",
            "content-length": str(len(payload)),
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode())

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
            self._respond(200, {"success": True, "id": new_id, "blob_url": result.get("url", "")})

        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_OPTIONS(self):
        self._respond(200, {})

    def _respond(self, status, body):
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass
