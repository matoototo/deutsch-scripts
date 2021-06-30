import scrapy

class QuotesSpider(scrapy.Spider):
    def __init__(self):
        self.download_delay = 0.0

    name = 'articles'
    start_urls = [
        'https://www.nachrichtenleicht.de/suchseite.2040.de.html?search%5Bsubmit%5D=1&search%5Bword%5D=',
    ]

    def parse_article(self, response):
        yield {
            'url': response.url,
            'content': response.css('#pageContentMain').get()
        }

    def parse(self, response):
        for article in response.css('p.dra-lsp-suche-artikel-headline'):
            link = article.css('p a::attr(href)').get().replace('.de.html', '.de.print')
            yield response.follow(link, self.parse_article)
        next_page = response.css('.dra-lsp-seitenzahl + a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
