import requests, json, csv, re, logging
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logging.basicConfig(level=logging.ERROR)

def clean_price(price_text):
    return re.sub(r'[^\d]+', '', price_text.split(',')[0])  # Видалити все, окрім цифр та крапки
# Попередньо визначені функції парсингу
def parse_name(soup):
    return soup.find(attrs={"data-qaid": "product_name"}).get_text(strip=True)

def parse_sku(soup):
    return soup.find(attrs={"data-qaid": "product_code"}).get_text(strip=True)

def parse_price(soup):
    price_text = soup.find(attrs={"data-qaid": "product_price"}).get_text(strip=True)
    return clean_price(price_text)

def parse_description(soup):
    return str(soup.find(attrs={"data-qaid": "product_description"}))

def parse_specifications(soup):
    specifications = {}
    table = soup.find('table', class_='b-product-info')
    for tr in table.find_all('tr'):
        cells = tr.find_all('td')
        if len(cells) == 2:
            specifications[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
    return specifications

def extract_product_id(url):
    # Extract the product ID from the URL
    prefix = "https://mixmol.com.ua/ua/p"
    suffix_position = url.find("-", len(prefix))
    if suffix_position != -1:
        product_id = url[len(prefix):suffix_position]
        return product_id
    return None

def fetch_product_images(product_id, session):
    """
    Fetch product images using a persistent session and caching.
    """
    url = "https://mixmol.com.ua/ua/graphql"
    headers = {
        "Content-Type": "application/json",
    }
    body = {
        "operationName": "productImagesQuery",
        "variables": {"productId": int(product_id)},
        "query": """
            query productImagesQuery($productId: Int!) {
                product(id: $productId) {
                    viewImages: images(width: 640, height: 640)
                }
            }
        """
    }
    try:
        response = session.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        image_urls = [image['url'] for image in data['data']['product']['viewImages']]
        return image_urls
    except HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')  # HTTP error response
    except Exception as err:
        logging.error(f'Other error occurred: {err}')  # Other errors
    return []

def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Основна функції парсингу та запису
def fetch_and_parse_from_file(file_path):
    all_data = {}
    with open(file_path, 'r') as f:
        urls = f.read().splitlines()
    
    session = requests_retry_session()
    try:
        for url in urls:
            response = session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            product_id = extract_product_id(url)
            if product_id:
                image_urls = fetch_product_images(product_id, session)
            else:
                image_urls = []
            data = {
                "name": parse_name(soup),
                "sku": parse_sku(soup),
                "price": parse_price(soup),
                "description": parse_description(soup),
                "specifications": parse_specifications(soup),
                "images": image_urls
            }
            print(data['specifications'])
            all_data[url] = data

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {str(e)}", exc_info=True)
        all_data[url] = {"Error": str(e)}
    finally:
        session.close()

        return all_data

def save_data_to_csv(data, output_file):
    # Determine the header based on keys of the first item in data
    if data:
        headers = list(data[next(iter(data))].keys())
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(["URL"] + headers)
            # Write data rows
            for url, attributes in data.items():
                row = [url]
                for header in headers:
                    if header == "images" and isinstance(attributes.get(header), list):
                        # Join image URLs into a single string separated by commas
                        row.append(','.join(attributes.get(header)))
                    else:
                        row.append(attributes.get(header, ''))
                writer.writerow(row)

def fetch_parse_and_save(file_path="files/url_list.txt", output_csv="files/output_data.csv"):
    all_data = fetch_and_parse_from_file(file_path)
    # Save all the collected data to a CSV file
    save_data_to_csv(all_data, output_csv)
    return(all_data)

if __name__ == "__main__":
    fetch_parse_and_save("files/url_list.txt", "files/output_data.csv")
