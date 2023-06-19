import requests

def ups_create_token(client_id, client_secret):
    url = "https://wwwcie.ups.com/security/v1/oauth/token"

    payload = {
        "grant_type": "client_credentials"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "x-merchant-id": "string"
    }

    response = requests.post(url, data=payload, headers=headers, auth=(client_id, client_secret))
    token = response.json()
    return token

def ups_track(inquiry_number, access_token):
    url = "https://wwwcie.ups.com/api/track/v1/details/" + inquiry_number

    query = {
        "locale": "en_US",
        "returnSignature": "false"
    }

    headers = {
        "Content-Type": "application/json",
        "transId": "string",
        "transactionSrc": "testing",
        "Authorization": "Bearer " + access_token
    }

    response = requests.get(url, headers=headers, params=query)

    tracking_data = response.json()
    return tracking_data