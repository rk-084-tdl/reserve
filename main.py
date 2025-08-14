import asyncio
from playwright.async_api import async_playwright
import requests
import time
from datetime import datetime

webhook_url = "https://discord.com/api/webhooks/1405412897470812180/fNXQTTLlTYYDnEC5YNfzjingsFhlKgp3sVAnzsGAApVinq5lro0-At-OK1h1uryvVdW2"

urls = [
    "https://reserve.tokyodisneyresort.jp/hotel/list/?roomsNum=1&adultNum=2&childNum=1&stayingDays=1&useDate=20251211&searchHotelCD=DHM&checkPointStr=16&reservationStatus=1",
    "https://reserve.tokyodisneyresort.jp/hotel/list/?roomsNum=1&adultNum=2&childNum=1&stayingDays=1&useDate=20251211&searchHotelCD=DHM&checkPointStr=18&reservationStatus=1"
]

notify_hours = [7, 13, 18]
notified_times = set()

def send_discord_message(webhook_url, message):
    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print(f"Sent message: {message}")
        else:
            print(f"Failed to send message: {response.status_code}")
    except Exception as e:
        print(f"Error sending message: {e}")

async def check_rooms():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        while True:
            now = datetime.now()
            current_hour = now.hour

            for url in urls:
                try:
                    await page.goto(url)
                    await page.wait_for_timeout(5000)
                    content = await page.content()
                    if "空室がありません" not in content:
                        send_discord_message(webhook_url, f"🎉 空室あり！予約ページはこちら：{url}")
                        await browser.close()
                        return
                except Exception as e:
                    print(f"Error checking URL {url}: {e}")

            if current_hour in notify_hours and current_hour not in notified_times:
                send_discord_message(webhook_url, f"⏰ {current_hour}時現在、空室はありませんでした。")
                notified_times.add(current_hour)

            time.sleep(10)

# 実行
if __name__ == "__main__":
    asyncio.run(check_rooms())
