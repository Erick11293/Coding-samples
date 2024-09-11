# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ConsultaamigableItem(scrapy.Item):
    # define the fields for your item here like:
    data = scrapy.Field()
    detalle = scrapy.Field()
    url = scrapy.Field()
    hierarchy = scrapy.Field()
