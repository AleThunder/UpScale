import requests, json, csv, re, logging
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logging.basicConfig(level=logging.ERROR)

# Форматування ціни товару
def clean_price(price_text):
    return re.sub(r'[^\d]+', '', price_text.split(',')[0])  # Видалити все, окрім цифр та крапки

# Попередньо визначені функції парсингу

#Функція використовує об'єкт BeautifulSoup для витягу назви продукту з HTML сторінки. 
#Атрибут data-qaid="product_name" використовується як маркер для визначення місця назви в документі.
def parse_name(soup):
    return soup.find(attrs={"data-qaid": "product_name"}).get_text(strip=True)
    
#Схожа на попередню функцію, але замість назви вона знаходить SKU (stock keeping unit) продукту.
def parse_sku(soup):
    return soup.find(attrs={"data-qaid": "product_code"}).get_text(strip=True)
    
#Функція витягує текст ціни і передає його в функцію clean_price для форматування.
def parse_price(soup):
    price_text = soup.find(attrs={"data-qaid": "product_price"}).get_text(strip=True)
    return clean_price(price_text)

#
def parse_description(soup):
    return str(soup.find(attrs={"data-qaid": "product_description"}))

#Отримує опис продукту з HTML. Повертає опис у вигляді рядка.
def parse_specifications(soup):
    specifications = {}
    table = soup.find('table', class_='b-product-info')
    if table:
        for tr in table.find_all('tr'):
            cells = tr.find_all('td')
            if len(cells) == 2:
                specifications[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
    else:
        specifications["Тип підйомного механізму"] = "Гідравлічний"
    return specifications

#Витягує ідентифікатор продукту з URL, використовуючи структуру URL як ключ для визначення місця розташування ідентифікатора.
def extract_product_id(url):
    # Дістаєм id товару по url
    prefix = "https://mixmol.com.ua/ua/p"
    suffix_position = url.find("-", len(prefix))
    if suffix_position != -1:
        product_id = url[len(prefix):suffix_position]
        return product_id
    return None

#Функція, яка використовує сесію з повторними спробами з'єднання для отримання зображень продуктів за допомогою GraphQL запиту.
def fetch_product_images(product_id, session):
    """
    Fetch product images using a persistent session and caching.
    """
    url = "https://mixmol.com.ua/ua/graphql"
    headers = {
        "Content-Type": "application/json",
    }
    body = {
        "operationName": "productImagesQuery",
        "variables": {"productId": int(product_id)},
        "query": """
            query productImagesQuery($productId: Int!) {
                product(id: $productId) {
                    viewImages: images(width: 640, height: 640)
                }
            }
        """
    }
    try:
        response = session.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        image_urls = [image['url'] for image in data['data']['product']['viewImages']]
        return image_urls
    except HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')  # HTTP error response
    except Exception as err:
        logging.error(f'Other error occurred: {err}')  # Other errors
    return []

#Створює сесію з налаштованою політикою повторних спроб з'єднань для запитів HTTP, що допомагає управляти з'єднаннями при нестабільних мережах.
def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Ця функція інтегрує всі вищеописані функції для отримання даних з конкретного URL. 
#Вона обробляє можливі винятки та зберігає сесію до закриття.
def parse_url(url):
    all_data = {}
    
    session = requests_retry_session()
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        product_id = extract_product_id(url)
        if product_id:
            image_urls = fetch_product_images(product_id, session)
        else:
            image_urls = []
        data = {
            "name": parse_name(soup),
            "sku": parse_sku(soup),
            "price": parse_price(soup),
            "description": parse_description(soup),
            "specifications": parse_specifications(soup),
            "images": image_urls
        }

    except requests.exceptions.RequestException as e:
        logging.error(f" Error fetching {url}: {str(e)}", exc_info=True)
        data = {"Error": str(e)}
    finally:
        session.close()

        return data

#Функція, яка викликає parse_url для конкретного URL і повертає результати.
def parse(url):
    data = parse_url(url)
    return(data)

#Для запуску цього скрипта окремо від програми розкоментуйте наступний код та передайте url mixmol товару в функцію - parse(URL)
#if __name__ == "__main__":
#    test_data = parse('https://mixmol.com.ua/ua/p2060998049-parikmaherskoe-kreslo-hektor.html')
#    print(test_data)