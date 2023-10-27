# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 05:26:57 2023

@author: rs
"""

# Version  РјРµРЅСЏРµРј N РЅР° Р»СЋР±РѕРµ РєРѕР»-РІРѕ РєР°СЂС‚РѕС‡РµРє
import csv
import os
import re
import ssl
import time
from datetime import datetime
import urllib.request
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import json
import shutil


product_info_list = []

path = 'C:/Users/12/Downloads/ali/'
chrome_options = Options()


def custom_wait(xpath):
    def inner(driver):
        condition1 = EC.visibility_of_element_located((By.XPATH, xpath))(driver)
        condition2 = EC.element_to_be_clickable((By.XPATH, xpath))(driver)
        condition3 = EC.presence_of_element_located((By.XPATH, xpath))(driver)
        return condition1 and condition2 and condition3
    return inner

def extract_text_after_keyword(text, keyword):
    try:
        start_pos = text.index(keyword) + len(keyword)
        return text[start_pos:].strip()
    except ValueError:
        return None

def find_element_and_extract_text(driver, xpath, extractor_function=None, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        text = element.text
        return extractor_function(text) if extractor_function else text
    except Exception as e:
        return None

def extract_number_of_reviews(text):
    match = re.search(r'(\d+)', text)
    if match:
        return int(match.group(1))
    else:
        return 0

def download_images(data: list, folder_path: str):
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    counter=0
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for img_url in data:
        counter+=1
        img_url=f'http:{img_url}'.split('_4')[0]
        img_data = requests.get(img_url,headers=header).content
        with open(f"{folder_path}/image_{counter + 1}.jpg", 'wb') as img_file:
            img_file.write(img_data)

def extract_reviews(text):
    match = re.search(r'\((\d+) отзыв', text)
    if match:
        return int(match.group(1))
    else:
        return None

def extract_numbers(text):
    match = re.search(r'(\d+)', text)
    if match:
        return int(match.group(1))
    else:
        return None

def extract_id_from_url(url):
    match = re.search(r'id=(\d+)', url)
    if match:
        return int(match.group(1))
    else:
        return None

def find_part_number(driver, xpath):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text.strip()
    except Exception as e:
#        print(f"An error occurred: {e}")
        return None #

def save_to_csv(filename):
    keys = product_info_list[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(product_info_list)

def img_parser(url,folder_path):
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    response = requests.get(url,headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')
    count=0;res={}
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for i in soup.find_all('img', class_='gallery_Gallery__image__1gsooe'):
        if i.get('alt'):
            count+=1
            res[count]=[]
        res[count].append(i.get('data-src'))
    if not os.path.exists(folder_path+'/result'):
        open(folder_path+'/result','a').write(json.dumps(res, indent=4))
    return res


def main():
    global product_info_list
    global current_datetime
    global path
    for page_number in range(20, 21+N):
        count=0
        url = f"https://aliexpress.ru/store/1941865?g=y&page={page_number}"
        res = img_parser(url,folder_path=path)
        for i in range(len(res)):
            download_images(data=res[i+1],folder_path=f"{path}/{i+1}")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(15)
        product_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'product-snippet_ProductSnippet__content')]")
        product_links = []
        for card in product_cards:
            lnk = card.find_element(By.TAG_NAME,"a").get_attribute('href')
            product_links.append(lnk)
        for link in product_links:
            driver.get(link)
            time.sleep(5)
            product_dict = {        
                'Id': str(count+1),
                'url': str(link),
                'Наименование': None,
                'Цена': None,
                'Доставка курьером': None,
                'Доставка в пункт выдачи': None,
                'Сколько раз купили': None,
                'Рейтинг': None,
                'Кол-во отзывов': None,
                'Описание': None,
                'Фото': None,
                'Отзывы покупателей': None,
                'Номер детали': None
            }
    #            product_info['url'] = driver.current_url
            product_name = find_element_and_extract_text(driver, "//h1[contains(@class, 'HazeProductDescription_HazeProductDescription__name__1bnud')]")
            product_price = find_element_and_extract_text(driver, "//div[contains(@class, 'snow-price_SnowPrice__mainS__jlh6el')]")
            first_price = find_element_and_extract_text(driver, "//div[@class='HazeProductDelivery_DeliveryMethodItem__item__1pl51'][1]//span[contains(text(), 'в‚Ѕ')]")
            second_price = find_element_and_extract_text(driver, "//div[@class='HazeProductDelivery_DeliveryMethodItem__item__1pl51'][2]//span[contains(text(), 'в‚Ѕ')]")
            purchases = find_element_and_extract_text(driver, "//span[contains(text(), 'купили')]", extractor_function=extract_numbers)
            rating = find_element_and_extract_text(driver, "//a[contains(@class, 'HazeProductDescription_HazeProductDescription__ratingNumber__1bnud')]")
            number_of_reviews = find_element_and_extract_text(driver, "//a[contains(@class, 'HazeProductDescription_HazeProductDescription__anchorLink__1bnud') and contains(@href, '#reviews_anchor')]", extractor_function=extract_numbers)
            #    reviews = find_element_and_extract_text(driver, "//a[contains(@href, '#reviews_anchor')]", extractor_function=extract_reviews)
            #    reviews = driver.find_element(By.XPATH, "//a[contains(@class, 'HazeProductDescription_HazeProductDescription__anchorLink__1bnud') and contains(@href, '#reviews_anchor')]")
            description = find_element_and_extract_text(driver, "//div[contains(@class, 'detail-desc-decorate-richtext')]")
            customer_reviews = find_element_and_extract_text(driver, "//p[@class='snow-reviews-v2_ContentItem__text__3qf5ol'][1]")
            part_number = find_part_number(driver, "//div[contains(@class, 'SnowProductCharacteristics_SnowProductCharacteristicsItem__item__1w7g4')]//span[contains(text(), 'Номер детали')]/following-sibling::span")
            product_dict['Наименование'] = product_name if product_name else "None"
            product_dict['Цена'] = product_price if product_price else "None"
            product_dict['Доставка курьером'] = first_price if first_price else "None"
            product_dict['Доставка в пункт выдачи'] = second_price if second_price else "None"
            product_dict['Сколько раз купили'] = purchases if purchases else "None"
            product_dict['Рейтинг'] = rating if rating else "None"
            product_dict['Кол-во отзывов'] = number_of_reviews if number_of_reviews else "None"
            product_dict['Описание'] = description if description else "None"
            product_dict['Фото'] = extract_id_from_url(driver.current_url) if extract_id_from_url(driver.current_url) else "None"
            product_dict['Отзывы покупателей'] = customer_reviews if customer_reviews else "None"
            product_dict['Номер детали'] = part_number if part_number else "None"
            # Р”РѕР±Р°РІР»РµРЅРёРµ СЃР»РѕРІР°СЂСЏ РІ СЃРїРёСЃРѕРє
            product_info_list.append(product_dict)
            shutil.copytree(f"{path}/{count+1}", f"{path}/{product_dict['Фото']}")
            shutil.rmtree(f'{path}/{count+1}')
            count+=1
            #download_images(data=res[count],folder_path=f"{path}/"+str(product_dict['Фото']))
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(":","").replace(" ","").replace(".","")
    print(product_links)       

    driver.quit()


if __name__ == "__main__":
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(":","").replace(" ","").replace(".","")
    N = 6
    main()
    filename = f"{path}/product_info_{current_datetime}.csv"
    save_to_csv(filename)
    print(f"Файл {filename} готов.")
