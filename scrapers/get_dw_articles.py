import scrapy
import datetime
import re

class DWSpider(scrapy.Spider):
    name = 'dw_articles'
    def __init__(self, from_date, to_date):
        self.current_date = datetime.date(*[int(x) for x in from_date.split(".")[::-1]])
        self.to_date = datetime.date(*[int(x) for x in to_date.split(".")[::-1]])
        self.download_delay = 0.01
        self.start_urls = [
            self.create_url(self.current_date)
        ]

    def parse_article(self, response):
        title = response.css("h1").get().replace('h1>', 'h2>')
        intro = f"<strong>{response.css('p.intro').get()}</strong>"
        article = ''.join([f"<p>{re.sub('<.*?>', '', x)}</p>" for x in response.css(".longText p").getall()])
        yield {
            'url': response.url,
            'content': title+intro+article
        }

    def create_url(self, date):
        return f'https://www.dw.com/search/?languageCode=de&contentType=ARTICLE&searchNavigationId=9077&from={self.date_to_str(date)}&to={self.date_to_str(date)}&sort=DATE&resultsCounter=100'


    @staticmethod
    def date_to_str(dt):
        return f"{dt.day}.{dt.month}.{dt.year}"

    def parse(self, response):
        for article in response.css('div.searchResult'):
            link = article.css('div a::attr(href)').get()
            yield response.follow(link, self.parse_article)
        if self.current_date < self.to_date:
            self.current_date += datetime.timedelta(days=1)
            yield response.follow(self.create_url(self.current_date), self.parse)
