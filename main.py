import asyncio
from playwright.async_api import async_playwright
import requests
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import Response
import threading

webhook_url = "https://discord.com/api/webhooks/1405412897470812180/fNXQTTLlTYYDnEC5YNfzjingsFhlKgp3sVAnzsGAApVinq5lro0-At-OK1h1uryvVdW2"

urls = [
    "https://reserve.tokyodisneyresort.jp/hotel/list/?showWay=&roomsNum=1&adultNum=2&childNum=1&stayingDays=1&useDate=20251211&cpListStr=&childAgeBedInform=01_3%7C&searchHotelCD=DHM&searchHotelDiv=&hotelName=&searchHotelName=&searchLayer=&searchRoomName=&hotelSearchDetail=true&checkPointStr=16&displayType=data-hotel&reservationStatus=1",
    "https://reserve.tokyodisneyresort.jp/hotel/list/?showWay=&roomsNum=1&adultNum=2&childNum=1&stayingDays=1&useDate=20251211&cpListStr=&childAgeBedInform=01_3%7C&searchHotelCD=DHM&searchHotelDiv=&hotelName=&searchHotelName=&searchLayer=&searchRoomName=&hotelSearchDetail=true&checkPointStr=18&displayType=data-hotel&reservationStatus=1"
]

notify_hours = [6, 12, 15, 18, 22]
notified_times = set()

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "running"}

@app.api_route("/", methods=["HEAD"])
async def handle_head():
    return Response(status_code=200)

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

        while True:
            now = datetime.now()
            current_hour = now.hour

            for url in urls:
                wait_time = 30
                max_wait_time = 10800
                total_waited = 0

                while total_waited < max_wait_time:
                    try:
                        context = await browser.new_context()
                        page = await context.new_page()

                        await page.goto(url, timeout=180000, wait_until="domcontentloaded")
                        await page.wait_for_timeout(5000)
                        content = await page.content()

                        await page.close()
                        await context.close()

                        if "ただいまサイトが混雑しております" in content:
                            print(f"混雑中。{wait_time}秒待機して再試行します。")
                            await asyncio.sleep(wait_time)
                            total_waited += wait_time
                            wait_time = min(wait_time * 2, 1800)
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

def start_checker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(check_rooms())

# Botをバックグラウンドで起動
threading.Thread(target=start_checker, daemon=True).start()
