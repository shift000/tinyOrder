import os

class Config:
    CLIENT_ID = os.getenv("CLIENT_ID", "b7a923cd-e2b2-44ac-94aa-266bd3aa8e5a")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "5f32fdc2-cf22-45ac-9a3c-5c42ec45a2be")
    AUTHORITY = f"https://login.microsoftonline.com/{os.getenv('TENANT_ID', '5dde3815-af63-49d5-b149-e545b73512fd')}"
    REDIRECT_PATH = "/auth/callback"
    SCOPE = ["User.Read"]
    SESSION_TYPE = "filesystem"  # Zum Speichern der Sitzung

secret_key = 'supergeheimeschluessel'
config_secret_key = 'supergeheimeschluessel'
login_by_sso = True

