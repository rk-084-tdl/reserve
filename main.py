import asyncio
from playwright.async_api import async_playwright
import requests
from datetime import datetime

# Discord Webhook URL（RyoさんのURLを使用）
webhook_url = "https://discord.com/api/webhooks/1405412897470812180/fNXQTTLlTYYDnEC5YNfzjingsFhlKgp3sVAnzsGAApVinq5lro0-At-OK1h1uryvVdW2"

# チェック対象のURL（必要に応じて追加・変更可能）
urls = [
    "https://reserve.tokyodisneyresort.jp/hotel/list/?roomsNum=1&adultNum=2&childNum=1&stayingDays=1&useDate=20251211&searchHotelCD=DHM&checkPointStr=16&reservationStatus=1",
    "https://reserve.tokyodisneyresort.jp/hotel/list/?roomsNum=1&adultNum=2&childNum=1&stayingDays=1&useDate=20251211&searchHotelCD=DHM&checkPointStr=18&reservationStatus=1"
]

# 通知時間（空室なしでも通知する時間帯）
notify_hours = [7, 13, 18]
notified_times = set()

# Discord通知関数
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

# 空室チェック関数（混雑検出＋最大3時間待機）
async def check_rooms():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        while True:
            now = datetime.now()
            current_hour = now.hour

            for url in urls:
                wait_time = 30  # 初回待機時間（秒）
                max_wait_time = 10800  # 最大待機時間（3時間）
                total_waited = 0

                while total_waited < max_wait_time:
                    try:
                        await page.goto(url)
                        await page.wait_for_timeout(5000)
                        content = await page.content()

                        if "ただいまサイトが混雑しております" in content:
                            print(f"混雑中。{wait_time}秒待機して再試行します。")
                            await asyncio.sleep(wait_time)
                            total_waited += wait_time
                            wait_time = min(wait_time * 2, 1800)  # 最大30分まで増加
                            continue

                        if "空室がありません" not in content:
                            send_discord_message(webhook_url, f"🎉 空室あり！予約ページはこちら：{url}")
                            await browser.close()
                            return
                        break
                    except Exception as e:
                        print(f"Error checking URL {url}: {e}")
                        break

            if current_hour in notify_hours and current_hour not in notified_times:
                send_discord_message(webhook_url, f"⏰ {current_hour}時現在、空室はありませんでした。")
                notified_times.add(current_hour)

            await asyncio.sleep(10)

# 実行
if __name__ == "__main__":
    asyncio.run(check_rooms())
