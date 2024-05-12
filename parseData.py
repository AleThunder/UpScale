import logging
import re
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.ERROR)


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    # Створює сесію з налаштованою політикою повторних спроб з'єднань для запитів
    # HTTP, що допомагає управляти з'єднаннями при нестабільних мережах.
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


class Parser:
    url = ""

    def __init__(self, url):
        self.url = url
        self.session = requests_retry_session()
        self.soup = BeautifulSoup(self.session.get(self.url).text, 'html.parser')
        self.product_id = self.eject_id()
        self.data = {}
    def eject_id(self):
        img_url = self.url.find("-", len("https://mixmol.com.ua/ua/p"))
        if img_url != -1:
            return self.url[len("https://mixmol.com.ua/ua/p"):img_url]

    def fetch_images_url(self):
        img_url = "https://mixmol.com.ua/ua/graphql"
        headers = {
            "Content-Type": "application/json",
        }
        body = {
            "operationName": "productImagesQuery",
            "variables": {"productId": int(self.product_id)},
            "query": """
                query productImagesQuery($productId: Int!) {
                    product(id: $productId) {
                        viewImages: images(width: 640, height: 640)
                    }
                }
            """
        }
        try:
            response = self.session.post(img_url, headers=headers, json=body)
            response.raise_for_status()
            response = response.json()
            return [image['url'] for image in response['data']['product']['viewImages']]
        except HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')  # HTTP error response
        except Exception as err:
            logging.error(f'Other error occurred: {err}')  # Other errors

    def parse_name(self):
        return self.soup.find(attrs={"data-qaid": "product_name"}).get_text(strip=True)

    def parse_sku(self):
        return self.soup.find(attrs={"data-qaid": "product_code"}).get_text(strip=True)

    def parse_price(self):
        price_text = self.soup.find(attrs={"data-qaid": "product_price"}).get_text(strip=True)
        return re.sub(r'\D+', '', price_text.split(',')[0])

    def parse_description(self):
        return str(self.soup.find(attrs={"data-qaid": "product_description"}))

    def parse_specifications(self):
        specifications = {}
        table = self.soup.find('table', class_='b-product-info')
        if table:
            for tr in table.find_all('tr'):
                cells = tr.find_all('td')
                if len(cells) == 2:
                    specifications[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
        else:
            specifications["Тип підйомного механізму"] = "Гідравлічний"
        return specifications

    def parse(self):
        try:
            self.data = {
                "name": self.parse_name(),
                "sku": self.parse_sku(),
                "price": self.parse_price(),
                "description": self.parse_description(),
                "specifications": self.parse_specifications(),
                "images": self.fetch_images_url()
            }
        except requests.exceptions.RequestException as e:
            logging.error(f" Error fetching {self.url}: {str(e)}", exc_info=True)
            self.data = {"Error": str(e)}
        finally:
            self.session.close()
            return self.data
