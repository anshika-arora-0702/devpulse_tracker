import os
import requests

class SlackNotifier():

    def __init__(self):
        pass

    def send_slack_message(self, text:str) -> None:
        webhook_url = os.environ("SLACK_WEBHOOK_URL")

        if not webhook_url:
            raise ValueError("SLACK_WEBHOOK_URL is not configured")
        
        response = requests.post(
            webhook_url,
            json={"text": text},
            timeout=10,
        )
        response.raise_for_status()

        if response.text != "ok":
            raise RuntimeError(f"Unexpected Slack response: {response.text}")