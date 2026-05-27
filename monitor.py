import json
import os
import re
import requests
from playwright.sync_api import sync_playwright

URL = "https://www.google.com/travel/flights/booking?tfs=CBwQAhpMEgoyMDI2LTA3LTI5Ih4KA0hORBIKMjAyNi0wNy0yORoDSVNHKgJOSDICOTEoADICTkhAC0gLUABYF2oHCAESA0hORHIHCAESA0lTRxpMEgoyMDI2LTA4LTA0Ih4KA0lTRxIKMjAyNi0wOC0wNBoDSE5EKgJOSDICOTIoADICTkhAD0gPUABYF2oHCAESA0lTR3IHCAESA0hOREABQAFAAUADSAFwAYIBCwj___________8BmAEB&tfu=CmxDalJJVkdocWNVeHZiRlZ4WjJ0QlEzSnZRM2RDUnkwdExTMHRMUzB0TFMxMGJISXlNMEZCUVVGQlIyOVhjR1JyU1dGNWNXOUJFZ1JPU0RreUdnc0kvZjRORUFBYUEwcFFXVGdjY1BmakNBPT0SAggAIgA&hl=ja&gl=JP"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()
    page.goto(URL)
    page.wait_for_timeout(7000)

    print("URL:", page.url)
    print("TITLE:", page.title())

    # 価格を取得
    texts = page.locator("div").all_inner_texts()

    prices = []

    for t in texts:
        matches = re.findall(r"￥[\d,]+", t)

        for m in matches:
            prices.append(m)
    
    # 重複削除
    prices = list(dict.fromkeys(prices))

    print("PRICES:", prices)

    if not prices:
        raise RuntimeError("価格が取得できませんでした")

    total_price_text = prices[0]
    total_price = int(total_price_text.replace("￥", "").replace(",", ""))

    print("TOTAL PRICE:", total_price_text)

    state_path = "state.json"

    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {
            "best_price": None,
            "last_notified_price": None,
            "last_alert_price": None
        }
    
    best_price = state.get("best_price")
    last_notified_price = state.get("last_notified_price")
    last_alert_price = state.get("last_alert_price")

    threshold = 280000
    notify_message = None

    if total_price <= threshold and total_price != last_alert_price:
        notify_message = f"""@here
        🚨 Google Flightsで指定金額以下を検知しました
    
    旅程: 2026/07/29 - 2026/08/04
    便: ANA 往路11:40 / 復路15:30
    人数: 4名
    合計: {total_price_text}
    指定ライン: ￥280,000以下

    ANA公式でログイン確認してください。
    """
        state["last_alert_price"] = total_price
    
    elif best_price is None or total_price < best_price:
        notify_message = f"""🎉 Google Flightsで最安値を更新しました
    
    旅程: 2026/07/29 - 2026/08/04
    便: ANA 往路11:40 / 復路15:30
    人数: 4名
    合計: {total_price_text}
    前回最安値: {best_price if best_price else "なし"}

    ANA公式でログイン確認してください。
    """
        state["last_notified_price"] = total_price
    
    if best_price is None or total_price < best_price:
        state["best_price"] = total_price
    
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    if notify_message:
        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        if webhook_url:
            requests.post(webhook_url, json={"content": notify_message})
        else:
            print("DISCORD_WEBHOOK_URL が未設定です")
    else:
        print("通知条件に一致しません")

    page.screenshot(path="google_flights_booking.png", full_page=True)

    browser.close()