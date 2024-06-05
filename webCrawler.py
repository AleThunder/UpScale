import logging
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
    async def fetch_images(self, url):
        # Реалізація завантаження сторінки та парсингу зображень за допомогою CSS селекторів
        pass


class GraphQLImageParsingStrategy(ImageParsingStrategy):
    async def fetch_images(self, url):
        headers = {
            "Content-Type": "application/json",
        }
        body = {
            "operationName": "productImagesQuery",
            "variables": {"productId": int(await self.eject_id(url))},
            "query": """
                        query productImagesQuery($productId: Int!) {
                            product(id: $productId) {
                                viewImages: images(width: 640, height: 640)
                            }
                        }
                    """,
        }


class Parser:
    def __init__(self, image_strategy: ImageParsingStrategy):
        self.image_strategy = image_strategy
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
        return element.get_text(strip=True) if element else None

    async def parse(self, url, selectors):
        page_content = await self.fetch_page(url)
        soup = BeautifulSoup(page_content, "html.parser")

        parsed_data = {
            "raw_name": self.get_element(soup, selectors.get("name")),
            "sku": self.get_element(soup, selectors.get("sku")),
            "price": self.get_element(soup, selectors.get("price")),
            "raw_description": self.get_element(soup, selectors.get("description")),
            "raw_specification": self.get_element(soup, selectors.get("specification")),
        }

        return parsed_data
