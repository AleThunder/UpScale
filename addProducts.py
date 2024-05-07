from parseProductsData import fetch_parse_and_save
from api_config import GPT_API, get_wc_api
from dataFormat import dataFormat
from woocommerce import API
import csv, logging, json
HTTP_CREATED = 201
consoleDevider = '''\n__________________________________________________________\n'''

logging.basicConfig(level=logging.ERROR)
wcapi = get_wc_api()

products_data = fetch_parse_and_save()
dataProducts = dataFormat(products_data)
meta_data = [{
    "key": "yikes_woo_products_tabs",
    "value": [
        {
            "title": "Доставка и оплата",
            "id": "dostavka-i-oplata",
            "content": "<div class='widget-title'>Доставка осуществляется с помощью курьерских служб:</div>\r\n<p>• Новая Почта • Delivery</p>\r\n<div class='widget-title'>Нова пошта</div>\r\n<p>При доставке товара компанией проводится обязательное страхование груза. Не забывайте проверять заказ при получении. После получения магазин не принимает претензии относительно внешнего вида и комплектации изделия. Бесплатная доставка от 1500 грн. в пределах Украины (бесплатная доставка не распространяется на мебель). При оформлении заказа на мебель до 3000 грн. необходимо внесение предоплаты в размере 300 грн. При оформлении заказа на мебель от 3000 грн. необходимо внесение предоплаты в размере 700 грн. Заказы, стоимостью товара до 200 грн., оформляются только по предоплате. Отправка заказов по Украине осуществляется транспортной компанией Новая Почта. Крупногабаритные товары (мебель) отправляются компаниями Новая Почта на грузовые отделения и 'Delivery'. Оформление заказов с отправкой в Почтоматы ПриватБанка только по предоплате.</p>\r\n<div class='widget-title'>Delivery</div>\r\n<p>Данный вид доставки рекомендуется для крупногабаритных товаров. При доставке товара транспортной компанией проводится обязательное страхование груза на полную стоимость товара. Не забывайте проверять внешний вид и комплектацию заказа, когда Вы получаете его в транспортной компании. После получения товара магазин не принимает претензии относительно внешнего вида и комплектации изделия.</p>\r\n<div class='widget-title'>Способы оплаты</div>\r\n<ul class='cs-delivery-info__list'>\r\n<li class='cs-delivery-info__item'><span class='cs-delivery-info__caption'><span class='cs-delivery-info__caption'>Наложенный платеж Оплата при получении наложенным платежом. Должны уведомить Вас, что Новая Почта кроме стоимости доставки берет еще комиссию за наложенный платеж 20 грн. + 2% от стоимости заказа. </span></span></li>\r\n<li><span class='cs-delivery-info__caption'>Карта ПриватБанка </span><span class='cs-delivery-info__comment h-pre-wrap'>Номер карты для оплаты мы сообщим вам в СМС или Viber после подтверждения и согласования заказа.</span></li>\r\n<li class='cs-delivery-info__item'><span class='cs-delivery-info__caption'>Безналичный расчет Оплата на расчетный счёт</span></li>\r\n</ul>"
        }
    ]
}]
            
#print(dataProducts)

def create_product_data(product):
    return {
        'name' : product['Name'],
        'type' : 'simple',
        'status': 'draft',
        'sku' : product['SKU'],   
        'regular_price' : product['Price'],
        'description' : product['Description'],
        'short_description' : product['BulletPoints'],
        'categories': [{'id': 61}],
        'attributes': json.loads(product['Specifications']),
        'images': [{'src': img} for img in product['Images']],
        'meta_data' : meta_data
    }

def post_product_to_wc(product_data):
    try:
        response = wcapi.post("products", product_data)
        if response.status_code == HTTP_CREATED:
            return response.json()
        else:
            # Log error or re-raise with additional context
            response.raise_for_status()
    except Exception as e:
        # Log the exception with traceback
        logging.error(f'''Failed to post product: {product_data['name']}\nErr: {e}''', exc_info=True)

for product in dataProducts:

    data = create_product_data(product)
    print(data)
    print(consoleDevider)
    
    response = post_product_to_wc(data)
    print(response)
    print(consoleDevider)
