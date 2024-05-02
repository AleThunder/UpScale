from parseProductsData import fetch_parse_and_save
from api_config import GPT_API
from openai import OpenAI
from gpt_data import icp, description_prompt, h2_prompt, faq, faq_prompt, other_data_prompt, name_prompt, specifications_list, specifications_prompt
import csv, logging

description = '''<h2>Перукарское кресло HEKTOR BH-3208 для профессионалов</h2>
<p>Откройте для себя превосходство и комфорт с перукарским креслом HEKTOR BH-3208 Black, которое является идеальным выбором для барбершопов в крупных и средних городах. Это кресло не только удобно и функционально, но и внешне привлекательно, что делает его отличным дополнением к стильному интерьеру вашего салона.</p>

<p>Кресло HEKTOR BH-3208 сочетает в себе изысканный дизайн и высокое качество. Обивка изготовлена из премиальной экологической кожи, что обеспечивает легкость в уходе и долговечность. Идеально подходит для мастеров, стремящихся создать респектабельную и комфортную атмосферу для своих клиентов.</p>

<p>Особенности кресла включают:</p>
<ul>
<li>Гидравлическое регулирование высоты для удобства и гибкости в работе;</li>
<li>Регулируемая спинка и съемный подголовник, что позволяет адаптировать кресло для различных процедур;</li>
<li>Элегантная хромированная основа, добавляющая изысканности.</li>
<li>Качественная обивка из экологической кожи.</li>
</ul>

<p>Размеры кресла поддерживают высокое качество работы барберов:
<ul>
<li>ширина сиденья: 51 см;</li>
<li>ширина сиденья с подлокотниками: 63 см;</li>
<li>глубина сиденья: 48 см;</li>
<li>высота спинки сиденья: 46 см;</li>
<li>высота кресла регулируется от 52 до 66 см;</li>
<li>диагональ основания: 60 см;</li>
<li>вес кресла: 35 кг.</li>
</ul></p>

<p>Гарантия на кресло составляет 12 месяцев, подтверждая его надежность и долговечность. Характеристики и размеры кресла делают его одним из лучших выборов для профессионалов, которые ценят качество и комфорт как для себя, так и для своих клиентов.</p>

<p>Выбор кресла HEKTOR BH-3208 Black станет залогом уверенности в качестве и профессионализме вашего барбершопа. Удобство, функциональность и стиль — три составляющие успешной работы и удовлетворенности клиентов. Приобретая это кресло, вы инвестируете не только в интерьер вашего салона, но и в удобство и положительные эмоции ваших клиентов.</p>
<div itemscope itemtype="https://schema.org/FAQPage">
    <div itemprop="mainEntity" itemscope itemtype="https://schema.org/Question">
        <strong itemprop="name">Как приобрести парикмахерское кресло через ваш сайт?</strong>
        <div itemprop="acceptedAnswer" itemscope itemtype="https://schema.org/Answer">
            <div itemprop="text">
                Для заказа кресла для вашего барбершопа воспользуйтесь функцией добавления в корзину на нашем сайте, позвоните по номеру в разделе контакты или начните диалог через онлайн-чат с нашими консультантами для получения помощи.
            </div>
        </div>
    </div>
    <div itemprop="mainEntity" itemscope itemtype="https://schema.org/Question">
        <strong itemprop="name">Предоставляется ли гарантия на парикмахерское кресло?</strong>
        <div itemprop="acceptedAnswer" itemscope itemtype="https://schema.org/Answer">
            <div itemprop="text">
                Каждое кресло для барбершопа сопровождается 12-месячной гарантией, подтверждающей его высокое качество и надежность.
            </div>
        </div>
    </div>
    <div itemprop="mainEntity" itemscope itemtype="https://schema.org/Question">
        <strong itemprop="name">Является ли парикмахерское кресло Stig Black оригинальным продуктом?</strong>
        <div itemprop="acceptedAnswer" itemscope itemtype="https://schema.org/Answer">
            <div itemprop="text">
                Да, мы предоставляем исключительно оригинальные кресла Stig Black, которые идут с подтверждением подлинности и гарантией от производителя.
            </div>
        </div>
    </div>
    <div itemprop="mainEntity" itemscope itemtype="https://schema.org/Question">
        <strong itemprop="name">В чем различие между пневматическим и гидравлическим механизмами в креслах?</strong>
        <div itemprop="acceptedAnswer" itemscope itemtype="https://schema.org/Answer">
            <div itemprop="text">
                Пневматический механизм кресла требует, чтобы клиент вставал для его регулирования, в то время как гидравлический механизм позволяет изменять высоту кресла без потребности подниматься клиенту, обеспечивая бесперебойность и удобство во время стрижки или других процедур.
            </div>
        </div>
    </div>
    <div itemprop="mainEntity" itemscope itemtype="https://schema.org/Question">
        <strong itemprop="name">Предоставляете ли вы скидки при покупке множества кресел Stig Black?</strong>
        <div itemprop="acceptedAnswer" itemscope itemtype="https://schema.org/Answer">
            <div itemprop="text">
                Да, мы предлагаем специальные скидки при покупке двух и более кресел Stig Black, а также при оформлении комплексного заказа.
            </div>
        </div>
    </div>
    <div itemprop="mainEntity" itemscope itemtype="https://schema.org/Question">
        <strong itemprop="name">Как осуществлять уход за креслом Stig Black для продления его срока службы?</strong>
        <div itemprop="acceptedAnswer" itemscope itemtype="https://schema.org/Answer">
            <div itemprop="text">
                Для обеспечения долговечности кресла Stig Black рекомендуется регулярно очищать его используя мягкие чистящие средства и избегать применения абразивных материалов, а также регулярно проверять все механизмы на предмет износа.
            </div>
        </div>
    </div>
    <div itemprop="mainEntity" itemscope itemtype="https://schema.org/Question">
        <strong itemprop="name">Можно ли отрегулировать высоту подножки на кресле Stig Black?</strong>
        <div itemprop="acceptedAnswer" itemscope itemtype="https://schema.org/Answer">
            <div itemprop="text">
                Да, подножка кресла Stig Black оснащена регулируемым механизмом, который позволяет настраивать ее высоту в соответствии с ростом и предпочтениями клиента.
            </div
'''

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
        print(get_specifications(description, raw_specifications))
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
            "SKU": sku
        })

    csv_file_path = 'files/products.csv'

    fieldnames = ['Name', 'Description', 'MetaTitle', 'MetaDescription', 'BulletPoints', 'Images', 'Price', 'SKU']

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    return csv_data

def process_other_data(other_data):
    # Split the input string into sections
    sections = other_data.split('#')

    # Extract meta title by removing the prefix "Мета заголовок:\n"
#    meta_title = sections[0].replace("Мета заголовок:", "").strip('"')
    meta_title = sections[0].replace(";", "").strip('"')
    # Extract meta description by removing the prefix "Мета описание:\n"
#    meta_description = sections[1].replace("Мета описание:", "").strip('"')
    meta_description = sections[1].replace(";", "").strip('"')
    # Process bullet points
    bullet_points_raw = sections[2].replace("Список характеристик и особенностей:", "").strip('"')
    bullet_points_raw = sections[2].replace("\n-", "\n").strip('"')
    bullet_points_lines = bullet_points_raw.split('\n')
    bullet_points = '\n'.join(line for line in bullet_points_lines if ':' not in line)

    # Return the extracted values
    return meta_title, meta_description, bullet_points

client = OpenAI(api_key=GPT_API)
tag = "https://mixmol.com.ua/ua/p2060998074-parikmaherskoe-kreslo-olaf.html"
products_data = fetch_parse_and_save()
try:
    specifications = products_data[tag]['specifications']
    print(get_specifications(description, specifications))
except Exception as e:
    print(f'''
{products_data}
----------Error-----------
{e}
''')
#
#products_data = fetch_parse_and_save()
#dataProducts = dataFormat(products_data)
#
#print(dataProducts)
