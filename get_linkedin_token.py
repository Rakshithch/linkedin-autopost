import webbrowser, requests, urllib.parse, threading, time
from http.server import HTTPServer, BaseHTTPRequestHandler

CLIENT_ID = "78xzajww4w6i47"
CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
REDIRECT_URI = "http://localhost:8000/callback"
SCOPES = "openid profile w_member_social"

result = {"code": None}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in params:
            result["code"] = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2 style='font-family:sans-serif;padding:40px'>Success! Return to terminal.</h2>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h2>Error. Try again.</h2>")
    def log_message(self, *a): pass

# Start server FIRST
server = HTTPServer(("localhost", 8000), Handler)
print("Server started on port 8000...")

# Open browser after short delay
def open_browser():
    time.sleep(1.5)
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": "rak"
    }
    url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode(params)
    print("Opening LinkedIn in browser...")
    webbrowser.open(url)

threading.Thread(target=open_browser, daemon=True).start()

print("Waiting for LinkedIn authorization (click Allow in browser)...")
while result["code"] is None:
    server.handle_request()

code = result["code"]
print(f"Got authorization code!")

# Exchange for token
print("Fetching access token...")
r = requests.post(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)

if r.status_code != 200:
    print(f"Token error: {r.status_code} {r.text}")
    exit(1)

token = r.json()["access_token"]
print(f"Got access token!")

# Get user info
print("Fetching your LinkedIn profile...")
r2 = requests.get(
    "https://api.linkedin.com/v2/userinfo",
    headers={"Authorization": f"Bearer {token}"}
)

if r2.status_code == 200:
    data = r2.json()
    sub = data.get("sub", "")
    name = data.get("name", "Unknown")
    print(f"Logged in as: {name}")
    urn = f"urn:li:person:{sub}"
else:
    print(f"Could not fetch profile: {r2.status_code} {r2.text}")
    urn = "FETCH_FAILED"

print("\n" + "=" * 60)
print("SAVE THESE AS GITHUB SECRETS:")
print("=" * 60)
print(f"LINKEDIN_ACCESS_TOKEN  ->  {token}")
print(f"LINKEDIN_USER_URN      ->  {urn}")
print(f"ANTHROPIC_API_KEY      ->  (from console.anthropic.com/api-keys)")
print("=" * 60)
