# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item
from scrapy.loader import ItemLoader


class PartyResultItem(Item):
    year = Field()
    region = Field()
    county = Field()
    town = Field()
    district_no = Field()
    party_name = Field()
    n_votes = Field()


class PartyResultItemLoader(ItemLoader):
    pass


class DistrictItem(Item):
    district_no = Field()
    year = Field()
    region = Field()
    county = Field()
    town = Field()
    n_all_votes = Field()
