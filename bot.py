import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from datetime import datetime

# ====== НАСТРОЙКИ ======
TELEGRAM_TOKEN = "8103249776:AAHVdzbM6ZZNjw7LL7s0yFuC_z-MCFRrRLM"
CHAT_ID        = "256270526"
PARKING_ID     = "80"

URL = "https://parking.mos.ru/parking/barrier/subscribe/"

def check_parking(page, radio_id, month_name):
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)

    page.evaluate(f"""
        let el = document.getElementById('{radio_id}');
        if (el) el.click();
    """)
    page.wait_for_timeout(2000)

    page.evaluate("""
        let item = document.querySelector('div[data-value="0500"]');
        if (item) item.click();
    """)
    page.wait_for_timeout(5000)

    content = page.content()
    soup = BeautifulSoup(content, "html.parser")
    item = soup.find("div", attrs={"data-value": PARKING_ID})
    if item is None:
        raise ValueError(f"Парковка {PARKING_ID} не найдена ({month_name})")
    return "disabledVar" not in item.get("class", [])

def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"},
        timeout=10
    )

def main():
    today = datetime.now().day
    check_current = today <= 10  # текущий месяц только с 1 по 10

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Всегда проверяем следующий месяц
        next_month = check_parking(page, "parking-barries-checkbox2", "следующий месяц")

        # Текущий месяц только с 1 по 10
        curr_month = False
        if check_current:
            curr_month = check_parking(page, "parking-barries-checkbox1", "текущий месяц")

        browser.close()

    print(f"Следующий: {'✅' if next_month else '❌'} | "
          f"Текущий: {'✅' if curr_month else '❌' if check_current else '⏭ не проверяем'}")

    if next_month:
        send_telegram(
            "🚗 <b>Место появилось на СЛЕДУЮЩИЙ месяц!</b>\n"
            "📍 г. Москва, ул. Донецкая, влд. 34\n"
            "👉 https://parking.mos.ru/parking/barrier/subscribe/"
        )
    if curr_month:
        send_telegram(
            "🚗 <b>Место появилось на ТЕКУЩИЙ месяц!</b>\n"
            "📍 г. Москва, ул. Донецкая, влд. 34\n"
            "👉 https://parking.mos.ru/parking/barrier/subscribe/"
        )

if __name__ == "__main__":
    main()