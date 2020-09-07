import re
import scrapy

from requests_html import HTML
from scrapy import Request
from scrapy.linkextractor import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import *


class ElectionsSpider(CrawlSpider):
    name = "elections"
    start_urls = [
        "https://volby.cz/pls/ps2017nss/ps?xjazyk=CZ",
        "https://volby.cz/pls/ps2013/ps",
        "https://volby.cz/pls/ps2010/ps",
    ]
    allowed_domains = ["volby.cz"]

    rules = [
        Rule(LinkExtractor(allow=r"ps3.*", restrict_css="div#tlacitka > ul > li")),
        Rule(LinkExtractor(restrict_css="table.table > tr > td:nth-of-type(4)")),
        Rule(
            LinkExtractor(restrict_css="table.table > tr > td:nth-of-type(3)"),
            callback="parse_town",
        ),
    ]

    def parse_town(self, response):
        html = HTML(html=response.body, default_encoding="ISO-8859-2")
        is_results = html.find("h2", containing="výběr okrsku") == []

        if is_results:
            results = self.parse_district(response)
            for r in results:
                yield r

        else:
            links = LinkExtractor(restrict_css="table.table > tr > td").extract_links(
                response
            )
            for l in links:
                yield Request(l.url, callback=self.parse_district)

    def parse_district(self, response):

        def helper(html, string, default=""):
            result = html.find("div#publikace > h3", containing=string, first=True)
            return result.text[len(string) + 2:] if result is not None else default

        html = HTML(html=response.body, default_encoding="ISO-8859-2")
        region = helper(html, "Kraj")
        county = helper(html, "Okres")
        district_no = helper(html, "Okrsek", default="0")
        town = helper(html, "Obec")
        year = safe_parse_int(re.search(r"ps(\d{4})", response.url).group(1))

        results = self.parse_party_results(
            html,
            region=region,
            county=county,
            town=town,
            district_no=district_no,
            year=year,
        )
        for result in results:
            yield result

        yield self.parse_district_stats(
            html,
            region=region,
            county=county,
            town=town,
            district_no=district_no,
            year=year,
        )

    def parse_party_results(self, html, **info):

        def parse_row(row):
            tds = row.find("td")
            return (tds[1].text, safe_parse_int(tds[2].text))

        tables = html.find("table")[1:]
        for table in tables:
            for row in table.find("tr")[2:]:
                party_name, n_votes = parse_row(row)
                if n_votes is not None and n_votes > 0:
                    yield PartyResultItem(
                        year=info["year"],
                        region=info["region"],
                        county=info["county"],
                        town=info["town"],
                        district_no=info["district_no"],
                        party_name=party_name,
                        n_votes=n_votes,
                    )

    def parse_district_stats(self, html, **info):
        table = html.find("table.table", first=True)
        index = ["Voliči" in th.text for th in table.find("th")].index(True)
        n_all_votes = table.find("td")[index].text

        return DistrictItem(
            district_no=safe_parse_int(info["district_no"]),
            year=info["year"],
            county=info["county"],
            region=info["region"],
            town=info["town"],
            n_all_votes=safe_parse_int(n_all_votes),
        )


def safe_parse_int(s):
    parsed = "".join(c for c in s if c.isdigit())
    return int(parsed) if parsed.isdigit() else None
