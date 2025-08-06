import configparser
import json
import sys

from carriers.ups import UPSClient
from pathlib import Path

class UPSResponseWriter:
    def __init__(self):
        config = configparser.RawConfigParser()
        config.read("config.ini")
        ups_client_id = config.get("UPS", "client_id")
        ups_client_secret = config.get("UPS", "client_secret")
        ups_use_sandbox = config.getboolean("UPS", "use_sandbox")
        self.client = UPSClient(ups_client_id, ups_client_secret, ups_use_sandbox)

    def save_tracking_json(self, inquiry_number):
        data = self.client.ups_track(inquiry_number)

        folder = "testData/ups/"
        Path(folder).mkdir(parents=True, exist_ok=True)

        file_name = f"{folder}{inquiry_number}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Response written to {file_name}")

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(__file__).name} <inquiry_number>")
        sys.exit(1)

    inquiry_number = sys.argv[1]
    UPSResponseWriter().save_tracking_json(inquiry_number)

if __name__ == "__main__":
    main()