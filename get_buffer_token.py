"""
Buffer OAuth Token Helper
Run this ONCE locally to get your Buffer access token + profile ID.
You only need to run this once — then save those values as GitHub Secrets.

Usage:
    pip install requests
    python get_buffer_token.py
"""

import webbrowser
import requests
from urllib.parse import urlencode, urlparse, parse_qs

# ─── STEP 1: Paste your Buffer app credentials here ───────────────────────────
CLIENT_ID = "YOUR_CLIENT_ID_HERE"
CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
REDIRECT_URI = "http://localhost"  # Must match what you set in Buffer app settings
# ──────────────────────────────────────────────────────────────────────────────


def get_authorization_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
    }
    return f"https://buffer.com/oauth2/authorize?{urlencode(params)}"


def exchange_code_for_token(code: str) -> str:
    response = requests.post("https://api.bufferapp.com/1/oauth2/token.json", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
        "grant_type": "authorization_code",
    })

    if response.status_code != 200:
        print(f"Error: {response.status_code} — {response.text}")
        raise RuntimeError("Token exchange failed")

    return response.json()["access_token"]


def get_linkedin_profile_id(access_token: str) -> str:
    response = requests.get(
        "https://api.bufferapp.com/1/profiles.json",
        params={"access_token": access_token}
    )
    profiles = response.json()

    print("\n📋 Your Buffer connected profiles:")
    for i, p in enumerate(profiles):
        service = p.get("service", "unknown")
        name = p.get("formatted_username") or p.get("service_username", "unknown")
        pid = p.get("id")
        print(f"  [{i}] {service.upper()} — @{name}  →  ID: {pid}")

    # Find LinkedIn profile
    linkedin_profiles = [p for p in profiles if p.get("service") == "linkedin"]

    if not linkedin_profiles:
        print("\n⚠️  No LinkedIn profile found in Buffer. Connect LinkedIn in Buffer first.")
        return ""

    profile = linkedin_profiles[0]
    return profile["id"]


def main():
    print("=" * 60)
    print("  Buffer OAuth Token Setup")
    print("=" * 60)

    if CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        print("\n❌ Please open this file and fill in CLIENT_ID and CLIENT_SECRET first.")
        print("   Get them from: https://buffer.com/developers/apps")
        return

    # Step 1: Open browser for authorization
    auth_url = get_authorization_url()
    print(f"\n🌐 Opening Buffer authorization in your browser...")
    print(f"   URL: {auth_url}\n")
    webbrowser.open(auth_url)

    # Step 2: Get the redirect URL from user
    print("After authorizing, you'll be redirected to a URL that looks like:")
    print("  http://localhost/?code=SOME_CODE_HERE\n")
    redirect_url = input("📋 Paste that full redirect URL here: ").strip()

    # Extract code
    parsed = urlparse(redirect_url)
    code = parse_qs(parsed.query).get("code", [None])[0]

    if not code:
        print("❌ Could not extract code from URL. Try again.")
        return

    # Step 3: Exchange for token
    print("\n🔄 Exchanging code for access token...")
    access_token = exchange_code_for_token(code)
    print(f"✅ Access Token: {access_token}")

    # Step 4: Get LinkedIn profile ID
    print("\n🔍 Fetching your Buffer profiles...")
    profile_id = get_linkedin_profile_id(access_token)

    if profile_id:
        print(f"\n✅ LinkedIn Profile ID: {profile_id}")

    # Final output
    print("\n" + "=" * 60)
    print("  📌 SAVE THESE AS GITHUB SECRETS:")
    print("=" * 60)
    print(f"  BUFFER_ACCESS_TOKEN  →  {access_token}")
    print(f"  BUFFER_PROFILE_ID    →  {profile_id or 'see above'}")
    print("=" * 60)
    print("\n  Also add your Anthropic key:")
    print("  ANTHROPIC_API_KEY    →  (from console.anthropic.com)")
    print("=" * 60)


if __name__ == "__main__":
    main()
