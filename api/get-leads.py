import json
import os
from http.server import BaseHTTPRequestHandler
import psycopg2
import psycopg2.extras


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

    def do_GET(self):
        try:
            conn = get_conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            init_db(cur)
            conn.commit()

            cur.execute("SELECT * FROM leads ORDER BY created_at DESC")
            rows = cur.fetchall()
            cur.close()
            conn.close()

            # Convert to serialisable list
            leads = []
            for row in rows:
                r = dict(row)
                if r.get("created_at"):
                    r["created_at"] = r["created_at"].isoformat()
                leads.append(r)

            self._respond(200, {"leads": leads})

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
        pass
