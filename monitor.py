from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto("https://www.ana.co.jp/")

    page.screenshot(path="ana_top.png", full_page=True)

    with open("ana_top.html", "w", encoding="utf-8") as f:
        f.write(page.content())

    browser.close()

print("saved")