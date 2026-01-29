from flask import Flask, request, redirect, jsonify, send_from_directory
from providers import GOOGLE, MICROSOFT, SIMPLYBOOK
from flows import oauth_authorization_code_exchange, oauth_refresh_access_token, simplybook_get_user_token
from token_store import TokenStore
import urllib.parse
import secrets
import os

SESSIONS = {}
OAUTH_STATE = {}
app = Flask(__name__)
store = TokenStore()

REDIRECT_URI = "https://servantlike-thermochemically-maison.ngrok-free.dev/callback"

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/icons/<path:filename>")
def icons(filename):
    return send_from_directory("static/icons", filename, mimetype="image/svg+xml")

@app.route("/auth/<provider>")
def auth(provider):
    if provider == "google":
        p = GOOGLE
    elif provider == "microsoft":
        p = MICROSOFT
    else:
        return "Unsupported provider", 400

    client_id = request.args["client_id"]
    client_secret = request.args["client_secret"]
    session_id = request.args.get("session_id")
    if not session_id:
        return "Missing session_id", 400

    SESSIONS.setdefault(session_id, {})
    SESSIONS[session_id][provider] = {
        "client_id": client_id,
        "client_secret": client_secret,
    }

    state = secrets.token_urlsafe(24)
    OAUTH_STATE[state] = {
        "provider": provider,
        "session_id": session_id,
    }

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": p.config["scope"],
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return redirect(p.config["auth_url"] + "?" + urllib.parse.urlencode(params))


@app.route("/callback")
def callback():
    try:
        code = request.args.get("code")
        state = request.args.get("state")
        if not code or not state:
            return jsonify({"error": "Missing code or state"}), 400

        ctx = OAUTH_STATE.pop(state, None)
        if not ctx:
            return jsonify({"error": "Unknown or expired state"}), 400

        provider = ctx["provider"]
        session_id = ctx["session_id"]

        creds = (SESSIONS.get(session_id, {}).get(provider) or {})
        client_id = creds.get("client_id")
        client_secret = creds.get("client_secret")
        if not client_id or not client_secret:
            return jsonify({"error": "Missing stored client credentials for session"}), 400

        p = GOOGLE if provider == "google" else MICROSOFT

        token = oauth_authorization_code_exchange(
            p, code, client_id, client_secret, REDIRECT_URI
        )

        store.save_oauth_token(provider, token)
        return jsonify(token)

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route("/simplybook/login", methods=["POST"])
def simplybook_login():
    try:
        data = request.json
        resp = simplybook_get_user_token(data["company_login"], data["user_login"], data["password"])
        store.save_simplybook_token(resp)
        return jsonify(resp)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/token/simplybook", methods=["GET"])
def simplybook_token():
    t = store.get_simplybook_token()
    if not t:
        return jsonify({"error": "No SimplyBook token stored yet. Login first."}), 400
    return jsonify({"token": t, "source": "cache"})

@app.route("/token/<provider>", methods=["GET"])
def token(provider):
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400
    if provider not in ("google", "microsoft"):
        return jsonify({"error": "Unsupported provider"}), 400

    if store.has_valid_access_token(provider):
        return jsonify({"access_token": store.get_access_token(provider), "source": "cache"})

    refresh_token = store.get_refresh_token(provider)
    if not refresh_token:
        return jsonify({"error": "No refresh_token stored. Do one interactive login first."}), 400

    creds = (SESSIONS.get(session_id, {}).get(provider) or {})
    client_id = creds.get("client_id")
    client_secret = creds.get("client_secret")
    if not client_id or not client_secret:
        return jsonify({"error": "Missing stored client credentials for session"}), 400

    p = GOOGLE if provider == "google" else MICROSOFT
    new_token = oauth_refresh_access_token(p, refresh_token, client_id, client_secret)
    store.save_oauth_token(provider, new_token)

    return jsonify({"access_token": store.get_access_token(provider), "source": "refresh"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

