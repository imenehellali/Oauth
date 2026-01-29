import json
import os
import time
from typing import Any, Dict, Optional


class TokenStore:
    def __init__(self, path: str = "token_store.json"):
        self.path = path

    def _read_all(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {}
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data: Dict[str, Any]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_oauth_token(self, provider: str, token_json: Dict[str, Any]) -> None:
        data = self._read_all()
        entry = data.get(provider, {})

        access_token = token_json.get("access_token")
        expires_in = token_json.get("expires_in")
        refresh_token = token_json.get("refresh_token")

        if access_token:
            entry["access_token"] = access_token

        if expires_in is not None:
            entry["expires_at"] = int(time.time()) + int(expires_in) - 30  # 30s safety

        if refresh_token:
            entry["refresh_token"] = refresh_token

        data[provider] = entry
        self._write_all(data)

    def get_oauth_entry(self, provider: str) -> Optional[Dict[str, Any]]:
        data = self._read_all()
        return data.get(provider)

    def has_valid_access_token(self, provider: str) -> bool:
        entry = self.get_oauth_entry(provider) or {}
        token = entry.get("access_token")
        expires_at = entry.get("expires_at", 0)
        return bool(token) and int(time.time()) < int(expires_at)

    def get_access_token(self, provider: str) -> Optional[str]:
        entry = self.get_oauth_entry(provider) or {}
        return entry.get("access_token")

    def get_refresh_token(self, provider: str) -> Optional[str]:
        entry = self.get_oauth_entry(provider) or {}
        return entry.get("refresh_token")
    
    def save_simplybook_token(self, resp_json):
        data = self._read_all()
        data["simplybook"] = resp_json
        self._write_all(data)
    
    def get_simplybook_token(self):
        entry = self._read_all().get("simplybook")
        if not entry:
            return None
        return entry.get("result")
    
