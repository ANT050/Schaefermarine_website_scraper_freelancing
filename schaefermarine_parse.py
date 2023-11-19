import requests
from bs4 import BeautifulSoup


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


def getting_product_category_links(soup: BeautifulSoup, url: str, menu_section: list) -> list:
    list_category_links = []

    for section in menu_section:
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


def main():
    base_url = 'https://hardware.schaefermarine.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    menu_section = ['Product Categories', 'Partner Products']

    soup = fetch_html_content(base_url, headers)
    all_product_category_links = getting_product_category_links(soup, base_url, menu_section)
    all_links_to_category_pages = getting_category_page_links(base_url, headers, all_product_category_links)
    links_to_products = get_links_to_products(all_links_to_category_pages, base_url, headers)

    count = 1
    for i in links_to_products:
        print(f'{count}. {i}')
        count += 1


if __name__ == '__main__':
    main()
