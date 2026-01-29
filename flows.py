import requests


def oauth_authorization_code_exchange(provider, code, client_id, client_secret, redirect_uri):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }

    response = requests.post(provider.config["token_url"], data=data)
    response.raise_for_status()
    return response.json()


import requests

def simplybook_get_user_token(company_login, user_login, password):
    payload = {
        "jsonrpc": "2.0",
        "method": "getUserToken",
        "params": [company_login, user_login, password],
        "id": 2
    }

    r = requests.post(
        "https://user-api.simplybook.me/login",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()

    # JSON-RPC error handling
    if "error" in data and data["error"] is not None:
        raise RuntimeError(f"SimplyBook error: {data['error']}")

    return data


def oauth_refresh_access_token(provider, refresh_token, client_id, client_secret):
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    r = requests.post(provider.config["token_url"], data=data)
    r.raise_for_status()
    return r.json()