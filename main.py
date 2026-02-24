"""URL Shortener API - Shorten and track URLs."""
import hashlib, json, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_FILE = "urls.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def shorten(url):
    db = load_db()
    code = hashlib.md5(url.encode()).hexdigest()[:6]
    if code not in db:
        db[code] = {"url": url, "hits": 0}
        save_db(db)
    return code

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        parsed = urlparse(self.path)
        db = load_db()
        if parsed.path == "/shorten":
            params = parse_qs(parsed.query)
            url = params.get("url", [""])[0]
            if not url:
                self.respond(400, {"error": "url param required"})
                return
            code = shorten(url)
            self.respond(200, {"short": f"http://localhost:8080/{code}", "code": code})
        elif parsed.path.lstrip("/") in db:
            code = parsed.path.lstrip("/")
            db[code]["hits"] += 1
            save_db(db)
            self.send_response(302)
            self.send_header("Location", db[code]["url"])
            self.end_headers()
        else:
            self.respond(404, {"error": "Not found"})

    def respond(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    print("URL Shortener running at http://localhost:8080")
    print("Usage: GET /shorten?url=https://example.com")
    HTTPServer(("", 8080), Handler).serve_forever()
