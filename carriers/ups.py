import time

import requests
from dateutil.parser import isoparse

from models.ups_token import UPSToken

class UPSClient:
    UPS_PRODUCTION_URL = "https://wwwcie.ups.com"
    UPS_SANDBOX_URL = "https://onlinetools.ups.com"
    def __init__(self, client_id: str, client_secret: str, use_sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.base_url = self.UPS_PRODUCTION_URL if use_sandbox else self.UPS_SANDBOX_URL

    def ups_generate_new_token(self):
        url = f"{self.base_url}/security/v1/oauth/token"
        payload = {
            "grant_type": "client_credentials"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-merchant-id": "string"
        }
        response = requests.post(url, data=payload, headers=headers, auth=(self.client_id, self.client_secret))
        response.raise_for_status()
        self.token = UPSToken(**response.json())
        return self.token

    def ups_get_token(self):
        current_time = time.time()

        if self.token:
            try:
                issued_at = isoparse(self.token.issued_at).timestamp()
                expires_in = int(self.token.expires_in)
                if current_time < issued_at + expires_in:
                    print(f"[Log] DEBUG: Using cached token (expires at {issued_at + expires_in})")
                    return self.token
            except Exception as e:
                print(f"[Log] DEBUG: Token check failed, regenerating token. Reason: {e}")

        return self.ups_generate_new_token()

    def ups_track(self, inquiry_number: str):
        access_token = self.ups_get_token().access_token
        url = f"{self.base_url}/api/track/v1/details/" + inquiry_number

        query = {
            "locale": "en_US",
            "returnSignature": "false"
        }

        headers = {
            "Content-Type": "application/json",
            "transId": "string",
            "transactionSrc": "testing",
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers, params=query)
        tracking_data = response.json()
        return tracking_data