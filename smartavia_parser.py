import logging
import time
import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from airports_airlines import AIRPORT_CODES

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(f"{__name__}.log", mode='a')
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

SMARTAVIA_URL = ('https://flysmartavia.com/search/'
                 # 'LED-1001-AER-1'
                 )

AEROFLOT_URL = (
    'https://www.aeroflot.ru/sb/app/ru-ru?utm_referrer=https%3A%2F%2F'
    'www.aeroflot.ru%2Fru-ru#/search?adults=1&cabin=economy&children=0&'
    'infants=0&routes='
    # 'LED.20241228.AER'
)


def get_url(url, date, dep_air, arr_air) -> str:
    departure = AIRPORT_CODES[dep_air]
    arrival = AIRPORT_CODES[arr_air]
    if url == AEROFLOT_URL:
        url = (url + departure + '.' + date + '.' + arrival)
    elif url == SMARTAVIA_URL:
        url = (url + departure + '-' + date + '-' + arrival + '-' + '1')
    return url


def get_web_driver(url, date, dep_air, arr_air):
    service = Service(executable_path=ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(get_url(url, date, dep_air, arr_air))
    time.sleep(8)
    return driver


def seven_days_aeroflot(url, current_date, dep_air, arr_air):
    driver = get_web_driver(url, current_date, dep_air, arr_air)
    if not driver.title:
        return 'Аэрофлот пока недоступен, попробуйте ещё один раз.'
    find_button = driver.find_element(
        By.XPATH, '//*[@id="frame-0.4608685637358576"]/div/div/div[2]/div[3]/a'
    )
    time.sleep(2)
    find_button.click()
    time.sleep(3)
    seven_days = driver.find_element(
        'xpath',
        # '//*[@id="frame-0.8446740044746548"]/div[2]/div[1]' # ЛУЧШАЯ ЦЕНА
        # '//*[@id="frame-0.8446740044746548"]/div[2]' # все рейсы на дату
        '//*[@id="chart-week-0"]'  # 7 дней
    )
    with open('aeroflot.txt', 'w+') as file:
        file.write(seven_days.text)
    return seven_days.text


def one_day_aeroflot(url, current_date, dep_air, arr_air):
    driver = get_web_driver(url, current_date, dep_air, arr_air)
    if not driver.title:
        return 'Аэрофлот пока недоступен, попробуйте ещё один раз.'
    find_button = driver.find_element(
        By.XPATH, '//*[@id="frame-0.4608685637358576"]/div/div/div[2]/div[3]/a'
    )
    time.sleep(2)
    find_button.click()
    time.sleep(3)
    better_price = driver.find_element(
        'xpath',
        '//*[@id="frame-0.8446740044746548"]/div[2]/div[1]'  # ЛУЧШАЯ ЦЕНА
        # '//*[@id="frame-0.8446740044746548"]/div[2]' # все рейсы на дату
        # '//*[@id="chart-week-0"]'  # 7 дней
    )
    if better_price.text.__class__ is not str or better_price.text is False:
        return "xpath has not worked"
    with open('aeroflot.txt', 'a') as file:
        file.write(datetime.datetime.now().isoformat())
        file.write('\n')
        file.write(better_price.text)
        file.write('\n')

    result = better_price.text
    list_result = result.split('\n')
    # print(list_result) #  for debugging
    if 'Разные дни вылета и прилета' in list_result:
        list_result.remove('Разные дни вылета и прилета')
    if '+1' in list_result:
        list_result.remove('+1')
    finish_dict = dict()
    finish_str = ''
    element_to_remove = list_result.pop(10)
    list_result[9] = list_result[9] + ':' + element_to_remove
    for number in range(6):
        finish_str += list_result[number]
        finish_str += ' '
        finish_str += list_result[number + 6]
        finish_str += '\n'
        finish_dict[list_result[number]] = list_result[number + 6]
    return finish_str


def five_days_smartavia(url, date, dep_air, arrive_air, flights: str) -> str:
    driver = get_web_driver(url, date, dep_air, arrive_air)
    soup = BeautifulSoup(driver.page_source, features="lxml")
    time.sleep(1)
    h_wrapper = driver.find_element(By.CLASS_NAME,
                                    'calendar-h-wrapper')
    link = h_wrapper.find_elements(By.CLASS_NAME, 'day-wrapper')
    price = soup.find_all('span', {'class': 'day-label'})
    # driver.quit()
    day = soup.find_all('span', {'class': 'day'})
    for i in range(len(link)):
        flights += f'{day[i].text} - {price[i].text.lstrip("от ")}\n'
    result = flights + f'\n{link[2].get_attribute("href")}'
    with open('aeroflot.txt', 'a') as file:
        file.write(datetime.datetime.now().isoformat())
        file.write('\n')
        file.write(flights)
        file.write('\n')
    return result


if __name__ == '__main__':  # for debugging
    # print(
    #     get_web_driver(
    #         SMARTAVIA_URL, '2012', 'СПБ', 'Сочи'
    #     )
    # )
    print(one_day_aeroflot(AEROFLOT_URL, '20241229', 'Москва', 'Сочи'))
