import logging
import re
from abc import ABC, abstractmethod

import httpx
from bs4 import BeautifulSoup

from retry_client import RetryClient  # Імпорт власного клієнта з повторними спробами

logging.basicConfig(level=logging.ERROR)


class ImageParsingStrategy(ABC):
    @abstractmethod
    async def fetch_images(self, url):
        pass

    @staticmethod
    async def eject_id(url):
        img_url = url.find("-", len("https://mixmol.com.ua/ua/p"))
        if img_url != -1:
            return url[len("https://mixmol.com.ua/ua/p") : img_url]


class CssImageParsingStrategy(ImageParsingStrategy):
    async def fetch_images(self, url=None, product_id=None, domain=None):
        # Реалізація завантаження сторінки та парсингу зображень за допомогою CSS селекторів
        pass


class GraphQLImageParsingStrategy(ImageParsingStrategy):
    async def fetch_images(self, url=None, product_id=None, domain=None):
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
                    """,
        }
        try:
            async with httpx.AsyncClient() as client:
                images = []
                response = await client.post(
                    f"https://{domain}/graphql", headers=headers, json=body
                )
                response.raise_for_status()
                data = response.json()
                for image in data["data"]["product"]["viewImages"]:
                    images.append(image["url"])
                return images
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e}")
            return []


class Parser:
    def __init__(self, url, selectors, image_strategy, p_id, domain):
        self.domain = domain
        self.url = url
        self.selectors = selectors
        self.image_strategy = image_strategy
        self.p_id = p_id
        self.client = RetryClient()

    async def fetch_page(
        self, url=None, method="GET", headers=None, data=None
    ) -> str | None:
        try:
            response = await self.client.request(
                method, url, headers=headers, json=data
            )
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e}")
            return None

    @staticmethod
    async def get_element(soup, selector):
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else "0"

    @staticmethod
    async def get_specifications(soup, selector):
        specifications = {}
        elements = soup.select(selector)
        if elements:
            for element in elements:
                cells = element.find_all("td")
                specifications[cells[0].get_text(strip=True)] = cells[1].get_text(
                    strip=True
                )
        else:
            specifications["Подъёмный механизм"] = "Гидравлический"
        return specifications

    async def parse(self):
        page_content = await self.fetch_page(self.url)
        if not page_content:
            return {}

        soup = BeautifulSoup(page_content, "html.parser")
        price = await self.get_element(soup, self.selectors.get("price"))
        parsed_data = {
            "name": await self.get_element(soup, self.selectors.get("name")),
            "sku": await self.get_element(soup, self.selectors.get("sku")),
            "price": re.sub(r"\D+", "", price),
            "description": await self.get_element(
                soup, self.selectors.get("description")
            ),
            "specification": await self.get_specifications(
                soup, self.selectors.get("specification")
            ),
            "images": await self.image_strategy.fetch_images(
                url=self.url, product_id=self.p_id, domain=self.domain
            ),
        }

        return parsed_data
