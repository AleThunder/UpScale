from parseData import parse
from dataFormat import dataFormat
from addProducts import post_product

data = {}
consoleDevider = '''\n__________________________________________________________\n'''
deviderConsole = '''\n__|         |        |_| Request |_|          |        |__\n'''

#Відкриття файлу url_list.txt: Список URL-адрес, з яких потрібно здійснювати парсинг, зчитується з файлу.
#Кожна URL-адреса зберігається у списку urls.
with open("files/url_list.txt", 'r') as f:
    urls = f.read().splitlines()
    
#Цикл обробки для кожного URL
for url in urls:
    #Парсинг: За допомогою функції parse(url) з модуля parseData.py здійснюється парсинг інформації з кожної URL.
    data[url] = parse(url) #Результат зберігається у словнику data з URL як ключем.
    
    #Форматування даних: Викликається dataFormat(data[url]) для перетворення зібраних даних у формат, придатний для додавання через API
    product = dataFormat(data[url])
    
    #Додавання товару: Викликається post_product(product), яка намагається додати сформований товар до магазину.
    response = post_product(product)
    
    #Відповідь від сервера друкується у консоль.
    print(response)
    print(consoleDevider)
    
#Друкування усіх даних: Після завершення обробки всіх URL-адрес в консоль друкується зібрані дані.
print(data)