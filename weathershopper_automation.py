import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv    

chrome_options = Options()
#chrome_options.add_argument("--headless")

#Decides which page to navigate depending on temperature
def decide_product_type(driver, temperature):
    if temperature < 19:
        moisturizer_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Buy moisturizers')]")   
        moisturizer_btn.click()
        return "m"
    elif temperature > 34:
        sunscreen_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Buy sunscreens')]")
        sunscreen_btn.click()
        return "s"
    else:
        driver.quit()
    print(page)

def wait_for_element(driver, by, element_identifier, timeout=5):
    try:
        element_present = EC.presence_of_element_located((by, element_identifier))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        logging.info(f"Timed out wating for {element_identifier}")
        return None
    return driver.find_element(by, element_identifier)

def wait_for_elements(driver, by, element_identifier, timeout=5):
    try:
        element_present = EC.presence_of_element_located((by, element_identifier))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        logging.info(f"Timed out wating for {element_identifier}")
        return None
    return driver.find_elements(by, element_identifier)

#Adds the cheapest product containing the specified text to cart
def add_to_cart(driver, text):
    prices = driver.find_elements(By.XPATH, "//*[contains(text(), 'Price:')]")
    add_btns = driver.find_elements(By.XPATH, "//*[contains(text(), 'Add')]")
    names = driver.find_elements(By.CLASS_NAME , "font-weight-bold")

    min_price = -1

    #finds all the prices
    for i, price in enumerate(prices):
        prices[i] = int(price.text.split(" ")[-1])
    #finds the lowest price
    for i, price in enumerate(prices):
        if text in names[i].text.lower():
            if min_price > -1:
                if prices[i] < min_price:
                    min_price = prices[i]
                    min_price_pos = i
            else:
                min_price = prices[i]
                min_price_pos = i

    if min_price > -1:
        #clicks the "Add" button associated with the product with the lowest price to add it to the cart
        add_btns[min_price_pos].click()

def check_cart_empty(driver):
    if wait_for_element(driver, By.ID, "cart").text == "Empty":
        time.sleep(10)
        print("Cart is empty)")
        driver.quit()

def go_to_cart(driver):
    cart_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Cart')]")
    cart_btn.click()

def insert_payment_info(driver, EMAIL, ACCOUNT_NUMBER_PART1, ACCOUNT_NUMBER_PART2, ACCOUNT_NUMBER_PART3, ACCOUNT_NUMBER_PART4, CVC, CARD_EXP_MONTH, CARD_EXP_YEAR, BILLING_ZIP):
    pay_card_btn = wait_for_element(driver, By.XPATH, "//*[contains(text(), 'Pay with Card')]").click()

    iframe = wait_for_element(driver, By.CLASS_NAME, "stripe_checkout_app")
    driver.switch_to.frame(iframe)

    email_input = wait_for_element(driver, By.ID, "email")
    email_input.clear()
    email_input.send_keys(EMAIL)

    card_number_input = driver.find_element(By.ID, "card_number")
    card_number_input.clear()
    card_number_input.send_keys(ACCOUNT_NUMBER_PART1)
    card_number_input.send_keys(ACCOUNT_NUMBER_PART2)
    card_number_input.send_keys(ACCOUNT_NUMBER_PART3)
    card_number_input.send_keys(ACCOUNT_NUMBER_PART4)

    cc_exp_input = driver.find_element(By.ID, "cc-exp")
    cc_exp_input.clear()
    cc_exp_input.click()
    cc_exp_input.send_keys(CARD_EXP_MONTH)
    cc_exp_input.click()
    cc_exp_input.send_keys(CARD_EXP_YEAR)

    cvc_input = driver.find_element(By.ID, "cc-csc")
    cvc_input.clear()
    cvc_input.send_keys(CVC)

    zip_input =  wait_for_element(driver, By.ID, "billing-zip", 50)
    zip_input.clear()
    zip_input.send_keys(BILLING_ZIP)

def pay(driver):
    pay_card_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Pay INR')]")
    pay_card_btn.click()

    try:
        wait_for_element(driver, By.XPATH, "//*[contains(text(), 'PAYMENT SUCCESS')]")
        return True
    except TimeoutException:
        return False

#Sends email containing information about the purchase
def send_message(subject, receiver, message):
    sender = "denisaculincu96@gmail.com"

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.set_content(message)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, "tfct jmop actj cqjb")
        smtp.send_message(msg)

#Gets all the products purchased and their prices
def get_cart_info(driver, products, prices):
    information = wait_for_elements(driver, By.TAG_NAME, "td")
    for i, info in enumerate(information):
        if i%2 == 0:
            products.append(info.text)
        else:
            prices.append(float(info.text))

def get_total(driver):
    return float(wait_for_element(driver, By.ID, "total").text.split(" ")[-1])

def main():
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://weathershopper.pythonanywhere.com/")

    load_dotenv()
    EMAIL = os.getenv("EMAIL")
    ACCOUNT_NUMBER_PART1 = int(os.getenv("ACCOUNT_NUMBER_PART1"))
    ACCOUNT_NUMBER_PART2 = int(os.getenv("ACCOUNT_NUMBER_PART2"))
    ACCOUNT_NUMBER_PART3 = int(os.getenv("ACCOUNT_NUMBER_PART3"))
    ACCOUNT_NUMBER_PART4 = int(os.getenv("ACCOUNT_NUMBER_PART4"))
    CVC = int(os.getenv("CVC"))
    CARD_EXP_MONTH = int(os.getenv("CARD_EXP_MONTH"))
    CARD_EXP_YEAR = int(os.getenv("CARD_EXP_YEAR"))
    BILLING_ZIP = int(os.getenv("BILLING_ZIP"))

    cart_products = []
    cart_prices = []
    
    temperature = int(wait_for_element(driver, By.ID, "temperature").text.split(" ")[0])
    #Decides which page to navigate depending on temperature
    chosen_page = decide_product_type(driver, temperature)
    #Adds the cheapest products to the cart
    if chosen_page == "m":
        add_to_cart(driver, "aloe")
        add_to_cart(driver, "almond")
    else:
        add_to_cart(driver, "spf-50")
        add_to_cart(driver, "spf-30")
    check_cart_empty(driver)
    go_to_cart(driver)

    #Gets all the products purchased and their prices, in order to send an information email
    get_cart_info(driver, cart_products, cart_prices)

    total = get_total(driver)

    insert_payment_info(driver, EMAIL, ACCOUNT_NUMBER_PART1, ACCOUNT_NUMBER_PART2, ACCOUNT_NUMBER_PART3, ACCOUNT_NUMBER_PART4, CVC, CARD_EXP_MONTH, CARD_EXP_YEAR, BILLING_ZIP)
    payment_success = pay(driver)

    success_msg = "You have purchased the following: "
    for i, product in enumerate(cart_products):
        success_msg = success_msg + product + " (" + str(cart_prices[i]) + " Rupees)"
        if i != len(cart_products) - 1:
            success_msg = success_msg + ", "
    success_msg = success_msg + ". \nThe total of your purchase is " + str(total) + " Rupees."

    failure_msg = "Your purchase has failed."
    
    if payment_success:
        send_message("Payment successful", "denisaculincu96@gmail.com", success_msg)
    else:
        send_message("Payment failed", "denisaculincu96@gmail.com", failure_msg)

    driver.quit()

if __name__ == "__main__":
    main()