"""One-time (and every ~60 days) LinkedIn sign-in. Run this on your laptop, not in GitHub.

What it does:
  1. Opens LinkedIn in your browser so you can approve your own app (scopes: openid profile w_member_social).
  2. Catches the redirect on http://localhost:8765/callback and swaps the code for an access token.
  3. Looks up your member id, and stores three things in the GitHub repo with the gh CLI:
       secret   LINKEDIN_ACCESS_TOKEN
       variable LINKEDIN_PERSON_URN      (urn:li:person:...)
       variable LINKEDIN_TOKEN_EXPIRES   (YYYY-MM-DD, so the pipeline can warn you a week early)

Usage:
  export LINKEDIN_CLIENT_ID=...  LINKEDIN_CLIENT_SECRET=...
  python scripts/linkedin_auth.py --repo theboxer85/linkedin-content-pipeline
Needs: Python 3.10+, `pip install requests`, and gh signed in (`gh auth login`).
"""
from __future__ import annotations

import argparse
import datetime as dt
import http.server
import os
import secrets
import subprocess
import sys
import threading
import urllib.parse
import webbrowser

import requests

REDIRECT = "http://localhost:8765/callback"
SCOPES = "openid profile w_member_social"


class Catcher(http.server.BaseHTTPRequestHandler):
    result: dict = {}

    def do_GET(self):  # noqa: N802
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        Catcher.result = {k: v[0] for k, v in q.items()}
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Done. You can close this tab and go back to the terminal.")

    def log_message(self, *args):
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="owner/name of the pipeline repo")
    args = ap.parse_args()
    cid, csec = os.environ.get("LINKEDIN_CLIENT_ID"), os.environ.get("LINKEDIN_CLIENT_SECRET")
    if not cid or not csec:
        print("Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET first (from your LinkedIn app's Auth tab).")
        return 2

    state = secrets.token_urlsafe(16)
    url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode(
        {"response_type": "code", "client_id": cid, "redirect_uri": REDIRECT, "state": state, "scope": SCOPES})
    server = http.server.HTTPServer(("localhost", 8765), Catcher)
    threading.Thread(target=server.handle_request, daemon=True).start()
    print("Opening LinkedIn to approve the app. If the browser doesn't open, visit:\n" + url)
    webbrowser.open(url)
    while not Catcher.result:
        threading.Event().wait(0.5)
    server.server_close()

    if Catcher.result.get("state") != state or "code" not in Catcher.result:
        print(f"Sign-in failed: {Catcher.result}")
        return 1
    tok = requests.post("https://www.linkedin.com/oauth/v2/accessToken", data={
        "grant_type": "authorization_code", "code": Catcher.result["code"], "redirect_uri": REDIRECT,
        "client_id": cid, "client_secret": csec}, timeout=30)
    tok.raise_for_status()
    token = tok.json()["access_token"]
    expires = dt.date.today() + dt.timedelta(seconds=int(tok.json().get("expires_in", 5184000)))
    me = requests.get("https://api.linkedin.com/v2/userinfo", headers={"Authorization": f"Bearer {token}"}, timeout=30)
    me.raise_for_status()
    urn = f"urn:li:person:{me.json()['sub']}"

    subprocess.run(["gh", "secret", "set", "LINKEDIN_ACCESS_TOKEN", "--repo", args.repo, "--body", token], check=True)
    subprocess.run(["gh", "variable", "set", "LINKEDIN_PERSON_URN", "--repo", args.repo, "--body", urn], check=True)
    subprocess.run(["gh", "variable", "set", "LINKEDIN_TOKEN_EXPIRES", "--repo", args.repo, "--body",
                    expires.isoformat()], check=True)
    print(f"Saved. Signed in as {me.json().get('name', urn)}. Token expires {expires}; you'll get an issue a week before.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
