from api_config import GPT_API
from openai import OpenAI
from gpt_data import icp, description_prompt, h2_prompt, faq, faq_prompt, other_data_prompt, name_prompt, specifications_prompt
import json, csv, logging

logging.basicConfig(level=logging.ERROR)

product = {'name': 'Перукарське крісло HEKTOR BH-3208 Black', 'sku': 'BH-3208/127', 'price': '13495', 'description': '<div class="b-user-content" data-qaid="product_description"><div class="resetcss">\n<div class="resetcss">\n<div class="resetcss">\n<p><strong>Перукарське крісло HEKTOR BH-3208 Black чорне</strong><br/>\nПропонуємо вам перукарське крісло, що поєднує в собі оригінальний стиль та функціональні рішення.<br/>\nОббивка виготовлена з високоякісної неорганічної шкіри. Модель представлена в декількох модних кольорах. Ви обов\'язково підберете колір, який найкраще підійде до стилю інтер\'єру вашого салону. Перукарське крісло HEKTOR BH-3808 забезпечує комфорт та ергономічність роботи.</p>\n<p><strong>Особливості:</strong></p>\n<ul>\n<li>Гідравлічне регулювання висоти.</li>\n<li>Рухлива спинка, що регулюється.</li>\n<li>Знімний підголівник.</li>\n<li>Хромова база.</li>\n<li>Оббивка виготовлена з високоякісної екологічної шкіри.</li>\n</ul>\n<p><strong>Габаритні розміри:</strong></p>\n<ul>\n<li>ширина сидіння: 51 см,</li>\n<li>ширина сидіння з підлокітниками: 63 см,</li>\n<li>глибина сидіння: 48 см,</li>\n<li>висота спинки сидіння: 46 см,</li>\n<li>висота спинки сидіння з регульованим підголівником: мін. 46 см, макс 65 см,</li>\n<li>висота крісла мін: 52 см,</li>\n<li>максимальна висота крісла: 66 см,</li>\n<li>діагональ основи: 60 см,</li>\n<li>вага крісла: 35 кг,</li>\n</ul>\n<p><strong>Розміри упаковки</strong>: 65x64x59см,</p>\n<p>Гарантія: 12 місяців.</p>\n</div>\n</div>\n<p>\xa0</p>\n</div></div>', 'specifications': {'Країна виробник': 'Польща', 'Колір': 'Чорний'}, 'images': ['https://images.prom.ua/5259770497_w640_h640_5259770497.jpg', 'https://images.prom.ua/5259770498_w640_h640_5259770498.jpg', 'https://images.prom.ua/5259770499_w640_h640_5259770499.jpg', 'https://images.prom.ua/5259770500_w640_h640_5259770500.jpg', 'https://images.prom.ua/5259770501_w640_h640_5259770501.jpg', 'https://images.prom.ua/5259770502_w640_h640_5259770502.jpg', 'https://images.prom.ua/5259770503_w640_h640_5259770503.jpg', 'https://images.prom.ua/5259770504_w640_h640_5259770504.jpg']}

#Ця функція використовує запит до API OpenAI для генерації HTML-опису товару, виходячи з поданого опису.
def get_description(description):
    user_prompt = f"{icp} {description_prompt} {description}"
    system_prompt = '''Ты Front-end специалист топ уровня, твоя задача редактирование описания товаров в формате html. Ти внимателено относишся к структуре DOM и следуешь стандартам разметки. В ответе не пиши ничего лишнего кроме результата работы в формате html!. Не пиши "```html" в ответе, ответ должен быть на русском языке!.'''
    return(call_openai(system_prompt, user_prompt))

#Генерує HTML-розділ (зазвичай заголовок другого рівня) для опису товару за допомогою OpenAI API.
def get_h2(description):
    user_prompt = f'''Описание "{description}" {h2_prompt}'''
    system_prompt = '''Ты Front-end специалист топ уровня, твоя задача редактирование описания товаров в формате html. Ти внимателено относишся к структуре DOM, количеству символов и следуешь стандартам разметки. В ответе не пиши ничего лишнего кроме результата работы в формате html. Не пиши "```html" в ответе, ответ должен быть на русском языке!'''
    return(call_openai(system_prompt, user_prompt))

#Створює FAQ розділ для товару, використовуючи зображення товару як контекст для запиту до OpenAI.
def get_faq(image):
    user_prompt = f'''{icp}
{faq}
Зображення товару: {image}
{faq_prompt}'''
    system_prompt = '''Ты Front-end специалист топ уровня, твоя задача редактирование описания товаров в формате html. Ти внимателено относишся к структуре DOM, количеству символов и следуешь стандартам разметки. В ответе не пиши ничего лишнего кроме результата работы в формате html. Не пиши "```html" в ответе, ответ должен быть на русском языке!'''
    return(call_openai(system_prompt, user_prompt))

#Отримує інші маркетингові або SEO оптимізовані тексти за допомогою опису товару.
def get_other(description):
    user_prompt = f'''Описание: {description}
{other_data_prompt}'''
    system_prompt = '''Ты SEO специалист топ уровня, твоя задача писать продающий SEO оптимизированый текст для товаров. Ти внимателено относишся к количеству символов и следуешь стандартам SEO. В ответе не пиши ничего лишнего кроме результата работы он должен быть прагматичным и содержательным, и не должен звучать как реклама, ответ должен быть на русском языке!'''
    return(call_openai(system_prompt, user_prompt))

#Перекладає назву товару з української на російську мову з використанням ключових слів.
def get_name(name):
    user_prompt = f'''Название на украинском: "{name}"
{name_prompt}'''
    system_prompt = '''Ты переводчик текста топ уровня, твоя задача переводить текст для товаров на русский якзык. В ответе не пиши ничего лишнего кроме результата работы'''
    return(call_openai(system_prompt, user_prompt))

#Формує характеристики товару у форматі JSON, використовуючи опис товару, його технічні характеристики та зображення.
def get_specifications(description, specifications, photo):
    user_prompt = f'''Описание товара: "{description}."
Характеристики на украинском: {specifications}.
Фото товара: {photo}

{specifications_prompt}.'''
    system_prompt = '''Ты менеджер онлайн магазина, твоя задача собрать характеристику о товаре на основе имеющиеся информации, перевести на русский язык, и заполнить список по примеру. В ответе не пиши ничего лишнего кроме результата работы в формате json, не пиши "```json
```"'''
    return(call_openai(system_prompt, user_prompt))

#Центральна функція, яка обробляє взаємодію з API OpenAI, використовуючи зазначені запити та відповіді.
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

#Основна функція, яка інтегрує всі вищезазначені функції для формування остаточної структури даних про товар, готових до експорту у форматі CSV або JSON.
def dataFormat(product):
    csv_data = {}
    
    raw_name = product['name']
    raw_description = product['description']
    raw_specifications = product['specifications']
    images = product['images']
    price = product['price']
    sku = product['sku']
    name = get_name(raw_name)
    description = get_description(raw_description)
    h2 = get_h2(description)
    faq = get_faq(images[0])
    other = get_other(description)
    specifications = get_specifications(description, raw_specifications, images[0])
    meta_title, meta_description, bullet_points = process_other_data(other)
    full_description = f'''{h2}\n{description}\n{faq}'''
    
    meta_data = [{
            "key": "yikes_woo_products_tabs",
            "value": [
                {
                    "title": "Доставка и оплата",
                    "id": "dostavka-i-oplata",
                    "content": "<div class='widget-title'>Доставка осуществляется с помощью курьерских служб:</div>\r\n<p>• Новая Почта • Delivery</p>\r\n<div class='widget-title'>Нова пошта</div>\r\n<p>При доставке товара компанией проводится обязательное страхование груза. Не забывайте проверять заказ при получении. После получения магазин не принимает претензии относительно внешнего вида и комплектации изделия. Бесплатная доставка от 1500 грн. в пределах Украины (бесплатная доставка не распространяется на мебель). При оформлении заказа на мебель до 3000 грн. необходимо внесение предоплаты в размере 300 грн. При оформлении заказа на мебель от 3000 грн. необходимо внесение предоплаты в размере 700 грн. Заказы, стоимостью товара до 200 грн., оформляются только по предоплате. Отправка заказов по Украине осуществляется транспортной компанией Новая Почта. Крупногабаритные товары (мебель) отправляются компаниями Новая Почта на грузовые отделения и 'Delivery'. Оформление заказов с отправкой в Почтоматы ПриватБанка только по предоплате.</p>\r\n<div class='widget-title'>Delivery</div>\r\n<p>Данный вид доставки рекомендуется для крупногабаритных товаров. При доставке товара транспортной компанией проводится обязательное страхование груза на полную стоимость товара. Не забывайте проверять внешний вид и комплектацию заказа, когда Вы получаете его в транспортной компании. После получения товара магазин не принимает претензии относительно внешнего вида и комплектации изделия.</p>\r\n<div class='widget-title'>Способы оплаты</div>\r\n<ul class='cs-delivery-info__list'>\r\n<li class='cs-delivery-info__item'><span class='cs-delivery-info__caption'><span class='cs-delivery-info__caption'>Наложенный платеж Оплата при получении наложенным платежом. Должны уведомить Вас, что Новая Почта кроме стоимости доставки берет еще комиссию за наложенный платеж 20 грн. + 2% от стоимости заказа. </span></span></li>\r\n<li><span class='cs-delivery-info__caption'>Карта ПриватБанка </span><span class='cs-delivery-info__comment h-pre-wrap'>Номер карты для оплаты мы сообщим вам в СМС или Viber после подтверждения и согласования заказа.</span></li>\r\n<li class='cs-delivery-info__item'><span class='cs-delivery-info__caption'>Безналичный расчет Оплата на расчетный счёт</span></li>\r\n</ul>"
                }
            ]
        },
        {
            "key":"_yoast_wpseo_title",
            "value":meta_title
        },
        {
            "key":"_yoast_wpseo_metadesc",
            "value":meta_description
        }]
    
    csv_data['name'] = name
    csv_data['type'] = 'simple'
    #csv_data['status'] = 'draft'
    csv_data['categories'] = [{'id': 61}]
    csv_data["meta_data"] = meta_data
    csv_data["description"] = description
    csv_data["short_description"] = bullet_points
    csv_data["images"] = [{'src': img} for img in images]
    csv_data['regular_price'] = price
    csv_data['sku'] = sku
    csv_data['attributes'] = json.loads(specifications)

    return csv_data

#Обробляє додаткові дані, такі як мета-заголовки та мета-описи, отримані з текстів, створених за допомогою API.
def process_other_data(other_data):
    # Split the input string into sections
    sections = other_data.split('#')

    # Extract meta title by removing the prefix "Мета заголовок:\n"
    meta_title = sections[0].replace(";", "").strip('"')
    # Extract meta description by removing the prefix "Мета описание:\n"
    meta_description = sections[1].replace(";", "").strip('"')
    # Process bullet points
    bullet_points = sections[2]

    # Return the extracted values
    return meta_title, meta_description, bullet_points

client = OpenAI(api_key=GPT_API)

#Функція для тестування всіх компонентів на прикладі реальних даних товару, інтегруючи їх в єдиний вихід.
def testing(products_data):
    raw_description = products_data['description']
    description = get_description(raw_description)
    print(get_description(raw_description))
    h2 = get_h2(description)
    faq = get_faq(products_data['images'][0])
    description = f'''{h2}\n{description}\n{faq}'''
    raw_spec = products_data['specifications']
    specif = get_specifications(description, raw_spec, products_data['images'][0])
    return(specif)