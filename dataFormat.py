from parseProductsData import fetch_parse_and_save
from api_config import GPT_API
from openai import OpenAI
from gpt_data import icp, description_prompt, h2_prompt, faq, faq_prompt, other_data_prompt, name_prompt, specifications_list, specifications_prompt
import csv, logging

logging.basicConfig(level=logging.ERROR)

def get_description(description):
    user_prompt = f"{icp} {description_prompt} {description}"
    system_prompt = '''Ты Front-end специалист топ уровня, твоя задача редактирование описания товаров в формате html. Ти внимателено относишся к структуре DOM и следуешь стандартам разметки. В ответе не пиши ничего лишнего кроме результата работы в формате html!. Не пиши "```html" в ответе, ответ должен быть на русском языке!.'''
    return(call_openai(system_prompt, user_prompt))

def get_h2(description):
    user_prompt = f'''Описание "{description}" {h2_prompt}'''
    system_prompt = '''Ты Front-end специалист топ уровня, твоя задача редактирование описания товаров в формате html. Ти внимателено относишся к структуре DOM, количеству символов и следуешь стандартам разметки. В ответе не пиши ничего лишнего кроме результата работы в формате html. Не пиши "```html" в ответе, ответ должен быть на русском языке!'''
    return(call_openai(system_prompt, user_prompt))

def get_faq(image):
    user_prompt = f'''{icp}
{faq}
Зображення товару: {image}
{faq_prompt}'''
    system_prompt = '''Ты Front-end специалист топ уровня, твоя задача редактирование описания товаров в формате html. Ти внимателено относишся к структуре DOM, количеству символов и следуешь стандартам разметки. В ответе не пиши ничего лишнего кроме результата работы в формате html. Не пиши "```html" в ответе, ответ должен быть на русском языке!'''
    return(call_openai(system_prompt, user_prompt))

def get_other(description):
    user_prompt = f'''Описание: {description}
{other_data_prompt}'''
    system_prompt = '''Ты SEO специалист топ уровня, твоя задача писать продающий SEO оптимизированый текст для товаров. Ти внимателено относишся к количеству символов и следуешь стандартам SEO. В ответе не пиши ничего лишнего кроме результата работы он должен быть прагматичным и содержательным, и не должен звучать как реклама, ответ должен быть на русском языке!'''
    return(call_openai(system_prompt, user_prompt))

def get_name(name):
    user_prompt = f'''Название на украинском: "{name}"
{name_prompt}'''
    system_prompt = '''Ты переводчик текста топ уровня, твоя задача переводить текст для товаров на русский якзык. В ответе не пиши ничего лишнего кроме результата работы'''
    return(call_openai(system_prompt, user_prompt))

def get_specifications(description, specifications):
    user_prompt = f'''Описание товара: "{description}."
Характеристики на украинском: {specifications}.
Список необходимых характеристик: {specifications_list}.
{specifications_prompt}.'''
    system_prompt = '''Ты менеджер онлайн магазина, твоя задача собрать характеристику о товаре на основе имеющиеся информации и перевести на русский язык. В ответе не пиши ничего лишнего кроме результата работы в формате json, не пиши "```json
```"'''
    return(call_openai(system_prompt, user_prompt))

def call_openai(system_prompt, user_prompt):
    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"API call failed: {e}")
        return None

def dataFormat(products_data):
    csv_data = []
    for tag in products_data:
        raw_name = products_data[tag]['name']
        raw_description = products_data[tag]['description']
        raw_specifications = products_data[tag]['specifications']
        images = products_data[tag]['images']
        price = products_data[tag]['price']
        sku = products_data[tag]['sku']
        
        name = get_name(raw_name)
        description = get_description(raw_description)
        h2 = get_h2(description)
        faq = get_faq(images[0])
        other = get_other(description)
        specifications = get_specifications(description, raw_specifications)
        meta_title, meta_description, bullet_points = process_other_data(other)
        
        full_description = f'''{h2}\n{description}\n{faq}'''
        
        csv_data.append({
            "Name": name,
            "Description": full_description,
            "MetaTitle": meta_title,
            "MetaDescription": meta_description,
            "BulletPoints": bullet_points,
            "Images": images,
            "Price": price,
            "SKU": sku,
            "Specifications": specifications
        })

    csv_file_path = 'files/products.csv'

    fieldnames = ['Name', 'Description', 'MetaTitle', 'MetaDescription', 'BulletPoints', 'Images', 'Price', 'SKU', 'Specifications']

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    return csv_data

def process_other_data(other_data):
    # Split the input string into sections
    sections = other_data.split('#')

    # Extract meta title by removing the prefix "Мета заголовок:\n"
    meta_title = sections[0].replace(";", "").strip('"')
    # Extract meta description by removing the prefix "Мета описание:\n"
    meta_description = sections[1].replace(";", "").strip('"')
    # Process bullet points
    bullet_points_raw = sections[2].replace("Список характеристик и особенностей:", "").strip('"')
    bullet_points_raw = sections[2].replace("\n-", "\n").strip('"')
    bullet_points_lines = bullet_points_raw.split('\n')
    bullet_points = '\n'.join(line for line in bullet_points_lines if ':' not in line)

    # Return the extracted values
    return meta_title, meta_description, bullet_points

client = OpenAI(api_key=GPT_API)
products_data = fetch_parse_and_save()
#dataProducts = dataFormat(products_data)

def testing(tag = "https://mixmol.com.ua/ua/p2060998074-parikmaherskoe-kreslo-olaf.html"):
    #Підготовка даних з products_data необхідних для тестування get_specifications()
    raw_description = products_data[tag]['description']
    description = get_description(raw_description)
    h2 = get_h2(description)
    faq = get_faq(products_data[tag]['images'][0])
    description = f'''{h2}\n{description}\n{faq}'''
    #тест функціїї get_specifications для обробки та створення нових характеристик.   
    raw_spec = products_data[tag]['specifications']
    specif = get_specifications(description, raw_spec)
    return(f'''Характеристики:
{specif}''')

print(testing())
