import re
from bs4 import BeautifulSoup
import requests
import pickle


def save_processed_categories(processed_categories):
    with open("processed_categories.pkl", "wb") as file:
        pickle.dump(processed_categories, file)


def load_processed_categories():
    try:
        with open("processed_categories.pkl", "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []


def parse(url, session):
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    raw_links = soup.find_all("a", class_="cs-goods-title")
    products = [link.get("href") for link in raw_links]
    title = soup.find("h1").get_text(strip=True)
    next_url = soup.find("link", rel="next")
    next_url = next_url.get("href") if next_url else None
    return title, products, next_url


def get_domain_info(category):
    regex = re.search("//([A-Za-z_0-9.-]+).*", category)
    if regex:
        domain = regex.group(1)
        website_name = domain.split(".")[0]
        return domain, website_name
    return "", ""


def main(list_of_categories_file, save_path):

    try:
        with open(list_of_categories_file, "rt") as f:
            categories = f.read().splitlines()
    except FileNotFoundError:
        print(f"{list_of_categories_file} не существует.")
    processed_categories = load_processed_categories()

    for category in categories:
        if category in processed_categories:
            continue

        session = requests.Session()
        product_links = []
        domain, website_name = get_domain_info(category)

        while True:
            processed_categories.append(category)
            print(f"Parsing {category}")
            name, products, next_url = parse(category, session)
            product_links.extend(products)
            if not next_url:
                break
            category = next_url

        category_name = name
        with open(f"{save_path}{website_name}_{category_name.lower()}.txt", "wt") as file:
            for link in product_links:
                file.write(f"https://{domain}{link}\n")
        save_processed_categories(processed_categories)


if __name__ == "__main__":
    # Путь к файлу со списком категорий.
    list_of_categories_file = "files/list_of_categories.txt"

    # Путь к папке в которую будут сохранены файлы с ссылками на товары.
    save_path = "files/"

    main(list_of_categories_file, save_path)
