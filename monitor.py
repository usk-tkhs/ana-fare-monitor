import os
import requests

webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

message = {
    "content": "✅ ANA Fare Monitor テスト通知"
}

r = requests.post(webhook_url, json=message)

print(r.status_code)
print(r.text)