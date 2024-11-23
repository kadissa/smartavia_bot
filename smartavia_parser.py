import logging
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from airports_airlines import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(f"{__name__}.log", mode='a')
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

BASE_URL = ('https://flysmartavia.com/search/'
            # 'LED-1001-AER-1'
            )


def get_url_smartavia(date, dep_air, arr_air):
    departure = AIRPORT_CODES[dep_air]
    arrival = AIRPORT_CODES[arr_air]
    url_smartavia = (BASE_URL + departure + '-' + date + '-' + arrival + '-'
                     + '1')
    logger.info(f'url_smartavia={url_smartavia}')
    return url_smartavia


def get_driver(date, dep_air, arr_air):
    service = Service(executable_path=ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(get_url_smartavia(date, dep_air, arr_air))
    time.sleep(4)
    if '403' in driver.title:
        return '403', 'forbidden'
    soup = BeautifulSoup(driver.page_source, features="lxml")
    time.sleep(1)
    logger.warning(f'driver={str(driver)}')
    logger.warning(f'soup={soup.get_text()[:30]}')
    return driver, soup


def get_5_days_flights(driver_chrome, soup_beauty, flights: str) -> str:
    current_web_page = driver_chrome
    if '403' in current_web_page:
        return 'Смарт-авиа закрыла доступ через Selenium'
    h_wrapper = current_web_page.find_element(By.CLASS_NAME, 'calendar-h-wrapper')
    link = h_wrapper.find_elements(By.CLASS_NAME, 'day-wrapper')
    price = soup_beauty.find_all('span', {'class': 'day-label'})
    day = soup_beauty.find_all('span', {'class': 'day'})
    for i in range(len(link)):
        flights += f'{day[i].text} - {price[i].text.lstrip("от ")}\n'
    flights += f'\n{link[2].get_attribute("href")}'
    return flights


if __name__ == '__main__':  # for debugging
    print(
        get_5_days_flights(
            get_driver('2412', 'СПБ', 'Сочи')[0],
            get_driver('2412', 'СПБ', 'Сочи')[1],
            'spb'
        ),
    )
