from parseData import Parser
from dataFormat import Director, ProductBuilder, ClientGpt
import pickle


data = {}
header = ('\n ____              _________________              ____\n'
          '\n |                 ___| Request |___                 |\n',
          '\n ____              _________________              ____\n')


def draw():
    for line in header:
        print(line)


def save_processed_urls(processed_urls):
    with open("processed_urls.pkl", "wb") as file:
        pickle.dump(processed_urls,file)


def load_processed_urls():
    try:
        with open("processed_urls.pkl", "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return []
    

#Відкриття файлу url_list.txt: Список URL-адрес, з яких потрібно здійснювати парсинг, зчитується з файлу.
#Кожна URL-адреса зберігається у списку urls.
with open("files/url_list.txt", 'r') as f:
    urls = f.read().splitlines()

processed_urls = load_processed_urls()

#Цикл обробки для кожного URL
for url in urls:
    data = Parser(url).parse()

    director = Director()

    gpt = ClientGpt(data)
    builder = ProductBuilder(data)

    director.gpt = gpt
    director.builder = builder

    director.build_product()
    product = builder.product

    print(product.body)
    processed_urls.append(url)
    save_processed_urls(processed_urls)

    break
