import concurrent.futures
import json

import requests
from bs4 import BeautifulSoup
import pandas as pd


def fetch_html_content(url: str, headers: dict) -> BeautifulSoup | None:
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'lxml')

            return soup
        else:
            print(f"Ошибка: {response.status_code}")

            return None

    except Exception:
        print("Ошибка: Неправильно указан URL")

        return None


def getting_product_category_links(url: str, headers: dict, menu_section: list) -> list:
    list_category_links = []

    for section in menu_section:
        soup = fetch_html_content(url, headers)
        product_section = soup.find('span', string=section)

        if product_section:
            # Найти все ссылки внутри списка
            all_links = product_section.find_next('ul', class_='widemenu').find_all('a', class_='widemenu__link')
            list_category_links.extend(f'{url.rstrip("/")}{link["href"]}' for link in all_links)

    return list_category_links


def getting_category_page_links(base_url: str, headers: dict, category_links: list) -> list:
    links_to_category_pages = []

    for link_to_category in category_links:
        url_pages = link_to_category
        links_to_category_pages.append(url_pages)

        while True:
            soup = fetch_html_content(url_pages, headers)

            next_button = soup.find('span', class_='next')

            if next_button is None:
                break

            link_next_button = next_button.find('a')['href']
            url_pages = f'{base_url.rstrip("/")}{link_next_button}'

            links_to_category_pages.append(url_pages)

    return links_to_category_pages


def get_links_to_products(category_pages: list, base_url: str, headers: dict) -> list:
    links_to_products = []

    for page in category_pages:
        soup = fetch_html_content(page, headers)
        all_url_product = soup.find_all('div', class_='thumbnail-overlay')

        if all_url_product:
            links_to_products.extend(f'{base_url.rstrip("/")}{url.find("a")["href"]}' for url in all_url_product)
        else:
            links_to_products.append(page)

    return links_to_products


def extract_product_data(url: str, headers: dict) -> dict:
    soup = fetch_html_content(url, headers)

    title = soup.find('div', class_='product-block--title').text.split()
    product_name = ' '.join(title[:-1])
    product_number = soup.find('div', class_='product-block--sku').text.strip()
    product_price = soup.find('div', class_='price-ui').find_next('span', class_='price').text
    product_description = soup.find('div', class_='rte').text.strip().replace('\n', ' ')

    product_data = {
        'Product name': product_name,
        'Product number': product_number,
        'Product price': product_price,
        'Product description': product_description,
        'Product url': url
    }

    return product_data


def threaded_get_product_info(urls: list, headers: dict, num_threads: int = 5) -> list:
    all_products_data = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Запуск функцию extract_product_data для каждого URL в отдельном потоке
        futures = {executor.submit(extract_product_data, url, headers): url for url in urls}

        # Обрабатка результата по мере их завершения
        for future in concurrent.futures.as_completed(futures):
            result_data = future.result()
            all_products_data.append(result_data)

    return all_products_data


def write_to_csv(data: list, filename: str) -> None:
    df = pd.DataFrame(data)
    df.columns = [
        'Product name',
        'Product number',
        'Product price',
        'Product description',
        'Product url',
    ]
    df.to_csv(filename, index=False)


def write_to_json(data: list, filename: str) -> None:
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def main():
    base_url = 'https://hardware.schaefermarine.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    menu_section = ['Product Categories', 'Partner Products']
    number_threads = 13

    all_product_category_links = getting_product_category_links(base_url, headers, menu_section)
    all_links_to_category_pages = getting_category_page_links(base_url, headers, all_product_category_links)
    links_to_products = get_links_to_products(all_links_to_category_pages, base_url, headers)
    products_info = threaded_get_product_info(links_to_products, headers, number_threads)

    write_to_csv(products_info, 'Schaefermarine_website.csv')
    write_to_json(products_info, 'Schaefermarine_website.json')


if __name__ == '__main__':
    main()
