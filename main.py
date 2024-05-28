import asyncio
from parseData import Parser
from dataFormat import Director, ProductBuilder, ClientGpt
import pickle

data = {}


async def save_processed_urls(processed_urls):
    with open("processed_urls.pkl", "wb") as file:
        pickle.dump(processed_urls, file)


async def load_processed_urls():
    try:
        with open("processed_urls.pkl", "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []


async def process_url(url, semaphore, processed_urls):
    async with semaphore:
        parser = Parser(url)
        parsed_data = await parser.parse()

        director = Director()
        gpt = ClientGpt(parsed_data)
        builder = ProductBuilder(parsed_data)

        director.gpt = gpt
        director.builder = builder

        await director.build_product()
        product = builder.product

        print(product.body)
        processed_urls.append(url)
        await save_processed_urls(processed_urls)


async def main(max_concurrent):
    with open("files/url_list.txt", 'r') as f:
        urls = f.read().splitlines()

    processed_urls = await load_processed_urls()
    semaphore = asyncio.Semaphore(max_concurrent)

    tasks = [process_url(url, semaphore, processed_urls) for url in urls if url not in processed_urls]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    max_concurrent_tasks = 5  # або встановіть бажану кількість
    asyncio.run(main(max_concurrent_tasks))