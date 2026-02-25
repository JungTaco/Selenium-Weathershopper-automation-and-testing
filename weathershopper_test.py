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
    if temperature < 25:
        moisturizer_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Buy moisturizers')]")   
        moisturizer_btn.click()
        if check_correct_title(self, driver, "Moisturizers"):
            print("Successfully navigated to moisturizer page")
            return True
        else:
            print("Failure")
            return False
    else:
        sunscreen_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Buy sunscreens')]")
        sunscreen_btn.click()
        if check_correct_title(self, driver, "Sunscreens"):
            print("Successfully navigated to sunscreen page")
            return True
        else:
            print("Failure")
            return False

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

#Adds the cheapest product to the cart
def add_to_cart(driver):
    cart_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Cart')]")
    prices = driver.find_elements(By.XPATH, "//*[contains(text(), 'Price:')]")
    add_btns = driver.find_elements(By.XPATH, "//*[contains(text(), 'Add')]")

    #finds all the prices
    for i, price in enumerate(prices):
        prices[i] = int(price.text.split(" ")[-1])
    #finds the lowest price
    for i, price in enumerate(prices):
        if prices[i] == min(prices):
            min_price_pos = i
            break
    #clicks the "Add" button associated with the product with the lowest price to add it to the cart
    add_btns[min_price_pos].click()
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
        ACCOUNT_NUMBER_PART1 = int(os.getenv("ACCOUNT_NUMBER_PART1"))
        ACCOUNT_NUMBER_PART2 = int(os.getenv("ACCOUNT_NUMBER_PART2"))
        ACCOUNT_NUMBER_PART3 = int(os.getenv("ACCOUNT_NUMBER_PART3"))
        ACCOUNT_NUMBER_PART4 = int(os.getenv("ACCOUNT_NUMBER_PART4"))
        CVC = int(os.getenv("CVC"))
        CARD_EXP_MONTH = int(os.getenv("CARD_EXP_MONTH"))
        CARD_EXP_YEAR = int(os.getenv("CARD_EXP_YEAR"))
        BILLING_ZIP = int(os.getenv("BILLING_ZIP"))
        
        temperature = int(wait_for_element(driver, By.ID, "temperature").text.split(" ")[0])
        decide_product_type(driver, temperature, self)
        add_to_cart(driver)

        insert_payment_info(driver, EMAIL, ACCOUNT_NUMBER_PART1, ACCOUNT_NUMBER_PART2, ACCOUNT_NUMBER_PART3, ACCOUNT_NUMBER_PART4, CVC, CARD_EXP_MONTH, CARD_EXP_YEAR, BILLING_ZIP)
        payment_success = pay(driver)
        assert payment_success

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()