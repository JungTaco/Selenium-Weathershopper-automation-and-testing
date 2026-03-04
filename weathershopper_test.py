import unittest
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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

chrome_options = Options()
chrome_options.add_argument("--headless")

def check_correct_title(self, driver, text):
    return text in driver.title

#Decides which page to navigate depending on temperature
def decide_product_type(driver, temperature, self):
    if temperature < 19:
        moisturizer_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Buy moisturizers')]")   
        moisturizer_btn.click()
        if check_correct_title(self, driver, "Moisturizers"):
            print("Successfully navigated to moisturizer page")
            return True
        else:
            print("Failure")
            return False
    elif temperature > 34:
        sunscreen_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Buy sunscreens')]")
        sunscreen_btn.click()
        if check_correct_title(self, driver, "Sunscreens"):
            print("Successfully navigated to sunscreen page")
            return True
        else:
            print("Failure")
            return False
    else:
        driver.quit()

def check_product_page(driver):
    if "Moisturizers" in driver.title:
        return "m"
    elif "Sunscreens" in driver.title:
        return "s"
    else:
        raise NameError('Not on products page')

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
def add_to_cart(driver, text, added_products, added_prices):
    prices = driver.find_elements(By.XPATH, "//*[contains(text(), 'Price:')]")
    add_btns = driver.find_elements(By.XPATH, "//*[contains(text(), 'Add')]")
    names = driver.find_elements(By.CLASS_NAME , "font-weight-bold")

    min_price = -1

    #finds all the prices
    for i, price in enumerate(prices):
        prices[i] = float(price.text.split(" ")[-1])
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
        added_products.append(names[min_price_pos].text)
        added_prices.append(float(prices[min_price_pos]))

def check_cart_empty(driver):
    if wait_for_element(driver, By.ID, "cart").text == "Empty":
        raise NameError('Cart is empty')

#verifies if products added to cart and their prices are the same as the ones shown in the cart page
def verify_cart(driver, added_products, added_prices, cart_products, cart_prices):
    for i, product in enumerate(cart_products):
        if product != added_products[i] or cart_prices[i] != added_prices[i]:
            raise NameError("Cart couldn't be verified")

def go_to_cart(driver):
    cart_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Cart')]")
    cart_btn.click()

def insert_payment_info(driver, EMAIL, ACCOUNT_NUMBER, CVC, CARD_EXP_MONTH, CARD_EXP_YEAR, BILLING_ZIP):
    pay_card_btn = wait_for_element(driver, By.XPATH, "//*[contains(text(), 'Pay with Card')]").click()

    iframe = wait_for_element(driver, By.CLASS_NAME, "stripe_checkout_app")
    driver.switch_to.frame(iframe)

    email_input = wait_for_element(driver, By.ID, "email")
    email_input.clear()
    email_input.send_keys(EMAIL)

    card_number_input = driver.find_element(By.ID, "card_number")
    card_number_input.clear()
    card_number_input.click()

    for n in ACCOUNT_NUMBER:
        card_number_input.send_keys(n)
        time.sleep(0.3)

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

#Gets all the products displayed in cart and their prices
def get_cart_info(driver, products, prices):
    information = wait_for_elements(driver, By.TAG_NAME, "td")
    for i, info in enumerate(information):
        if i%2 == 0:
            products.append(info.text)
        else:
            prices.append(float(info.text))

def pay(driver):
    pay_card_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Pay INR')]")
    pay_card_btn.click()

    try:
        wait_for_element(driver, By.XPATH, "//*[contains(text(), 'PAYMENT SUCCESS')]")
        return True
    except TimeoutException:
        return False

class WeatherShopperTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(options=chrome_options)

    #Tests navigation to moisturizers/sunscreens product pages
    def test_navigate_product_page(self):
        driver = self.driver
        driver.get("https://weathershopper.pythonanywhere.com/")
        temperature = int(wait_for_element(driver, By.ID, "temperature").text.split(" ")[0])
        result_flag = decide_product_type(driver, temperature, self)
        assert result_flag

    #Tests buying the cheapest products
    def test_buy_cheapest_product(self):
        driver = self.driver
        driver.get("https://weathershopper.pythonanywhere.com/")

        load_dotenv()
        EMAIL = os.getenv("EMAIL")
        ACCOUNT_NUMBER = os.getenv("ACCOUNT_NUMBER")
        CVC = int(os.getenv("CVC"))
        CARD_EXP_MONTH = int(os.getenv("CARD_EXP_MONTH"))
        CARD_EXP_YEAR = int(os.getenv("CARD_EXP_YEAR"))
        BILLING_ZIP = int(os.getenv("BILLING_ZIP"))
        
        #keeps track of products added to cart
        added_products = []
        #keeps track of prices of products added to cart
        added_prices = []
        #products that show in cart
        cart_products = []
        #prices of products that show in cart
        cart_prices = []

        temperature = int(wait_for_element(driver, By.ID, "temperature").text.split(" ")[0])
        decide_product_type(driver, temperature, self)
        
        chosen_page = check_product_page(driver)
        #Adds the cheapest products to the cart, depending on the page navigated to
        if chosen_page == "m":
            add_to_cart(driver, "aloe", added_products, added_prices)
            add_to_cart(driver, "almond", added_products, added_prices)
        else:
            add_to_cart(driver, "spf-50", added_products, added_prices)
            add_to_cart(driver, "spf-30", added_products, added_prices)

        check_cart_empty(driver)
        go_to_cart(driver)
        #Gets all the products purchased and their prices, in order verify cart
        get_cart_info(driver, cart_products, cart_prices)
        #verifies if products added to cart and their prices are the same as the ones shown in the cart page
        verify_cart(driver, added_products, added_prices, cart_products, cart_prices)
        insert_payment_info(driver, EMAIL, ACCOUNT_NUMBER, CVC, CARD_EXP_MONTH, CARD_EXP_YEAR, BILLING_ZIP)
        payment_success = pay(driver)
        assert payment_success

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()