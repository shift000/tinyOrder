import os

class Config:
    CLIENT_ID = os.getenv("CLIENT_ID", "<REDACTED>")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "<REDACTED>")
    AUTHORITY = f"https://login.microsoftonline.com/{os.getenv('TENANT_ID', '<REDACTED>')}"
    REDIRECT_PATH = "/auth/callback"
    SCOPE = ["User.Read"]
    SESSION_TYPE = "filesystem"  # Zum Speichern der Sitzung

secret_key = 'supergeheimeschluessel'
config_secret_key = 'supergeheimeschluessel'
login_by_sso = True

