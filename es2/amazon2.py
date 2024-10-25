import telebot
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import threading

# Configurazione del logger
logging.basicConfig(level=logging.INFO)

API_TOKEN = '8013250687:AAE3WK6Gun1BEX9vbi5Pkeqz0U-TcybOcac'  # Inserisci il tuo token Telegram
bot = telebot.TeleBot(API_TOKEN)

# Percorso del driver di Chrome specifico
chrome_driver_path = r"C:\Users\pigro\OneDrive\Desktop\chromedriver-win64\chromedriver.exe"

# Funzione per avviare il driver di Selenium
def init_driver():
    service = Service(chrome_driver_path)
    options = Options()
    options.add_argument("--headless")  # Esegui il browser in modalità headless
    driver = Chrome(service=service, options=options)
    return driver

def search_amazon(product_name):
    driver = init_driver()
    driver.get("https://www.amazon.it")

    input_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[id='twotabsearchtextbox']"))
    )
    
    input_element.clear()
    input_element.send_keys(product_name)
    input_element.send_keys(Keys.RETURN)

    time.sleep(5)

    products = []

    try:
        titles = driver.find_elements(By.CSS_SELECTOR, "span.a-size-base-plus.a-color-base.a-text-normal")
        prices = driver.find_elements(By.CSS_SELECTOR, "span.a-price-whole")

        for i in range(min(len(titles), len(prices))):
            title = titles[i].text
            price = prices[i].text
            products.append({'title': title, 'price': price})

    except Exception as e:
        logging.error(f"Errore durante la ricerca su Amazon: {str(e)}")

    finally:
        driver.quit()

    return products

# Gestione dei comandi /start e /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Ciao! Inviami il nome di un prodotto da cercare su Amazon.")

# Gestione dei messaggi con testo
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    product_name = message.text
    bot.reply_to(message, f"Cerco '{product_name}' su Amazon, attendi...")

    # Esegui lo scraping su Amazon
    products = search_amazon(product_name)

    if products:
        for product in products:
            bot.send_message(message.chat.id, f"Prodotto: {product['title']}\nPrezzo: {product['price']} €")
    else:
        bot.send_message(message.chat.id, "Non ho trovato nessun prodotto corrispondente.")

# Funzione per eseguire il bot in un thread separato
def run_bot():
    bot.infinity_polling()

# Esegui il bot in un thread separato
threading.Thread(target=run_bot).start()
