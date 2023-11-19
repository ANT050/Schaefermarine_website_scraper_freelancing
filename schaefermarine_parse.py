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


def getting_product_category_links(soup: BeautifulSoup, url: str) -> list:
    product_categories = soup.find('span', string='Product Categories')

    list_category_links = []

    if product_categories:
        # Найти все ссылки внутри списка
        all_links = product_categories.find_next('ul', class_='widemenu').find_all('a', class_='widemenu__link')

        for link in all_links:
            list_category_links.append(f'{url.rstrip("/")}{link["href"]}')

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


def main():
    base_url = 'https://hardware.schaefermarine.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    soup = fetch_html_content(base_url, headers)
    all_product_category_links = getting_product_category_links(soup, base_url)
    all_links_to_category_pages = getting_category_page_links(base_url, headers, all_product_category_links)

    count = 1
    for i in all_links_to_category_pages:
        print(f'{count}. {i}')
        count += 1


if __name__ == '__main__':
    main()
