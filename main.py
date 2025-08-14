from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import requests
import time

# Discord通知関数
def send_discord_message(webhook_url, message):
    data = {"content": message}
    requests.post(webhook_url, json=data)

# Selenium設定
service = Service('./chromedriver')  # ChromeDriverのパス
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 画面非表示
driver = webdriver.Chrome(service=service, options=options)

# チェック対象のURL（2つ）
urls = [
    "https://reserve.tokyodisneyresort.jp/hotel/list/?roomsNum=1&adultNum=2&childNum=1&stayingDays=1&useDate=20251211&searchHotelCD=DHM&checkPointStr=16&reservationStatus=1",
    "https://reserve.tokyodisneyresort.jp/hotel/list/?roomsNum=1&adultNum=2&childNum=1&stayingDays=1&useDate=20251211&searchHotelCD=DHM&checkPointStr=18&reservationStatus=1"
]

webhook_url = "https://discord.com/api/webhooks/1405412897470812180/fNXQTTLlTYYDnEC5YNfzjingsFhlKgp3sVAnzsGAApVinq5lro0-At-OK1h1uryvVdW2"

# 空室チェック
for url in urls:
    driver.get(url)
    time.sleep(5)  # ページ読み込み待ち
    if "空室がありません" not in driver.page_source:
        send_discord_message(webhook_url, f"🎉 空室あり！予約ページはこちら：{url}")
        break  # 最初に空いていたページだけ通知
else:
    print("空室なし")

driver.quit()
