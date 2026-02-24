import json
import os
from http.server import BaseHTTPRequestHandler
import psycopg2


def get_conn():
    return psycopg2.connect(os.environ["POSTGRES_URL"])


def init_db(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            company_name TEXT,
            contact_number TEXT,
            email TEXT,
            number_of_units INTEGER,
            comments TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)

            conn = get_conn()
            cur = conn.cursor()
            init_db(cur)

            cur.execute(
                """INSERT INTO leads
                   (company_name, contact_number, email, number_of_units, comments)
                   VALUES (%s, %s, %s, %s, %s)
                   RETURNING id""",
                (
                    data.get("companyName"),
                    data.get("contactNumber"),
                    data.get("email"),
                    int(data.get("numberOfUnits") or 0),
                    data.get("comments"),
                ),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()

            self._respond(200, {"success": True, "id": new_id})

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

    def log_message(self, format, *args):
        pass  # suppress default logging
