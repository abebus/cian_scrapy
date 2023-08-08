# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from dataclasses import dataclass
'''
Паук должен уметь собирать следующие данные из каждого объявления:
- Заголовок объявления (количество комнат, площадь (общая и/или жилая), этаж и количество этажей в здании);
- Адрес;
- Цена;
- Ссылка на объявление;
- Номер страницы, на которой находится объявление.
'''
@dataclass
class CianItem:
    # define the fields for your item here like:
    url: str
    addr: str
    price: int
    page: int
    header: str
    description: str
