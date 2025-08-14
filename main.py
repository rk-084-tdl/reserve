import asyncio
from playwright.async_api import async_playwright
import requests

# Discord通知関数
def send_discord_message(webhook_url, message):
    data = {"content": message}
    requests.post(webhook_url, json=data)

# チェック対象のURL（2つ）
urls = [
    "https://reserve.tokyodisneyresort.jp/hotel/list/?roomsNum=1&adultNum=2&childNum=1&stayingDays=1&useDate=20251211&searchHotelCD=DHM&checkPointStr=16&reservationStatus=1",
    "https://reserve.tokyodisneyresort.jp/hotel/list/?roomsNum=1&adultNum=2&childNum=1&stayingDays=1&useDate=20251211&searchHotelCD=DHM&checkPointStr=18&reservationStatus=1"
]

webhook_url = "https://discord.com/api/webhooks/1405412897470812180/fNXQTTLlTYYDnEC5YNfzjingsFhlKgp3sVAnzsGAApVinq5lro0-At-OK1h1uryvVdW2"

async def check_rooms():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for url in urls:
            await page.goto(url)
            await page.wait_for_timeout(5000)  # ページ読み込み待ち
            content = await page.content()
            if "空室がありません" not in content:
                send_discord_message(webhook_url, f"🎉 空室あり！予約ページはこちら：{url}")
                break
        await browser.close()

asyncio.run(check_rooms())
