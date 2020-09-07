# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from elections.items import DistrictItem, PartyResultItem
from scrapy.exporters import CsvItemExporter


class ElectionsPipeline(object):

    def open_spider(self, spider):
        self.year_exporters = {}

    def close_spider(self, spider):
        self.district_exporter.finish_exporting()
        self.district_exporter.close()
        self.party_results_exporter.finish_exporting()
        self.party_results_exporter.close()

    def process_item(self, item, spider):
        year = item["year"]
        if year in self.year_exporters:
            exporter_d, exporter_p = self.year_exporters[year]
        else:
            file_d = open(f"districts_{year}.csv", "wb")
            file_p = open(f"parties_{year}.csv", "wb")
            exporter_d = CsvItemExporter(file_d)
            exporter_p = CsvItemExporter(file_p)
            self.year_exporters[year] = (exporter_d, exporter_p)

        if type(item) == DistrictItem:
            exporter_d.export_item(item)
        else:
            exporter_p.export_item(item)

        return item
