import time

from bs4 import BeautifulSoup
from selenium import webdriver
# Импортируем классы для Chrome. Если у вас другой браузер - измените импорт.
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from airports_airlines import *

BASE_URL = ('https://flysmartavia.com/search/'
            # 'LED-1001-AER-1'
            )


def get_url_smartavia(date, dep_air, arr_air):
    departure = AIRPORT_CODES[dep_air]
    arrive = AIRPORT_CODES[arr_air]
    url_smartavia = BASE_URL + departure + '-' + date + '-' + arrive + '-' + '1'
    return url_smartavia


def get_driver(date, dep_air, arr_air):
    service = Service(executable_path=ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(get_url_smartavia(date, dep_air, arr_air))
    time.sleep(1)
    return driver


def get_soup(driver):
    soup = BeautifulSoup(driver.page_source, features='lxml')
    time.sleep(2)
    driver.quit()
    return soup


def get_5_days_flights(driver_chrome, soup_beauty, flights):
    h_wrapper = driver_chrome.find_element(By.CLASS_NAME, 'calendar-h-wrapper')
    link = h_wrapper.find_elements(By.CLASS_NAME, 'day-wrapper')
    price = soup_beauty.find_all('span', {'class': 'day-label'})
    day = soup_beauty.find_all('span', {'class': 'day'})
    for i in range(len(link)):
        flights += f'{day[i].text} - {price[i].text.lstrip("от ")}\n'
    flights += f'\n{link[2].get_attribute("href")}'
    return flights


def get_one_day_flight(driver_chrome):
    row = driver_chrome.find_element(By.CLASS_NAME, 'row')
    date_time = row.find_element(By.CLASS_NAME, 'inner')
    price = row.find_element(By.CLASS_NAME, 'button-wrapper')

    print(date_time.text)
    print(price.text.lstrip('от'))


if __name__ == '__main__':
    print(get_5_days_flights(get_driver('2807', 'СПБ', 'Сочи'),
                             get_soup(get_driver('2807', 'СПБ', 'Сочи')),
                             'spb'))
    # get_one_day_flight(driver)
    # time.sleep(4)
    # driver.quit()
