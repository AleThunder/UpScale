from parseData import Parser
from dataFormat import Director, ProductBuilder, ClientGpt

data = {}
header = ('\n ____              _________________              ____\n'
          '\n |                 ___| Request |___                 |\n',
          '\n ____              _________________              ____\n')


def draw():
    for line in header:
        print(line)


#Відкриття файлу url_list.txt: Список URL-адрес, з яких потрібно здійснювати парсинг, зчитується з файлу.
#Кожна URL-адреса зберігається у списку urls.
with open("files/url_list.txt", 'r') as f:
    urls = f.read().splitlines()

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
    break
