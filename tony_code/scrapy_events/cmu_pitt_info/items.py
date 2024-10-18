# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CmuPittInfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class EventItem(scrapy.Item):
    id = scrapy.Field()
    category = scrapy.Field()
    event_name = scrapy.Field()
    start_month = scrapy.Field()
    start_day = scrapy.Field()
    start_year = scrapy.Field()
    end_month = scrapy.Field()
    end_day = scrapy.Field()
    end_year = scrapy.Field()
    start_time = scrapy.Field()
    end_time = scrapy.Field()
    content = scrapy.Field()
    revenue = scrapy.Field()
    location = scrapy.Field()
    pass
