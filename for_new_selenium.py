import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager



with webdriver.Chrome() as driver:
    driver.get("https://flysmartavia.com/search/LED-2212-AER-1")
    time.sleep(5)