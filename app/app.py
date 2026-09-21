import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import psycopg2


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        database=os.environ.get("DB_NAME", "appdb"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres")
    )


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS calculations (
            id SERIAL PRIMARY KEY,
            operation VARCHAR(20),
            a FLOAT,
            b FLOAT,
            result FLOAT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def save_calculation(operation, a, b, result):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO calculations (operation, a, b, result) VALUES (%s, %s, %s, %s)",
        (operation, a, b, result)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_history():
    conn = get_db_connection()
    cur = conn.cursor()
    query = (
        "SELECT operation, a, b, result FROM calculations "
        "ORDER BY id DESC LIMIT 10"
    )
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

        if self.path == "/history":
            rows = get_history()
            body = "\n".join([f"{r[0]}({r[1]},{r[2]})={r[3]}" for r in rows])
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body.encode())
            return

        result = add(2, 3)
        save_calculation("add", 2, 3, result)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"v3-eks - add(2,3)={result}".encode())

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    init_db()
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("Server running on port 8080")
    server.serve_forever()
