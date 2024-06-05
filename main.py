import asyncio
import re
from urllib.parse import urlparse

from dataFormat import Director, ProductBuilder, ClientGpt
from dbManager import Source, Input, DatabaseManager
from webCrawler import Parser

CONCURRENT_LIMIT = 5
INPUT_FILE_NAME = "url.txt"


class URLProcessor:
    def __init__(self, session, input_file_name):
        self.session = session
        self.input_file_name = input_file_name

    @staticmethod
    def parse_line(line):
        parts = line.split("|")
        url = parts[0]
        product_id_match = re.search(r"/p(\d+)", url)
        product_id = f"p{product_id_match.group(1)}" if product_id_match else None
        brand = parts[1]
        domain = urlparse(url).netloc
        graphql = (
            True if parts[2].lower() in ("y", "yes", "t", "true", "on", "1") else False
        )
        selectors_id = int(parts[3])
        return url, product_id, brand, domain, graphql, selectors_id

    def load_urls_to_db(self):
        with open(f"files/{INPUT_FILE_NAME}", "r") as f:
            for line in f.read().splitlines():
                url, product_id, brand, domain, graphql, selectors_id = self.parse_line(
                    line
                )
                new_source = Source(
                    domain=domain, graphql=graphql, selectors_id=selectors_id
                )
                self.session.add(new_source)
                self.session.commit()  # Save to get the new_source.id

                new_input = Input(
                    url=url, p_id=product_id, brand=brand, source_id=new_source.id
                )
                self.session.add(new_input)
            self.session.commit()


class AsyncProcessor:
    def __init__(self, session, concurrent_limit):
        self.session = session
        self.concurrent_limit = concurrent_limit

    async def process_url(self, input_url, semaphore):
        async with semaphore:
            selectors = DatabaseManager.get_selectors_for_domain(
                self.session, input_url.source_id
            )
            image_strategy = DatabaseManager.get_image_strategy_for_domain(
                self.session, input_url.source_id
            )

            parser = Parser(image_strategy)
            parsed_data = await parser.parse(input_url.url, selectors)

            director = Director()
            gpt = ClientGpt(parsed_data)
            builder = ProductBuilder(parsed_data)

            director.gpt = gpt
            director.builder = builder

            await director.build_product()
            product = builder.product

        print(product.body)

    async def process_urls(self):
        input_urls = self.session.query(Input).filter_by(status=False).all()
        semaphore = asyncio.Semaphore(self.concurrent_limit)
        tasks = []

        for input_url in input_urls:
            tasks.append(self.process_url(input_url, semaphore))

        await asyncio.gather(*tasks)


class MainApp:
    def __init__(self, input_file_name, concurrent_limit):
        self.input_file_name = input_file_name
        self.concurrent_limit = concurrent_limit

    def run(self):
        DatabaseManager.initialize_database()
        session = DatabaseManager.get_session()

        url_processor = URLProcessor(session, self.input_file_name)
        url_processor.load_urls_to_db()

        async_processor = AsyncProcessor(session, self.concurrent_limit)
        asyncio.run(async_processor.process_urls())


if __name__ == "__main__":
    app = MainApp(INPUT_FILE_NAME, CONCURRENT_LIMIT)
    app.run()
