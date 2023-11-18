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


def main():
    url = 'https://hardware.schaefermarine.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    soup = fetch_html_content(url, headers)
    all_product_category_links = getting_product_category_links(soup, url)

    count = 1
    for product in all_product_category_links:
        print(f'{count}. {product}')
        count += 1


if __name__ == '__main__':
    main()
