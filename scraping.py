"""Реализован парсинг"""

import os
import requests
from bs4 import BeautifulSoup as bs4


from services import create_csv


PAGES = 18  # Сколько страниц парсить (на тек момент максимум 18 (больше страниц нету))
COUNT_SCRAPED = 0

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
}

"""Скачивает нужную картинку"""
def download_images(images):
    try:
        os.mkdir(f"files/{COUNT_SCRAPED}")
    except FileExistsError:
        return []
    paths = []
    for image in images:
        path = f"files/{COUNT_SCRAPED}/{image.split('/')[-1]}"
        image_response = requests.get(image, headers=headers, stream=True)
        with open(path, "wb") as f:
            for chunk in image_response:
                f.write(chunk)
        paths.append(path)
    return paths

"""Парсит нужную страницу"""
def scraping(page, data_rows_4gb, data_rows_8gb, data_rows_16gb, data_rows_32gb, data_rows_64gb):
    global COUNT_SCRAPED

    print(f"Парсинг страницы {page}")
    res = requests.get(f"https://it-blok.com.ua/computeri.html?page={page}", headers=headers).text
    soup = bs4(res, 'html.parser')

    items = soup.findAll("div", class_='product-inner')
    for item in items:
        COUNT_SCRAPED += 1
        item_url = "https://it-blok.com.ua/" + item.findNext().findNext().get('href')

        # Данные достаем с карточки товара
        caption = item.find("div", class_="caption")
        title = caption.find("div", class_="h4").findNext("a").text
        price = caption.find("p", class_="price").find("span", class_="price-new").text
        count_review = str(caption.find("div", class_="rating-prods").find("span", class_="r-count").text).replace("(", '').replace(")", '')

        items_table = caption.find("div", class_="grid-attrs").findAll("tr")
        processor, count_yader, ozy, video_card, ssd, hdd = ['---' for i in range(6)]
        for tr in items_table:
            if "Процессор" in tr.text:
                processor = tr.findAll("td")[1].text
            elif "Количество ядер" in tr.text:
                count_yader = tr.findAll("td")[1].text
            elif "Объем памяти ОЗУ" in tr.text:
                ozy = tr.findAll("td")[1].text
            elif "Видеокарта" in tr.text:
                video_card = tr.findAll("td")[1].text
            elif 'SSD' in tr.text:
                ssd = tr.findAll("td")[1].text
            elif 'HDD' in tr.text:
                hdd = tr.findAll("td")[1].text

        # Для этих данных делаем запрос на страницу товара
        result = requests.get(item_url, headers=headers).text
        soup_html = bs4(result, 'html.parser')

        # Достаем картинки
        images = []
        images_main = soup_html.find("div", class_="pp-l-blok").findNext().find("a")
        try:
            images_low = soup_html.find("div", class_="pp-l-blok").find("ul").findAll("a")
        except AttributeError:
            images_low = []
        images.append("https://it-blok.com.ua/" + images_main.get('href'))
        for image in images_low:
            images.append("https://it-blok.com.ua/" + image.get('href'))

        # Достаем нужные данные
        table_data = soup_html.find("div", class_="tab-content").findAll("tbody")
        count_video_memory, mather_plate = ['----', '----']
        for tbody in table_data:
            if "Объем видеопамяти" in tbody.text:
                count_video_memory = tbody.findAll("tr")[-1].findAll("td")[1].text
            elif "На чипсете" in tbody.text:
                mather_plate = tbody.find("tr").findAll("td")[1].text

        # Скачиваем картинки
        image_paths = ' | '.join(download_images(images))

        row = [item_url, title, price, count_review, image_paths, video_card, count_video_memory,
               processor, count_yader, ozy, ssd, hdd, mather_plate]

        if '64' in ozy:
            data_rows_64gb.append(row)
        elif '32' in ozy:
            data_rows_32gb.append(row)
        elif '16' in ozy:
            data_rows_16gb.append(row)
        elif '8' in ozy:
            data_rows_8gb.append(row)
        elif '4' in ozy:
            data_rows_4gb.append(row)

if __name__ == '__main__':
    headers_rows = ["Url", 'Title', 'Price', 'Count Review', "Images", "Videocard", "Count VideoMemory", "Processor",
               "Count Yader", "OZY", "SSD", "HDD", "Mother Plate"]

    data_rows_4gb, data_rows_8gb, data_rows_16gb, data_rows_32gb, data_rows_64gb = [], [], [], [], []
    for page in range(1, PAGES+1):
        scraping(page, data_rows_4gb, data_rows_8gb, data_rows_16gb, data_rows_32gb, data_rows_64gb)

    # Создаем файлы csv
    create_csv("4gb.csv", headers_rows, data_rows_4gb)
    create_csv("8gb.csv", headers_rows, data_rows_8gb)
    create_csv("16gb.csv", headers_rows, data_rows_16gb)
    create_csv("32gb.csv", headers_rows, data_rows_32gb)
    create_csv("64gb.csv", headers_rows, data_rows_64gb)


