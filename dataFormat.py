from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Text
from openai import AsyncOpenAI
import json
import logging
import re

from api_config import GPT_API, get_wc_api
from gpt_data import PromptData

logging.basicConfig(level=logging.ERROR)


class CallMethods:
    def __init__(self, data, call):
        self._name = data["name"]
        self._sku = data["sku"]
        self._description = data["description"]
        self._images = data["images"]
        self._specifications = ["specifications"]
        self.call = call

    async def get_name(self):
        user_prompt = f'''Название на украинском: "{self._name}"
    {PromptData.name_prompt}'''
        system_prompt = '''Ты переводчик текста топ уровня, твоя задача переводить текст для товаров на русский якзык. В ответе не пиши ничего лишнего кроме результата работы'''
        return await self.call(system_prompt, user_prompt)

    async def get_description(self):
        user_prompt = f"{PromptData.icp} {PromptData.description_prompt} {self._description}"
        system_prompt = '''Ты Front-end специалист топ уровня, твоя задача редактирование описания товаров в формате html. Ты внимательно относишься к структуре DOM и следуешь стандартам разметки. В ответе не пиши ничего лишнего кроме результата работы в формате html!. Не пиши "```html" в ответе, ответ должен быть на русском языке!.'''
        return re.sub('\n', '', await self.call(system_prompt, user_prompt))

    async def get_h2(self):
        user_prompt = f'''Описание "{self._description}" {PromptData.h2_prompt}'''
        system_prompt = '''Ты Front-end специалист топ уровня, твоя задача редактирование описания товаров в формате html. Ти внимателено относишся к структуре DOM, количеству символов и следуешь стандартам разметки. В ответе не пиши ничего лишнего кроме результата работы в формате html. Не пиши "```html" в ответе, ответ должен быть на русском языке!'''
        return await self.call(system_prompt, user_prompt)

    async def get_faq(self):
        user_prompt = f'''{PromptData.icp}
    Информация о товаре: {self._description}
    {PromptData.faq_prompt}
    {PromptData.faq}'''
        system_prompt = '''Ты Front-end специалист топ уровня, твоя задача редактирование описания товаров в формате html. Ти внимателено относишся к структуре DOM, количеству символов и следуешь стандартам разметки. В ответе не пиши ничего лишнего кроме результата работы в формате html. Не пиши "```html" в ответе, ответ должен быть на русском языке!'''
        return re.sub('\n', '', await self.call(system_prompt, user_prompt))

    async def get_other(self):
        user_prompt: str = f'''Описание: {self._description}
    {PromptData.other_data_prompt}'''
        system_prompt = '''Ты SEO специалист топ уровня, твоя задача писать продающий SEO оптимизированый текст для товаров. Ти внимателено относишся к количеству символов и следуешь стандартам SEO. В ответе не пиши ничего лишнего кроме результата работы он должен быть прагматичным и содержательным, и не должен звучать как реклама, ответ должен быть исключительно на русском языке'''
        return await self.call(system_prompt, user_prompt)

    async def get_specifications(self):
        user_prompt = f'Описание товара: "{self._description}."\nХарактеристики на украинском: {self._specifications}.\nФото товара: {self._images[0]}\n{PromptData.specifications_prompt}.'
        system_prompt = '''Ты менеджер онлайн магазина, твоя задача собрать характеристику о товаре на основе имеющиеся информации, перевести на русский язык, и заполнить список по примеру. В ответе не пиши ничего лишнего кроме результата работы в формате json, не пиши "```json```"'''
        return await self.call(system_prompt, user_prompt)


class ClientGpt:
    def __init__(self, data):
        self.methods = CallMethods(data, self.call)
        self._client = AsyncOpenAI(api_key=GPT_API)

    async def call(self, system_prompt, user_prompt):
        try:
            completion = await self._client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_prompt}]
            )
            response = completion.choices[0].message.content
            return response
        except Exception as e:
            logging.error(f"API call failed: {e}")
            return None

    async def generate(self):
        name = await self.methods.get_name()
        description = await self.methods.get_description()
        h2 = await self.methods.get_h2()
        faq = await self.methods.get_faq()
        other = await self.methods.get_other()
        attributes = await self.methods.get_specifications()
        return name, description, h2, faq, other, attributes


class Builder(ABC):

    @property
    @abstractmethod
    def product(self) -> None:
        pass

    @abstractmethod
    def set_name(self) -> None:
        pass

    @abstractmethod
    def set_sku(self) -> None:
        pass

    @abstractmethod
    def set_price(self) -> None:
        pass

    @abstractmethod
    def set_short_description(self) -> None:
        pass

    @abstractmethod
    def set_meta_data(self) -> None:
        pass

    @abstractmethod
    def set_description(self) -> None:
        pass

    @abstractmethod
    def set_attributes(self) -> None:
        pass

    @abstractmethod
    def set_images(self) -> None:
        pass

    @abstractmethod
    def set_categories(self) -> None:
        pass

    @abstractmethod
    def set_type(self) -> None:
        pass

    @abstractmethod
    def set_status(self) -> None:
        pass


class ProductBuilder(Builder):

    def __init__(self, data) -> None:
        self._product = None
        self.reset()
        self.data = data

    def reset(self) -> None:
        self._product = Product()

    @property
    def product(self) -> Product:
        product = self._product
        self.reset()
        return product

    def set_name(self, name=None):
        self._product.add(key='name', value=name)

    def set_sku(self, sku=None):
        self._product.add(key='sku', value=sku)

    def set_price(self, price=None):
        self._product.add(key='regular_price', value=price)

    def set_short_description(self, short_description=None):
        self._product.add(key='short_description', value=short_description)

    def set_meta_data(self, meta_data=None):
        self._product.add(key='meta_data', value=meta_data)

    def set_description(self, description=None):
        self._product.add(key='description', value=description)

    def set_attributes(self, specifications=None):
        self._product.add(key='attributes', value=specifications)

    def set_images(self, images=None):
        self._product.add(key='images', value=images)

    def set_categories(self, categories=None):
        if categories is None:
            categories = [{'id': 61}]
        self._product.add(key='categories', value=categories)

    def set_type(self, type="simple"):
        self._product.add(key='type', value=type)

    def set_status(self, status="draft"):
        self._product.add(key='status', value=status)


class Product:
    def __init__(self) -> None:
        self.body = {}
        self.HTTP_CREATED = 201
        self.wcapi = get_wc_api()

    def add(self, key, value) -> None:
        if key == "images":
            self.body[key] = [{'src': img} for img in value]
        elif key == "attributes":
            self.body[key] = json.loads(value)
        else:
            self.body[key] = value

    def get(self, key: Text):
        return self.body[key]

    def post(self):
        try:
            response = self.wcapi.post("products", self.body)
            if response.status_code == self.HTTP_CREATED:
                return response.json()
            else:
                # Log error or re-raise with additional context
                return response.raise_for_status()
        except Exception as e:
            # Log the exception with traceback
            logging.error(f'''Failed to post product: {self.body['name']}\nErr: {e}''', exc_info=True)


class Director:
    def __init__(self) -> None:
        self._builder = None
        self._gpt = None

    @property
    def builder(self) -> Builder:
        return self._builder

    @property
    def gpt(self) -> ClientGpt:
        return self._gpt

    @builder.setter
    def builder(self, builder: ProductBuilder) -> None:
        self._builder = builder

    @gpt.setter
    def gpt(self, gpt: ClientGpt) -> None:
        self._gpt = gpt

    async def build_product(self) -> None:
        name, description, h2, faq, other, attributes = await self._gpt.generate()
        description = f'''{h2}{description}<h3>Часто задаваемые вопросы</h3>{faq}'''
        meta_title, meta_description, short_description = process_other_data(other)
        meta_data = get_metadata(meta_title, meta_description)
        self.builder.set_name(name)
        self.builder.set_sku(self.builder.data['sku'])
        self.builder.set_price(self.builder.data['price'])
        self.builder.set_description(description)
        self.builder.set_attributes(attributes)
        self.builder.set_short_description(short_description)
        self.builder.set_meta_data(meta_data)
        self.builder.set_images(self.builder.data['images'])
        self.builder.set_categories()
        self.builder.set_type()
        self.builder.set_status()


def get_metadata(meta_title, meta_description):
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
            "key": "_yoast_wpseo_title",
            "value": meta_title
        },
        {
            "key": "_yoast_wpseo_metadesc",
            "value": meta_description
        }]
    return meta_data


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
