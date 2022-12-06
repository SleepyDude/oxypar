# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
from itemloaders.processors import TakeFirst, MapCompose

# process EACH item in list if it's MapCompose
# process LIST if it's Compose
def process_protocol(protocols):
    protocols = [pro.lower() for pro in protocols]
    if 'https' in protocols or 'socks4' in protocols or 'socks5' in protocols:
        return ['http', 'https']
    else:
        return ['http']
    
def lower_protocol(protocol):
    return protocol.lower()


class ProxyItem(scrapy.Item):
    ip = Field(
        output_processor=TakeFirst()
    )
    port = Field(
        output_processor=TakeFirst()
    )
    protocols = Field(
        input_processor=(MapCompose(lower_protocol))
    )
    https = Field(
        output_processor=TakeFirst()
    )
    cc = Field(
        output_processor=TakeFirst()
    )
    country = Field(
        output_processor=TakeFirst()
    )
    isanon = Field(
        output_processor=TakeFirst()
    )
    google_pass = Field(
        output_processor=TakeFirst()
    )
    source = Field(
        output_processor=TakeFirst()
    )
    ping = Field(
        output_processor=TakeFirst()
    )
