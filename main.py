import asyncio
import re
from urllib.parse import urlparse

from dbManager import Source, Input, Selector, DatabaseManager
from webCrawler import Parser

CONCURRENT_LIMIT = 1
INPUT_FILE_NAME = "url.txt"
P_TYPE = "simple"
P_STATUS = "draft"


class URLProcessor:
    def __init__(self, session, input_file_name):
        self.session = session
        self.input_file_name = input_file_name

    @staticmethod
    def parse_line(line):
        parts = line.split("|")
        url = parts[0]
        product_id_match = re.search(r"/p(\d+)", url)
        product_id = f"{product_id_match.group(1)}" if product_id_match else None
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

                existing_source = (
                    self.session.query(Source).filter_by(domain=domain).first()
                )
                if not existing_source:
                    new_source = Source(
                        domain=domain, graphql=graphql, selectors_id=selectors_id
                    )
                    self.session.add(new_source)
                    self.session.commit()
                else:
                    new_source = existing_source

                existing_input = self.session.query(Input).filter_by(url=url).first()
                if not existing_input:
                    new_input = Input(
                        url=url, p_id=product_id, brand=brand, source_id=new_source.id
                    )
                    self.session.add(new_input)
            self.session.commit()


class SelectorProcessor:
    def __init__(self, session):
        self.session = session

    def add_selectors_to_db(self):
        group_id = input("Введіть id групи селекторів: ").strip()
        element_type = input(
            "Введіть тип елементу (наприклад, 'name', 'sku'): "
        ).strip()
        css_selector = input("Введіть CSS селектор: ").strip()

        new_selector = Selector(
            group_id=group_id, element_type=element_type, css=css_selector
        )
        self.session.add(new_selector)
        self.session.commit()
        print(f"Селектор '{element_type}' для групи '{group_id}' успішно доданий.")


class AsyncProcessor:
    def __init__(self, session, concurrent_limit):
        self.session = session
        self.concurrent_limit = concurrent_limit

    async def process_url(self, input_item, semaphore):
        async with semaphore:
            image_strategy = DatabaseManager.get_image_strategy_for_domain(
                self.session, input_item.source_id
            )
            source = (
                self.session.query(Source).filter_by(id=input_item.source_id).first()
            )
            selectors = DatabaseManager.get_selectors_for_domain(
                self.session, source.selectors_id
            )

            parser = Parser(
                input_item.url,
                selectors,
                image_strategy,
                input_item.p_id,
                source.domain,
            )
            parsed_data = await parser.parse()
            print(parsed_data)

            # director = Director()
            # gpt = ClientGpt(parsed_data)
            # builder = ProductBuilder(parsed_data)
            #
            # director.gpt = gpt
            # director.builder = builder
            #
            # await director.build_product()
            # product = builder.product
            #
            # print(product.body)

    async def process_urls(self):
        inputs = self.session.query(Input).filter_by(status=False).all()
        semaphore = asyncio.Semaphore(self.concurrent_limit)
        tasks = []

        for input_item in inputs:
            tasks.append(self.process_url(input_item, semaphore))

        await asyncio.gather(*tasks)


class MainApp:
    def __init__(self, input_file_name, concurrent_limit):
        self.input_file_name = input_file_name
        self.concurrent_limit = concurrent_limit

    def run(self):
        DatabaseManager.initialize_database()
        session = DatabaseManager.get_session()

        action = (
            input(
                "Введіть дію ('read' для зчитування даних з файлу та додавання до БД, 'start' для запуску обробки URL, 'add_selector' для додавання селектора в БД): "
            )
            .strip()
            .lower()
        )

        if action == "read":
            url_processor = URLProcessor(session, self.input_file_name)
            url_processor.load_urls_to_db()
        elif action == "start":
            async_processor = AsyncProcessor(session, self.concurrent_limit)
            asyncio.run(async_processor.process_urls())
        elif action == "add_selector":
            selector_processor = SelectorProcessor(session)
            selector_processor.add_selectors_to_db()
        else:
            print("Невідома дія. Будь ласка, введіть 'read' або 'start'.")


if __name__ == "__main__":
    app = MainApp(INPUT_FILE_NAME, CONCURRENT_LIMIT)
    app.run()
