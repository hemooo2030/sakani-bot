import os
import time
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- تحميل متغيرات البيئة
national_id = os.getenv("national_id")
password = os.getenv("password")
telegram_token = os.getenv("telegram_token")
chat_id = os.getenv("chat_id")

# --- إعداد المتصفح
options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 15)

# --- إرسال رسالة تيليجرام
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        requests.post(url, data=data)
    except Exception as e:
        print("فشل إرسال رسالة تيليجرام:", e)

# --- تسجيل الدخول
def login():
    try:
        driver.get("https://sakani.sa/")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),  تسجيل الدخول )]"))).click()

        wait.until(EC.presence_of_element_located((By.NAME, "id"))).send_keys(national_id)
        driver.find_element(By.NAME, "password").send_keys(password + Keys.ENTER)

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("تم تسجيل الدخول بنجاح.")
    except Exception as e:
        print("خطأ في تسجيل الدخول:", e)
        send_telegram("فشل تسجيل الدخول إلى سكني.")
        driver.quit()
        exit()

# --- مراقبة وحجز
def monitor():
    driver.get("https://sakani.sa/app/land-projects/674")
    time.sleep(6)
    while True:
        try:
            driver.refresh()
            print("[تحقق] جارٍ التحقق من توفر الأراضي...")
            time.sleep(5)
            buttons = driver.find_elements(By.XPATH, "//button[contains(text(),  احجز الآن )]")
            if buttons:
                buttons[0].click()
                send_telegram("أرض متاحة الآن! تم الضغط على زر الحجز.")
                print("تم الحجز مبدئيًا!")
                break
            else:
                print("[تحقق] لا توجد أراضي حالياً. إعادة المحاولة بعد 30 ثانية.")
                time.sleep(30)
        except Exception as e:
            print("حدث خطأ أثناء المراقبة:", e)
            send_telegram("حدث خطأ أثناء التحقق من توفر الأراضي.")
            time.sleep(30)

# --- تشغيل البوت
login()
monitor()
driver.quit()