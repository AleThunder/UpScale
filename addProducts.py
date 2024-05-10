from api_config import GPT_API, get_wc_api
from dataFormat import dataFormat
from woocommerce import API
import csv, logging, json
HTTP_CREATED = 201

logging.basicConfig(level=logging.ERROR)
wcapi = get_wc_api()

#Ця функція відповідає за надсилання даних про товари до WooCommerce за допомогою POST-запиту.
#Вона використовує об'єкт API, створений в get_wc_api() для взаємодії з WooCommerce.
def post_product(product_data):
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