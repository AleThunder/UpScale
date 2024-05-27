import logging
import re
import json
from bs4 import BeautifulSoup
import asyncio
from retry_client import RetryClient  # Імпорт власного клієнта з повторними спробами

logging.basicConfig(level=logging.ERROR)


class Parser:
    url = ""

    def __init__(self, url):
        self.url = url
        self.client = RetryClient()
        self.soup = BeautifulSoup(self.session.get(self.url).text, 'html.parser')
        self.product_id = self.eject_id()
        self.data = {}

    async def eject_id(self):
        img_url = self.url.find("-", len("https://mixmol.com.ua/ua/p"))
        if img_url != -1:
            return self.url[len("https://mixmol.com.ua/ua/p"):img_url]

    async def fetch_images_url(self):
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
            response_text = await self.fetch(img_url, method='POST', headers=headers, data=body)
            if response_text:
                response = json.loads(response_text)
                return [image['url'] for image in response['data']['product']['viewImages']]
        except Exception as err:
            logging.error(f'Other error occurred: {err}')  # Other errors

    async def parse_name(self):
        return self.soup.find(attrs={"data-qaid": "product_name"}).get_text(strip=True)

    async def parse_sku(self):
        return self.soup.find(attrs={"data-qaid": "product_code"}).get_text(strip=True)

    async def parse_price(self):
        price_text = self.soup.find(attrs={"data-qaid": "product_price"}).get_text(strip=True)
        return re.sub(r'\D+', '', price_text.split(',')[0])

    async def parse_description(self):
        return str(self.soup.find(attrs={"data-qaid": "product_description"}).get_text(strip=True))

    async def parse_specifications(self):
        specifications = {}
        table = self.soup.find('table', class_='b-product-info')
        if table:
            for tr in table.find_all('tr'):
                cells = tr.find_all('td')
                if len(cells) == 2:
                    specifications[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
        else:
            specifications["Подъёмный механизм"] = "Гидравлический"
        return specifications

    async def parse(self):
        try:
            html = await self.fetch(self.url)
            if not html:
                return {"Error": "Failed to retrieve HTML"}
            self.soup = BeautifulSoup(html, 'html.parser')
            self.data = {
                "name": await self.parse_name(),
                "sku": await self.parse_sku(),
                "price": await self.parse_price(),
                "description": await self.parse_description(),
                "specifications": await self.parse_specifications(),
                "images": await self.fetch_images_url()
            }
        finally:
            await self.client.close()
        return self.data
