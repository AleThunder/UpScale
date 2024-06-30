import asyncio
import csv

import aiofiles

from parseData import Parser
from dataFormat import Director, ProductBuilder, ClientGpt
import pickle

MAX_TASKS = 5  # або встановіть бажану кількість
FILE_NAME = "files/velmi_3.txt"


async def save_processed_urls(processed_urls):
    with open("processed_urls.pkl", "wb") as file:
        pickle.dump(processed_urls, file)


async def load_processed_urls():
    try:
        with open("processed_urls.pkl", "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []


# Функция для записи данных в CSV
async def save_to_csv(name, sku, csv_file='products.csv'):
    async with aiofiles.open(csv_file, mode='a', newline='') as f:
        await f.write(f"{name},{sku}\n")


async def process_url(url, semaphore, processed_urls, csv_file='files/added_products.csv'):
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

        await product.post()
        print(product.body["name"])
        await save_to_csv(product.body["name"], product.body["sku"], csv_file)

        processed_urls.append(url)
        await save_processed_urls(processed_urls)


async def main(max_concurrent):
    with open(FILE_NAME, 'r') as f:
        urls = f.read().splitlines()

    processed_urls = await load_processed_urls()
    semaphore = asyncio.Semaphore(max_concurrent)

    tasks = [process_url(url, semaphore, processed_urls) for url in urls if url not in processed_urls]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main(MAX_TASKS))
