class Provider:
    def __init__(self, name, auth_type, config):
        self.name = name
        self.auth_type = auth_type
        self.config = config


GOOGLE = Provider(
    name="google",
    auth_type="oauth_authorization_code",
    config={
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scope": "https://www.googleapis.com/auth/spreadsheets.readonly",
    },
)

MICROSOFT = Provider(
    name="microsoft",
    auth_type="oauth_authorization_code",
    config={
        "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "scope": "https://graph.microsoft.com/User.Read",
    },
)

SIMPLYBOOK = Provider(
    name="simplybook",
    auth_type="credential_login",
    config={
        "token_url": "https://user-api.simplybook.me/login",
    },
)
