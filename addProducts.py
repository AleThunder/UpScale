from parseProductsData import fetch_parse_and_save
from api_config import GPT_API, get_wc_api
from dataFormat import dataFormat
from woocommerce import API
import csv, logging
HTTP_CREATED = 201
consoleDevider = '''\n__________________________________________________________\n'''

logging.basicConfig(level=logging.ERROR)
wcapi = get_wc_api()

products_data = fetch_parse_and_save()
dataProducts = dataFormat(products_data)

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
        'images': [{'src': img} for img in product['Images']]
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
