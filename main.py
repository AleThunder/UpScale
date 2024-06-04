import asyncio
from parseData import Parser
from dataFormat import Director, ProductBuilder, ClientGpt
import pickle
from dbManager import Source, Selector, Input, Result
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse
import re

INPUT_FILE_NAME = "url.txt"


# async def save_processed_urls(processed_urls):
#     with open("processed_urls.pkl", "wb") as file:
#         pickle.dump(processed_urls, file)


# async def load_processed_urls():
#     try:
#         with open("processed_urls.pkl", "rb") as file:
#             return pickle.load(file)
#     except FileNotFoundError:
#         return []

# 
# async def process_url(url, semaphore, processed_urls):
#     async with semaphore:
#         parser = Parser(url)
#         parsed_data = await parser.parse()
# 
#         director = Director()
#         gpt = ClientGpt(parsed_data)
#         builder = ProductBuilder(parsed_data)
# 
#         director.gpt = gpt
#         director.builder = builder
# 
#         await director.build_product()
#         product = builder.product
# 
#         print(product.body)
#         processed_urls.append(url)
#         await save_processed_urls(processed_urls)


def get_selectors_for_domain(session, source_id):
    selectors = session.query(Selector).filter_by(source_id=source_id).all()
    return {selector.element_type: selector.css for selector in selectors}


def parse_line(line):
    parts = line.split('|')

    url = parts[0]
    product_id_match = re.search(r'/p(\d+)', url)
    product_id = f"p{product_id_match.group(1)}" if product_id_match else None
    brand = parts[1]

    domain = urlparse(url).netloc
    graphql = True if parts[2].lower() in ('y', 'yes', 't', 'true', 'on', '1') else False
    selectors_id = int(parts[3])

    return url, product_id, brand, domain, graphql, selectors_id


async def main(max_concurrent):
    engine = create_engine('sqlite:///database.db')
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_local()

    with open(f"files/{INPUT_FILE_NAME}", 'r') as f:
        for line in f.read().splitlines():
            url, product_id, brand, domain, graphql, selectors_id = parse_line(line)
            new_source = Source(domain=domain, graphql=graphql, selectors_id=selectors_id)
            new_input = Input(url=url, p_id=product_id, brand=brand, source_id=new_source.id)
            new_result = Result(url=url, p_id=product_id, brand=brand, input_id=new_source.id)

    input_urls = session.query(Input).filter_by(status=False).all()
    for input_url in input_urls:
        selectors = get_selectors_for_domain(session, input_url.source_id)

    # processed_urls = await load_processed_urls()
    # semaphore = asyncio.Semaphore(max_concurrent)
    # 
    # tasks = [process_url(url, semaphore, processed_urls) for url in urls if url not in processed_urls]
    # await asyncio.gather(*tasks)


if __name__ == "__main__":
    max_concurrent_tasks = 5  # або встановіть бажану кількість
    asyncio.run(main(max_concurrent_tasks))
