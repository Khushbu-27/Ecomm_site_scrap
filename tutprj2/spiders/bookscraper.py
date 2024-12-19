import os
import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess 
from dotenv import load_dotenv
from scrapy.utils.reactor import install_reactor

install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
load_dotenv()

class BookscraperSpider(CrawlSpider):
    name = "bookscraper"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    base_url = ["https://books.toscrape.com"]
    
    rules = [Rule(LinkExtractor (allow = 'catalogue/',deny='catalogue/category/', unique=True) ,callback= 'parse', follow = True)]
    
    custom_settings ={
        'FEEDS':{
            'books.csv': {
                'format': 'csv'
            }
        }
    }

    def parse(self, response):
        
        for books in response.xpath("//article[@class = 'product_pod']/h3/a/@href"):
            yield response.follow(books, self.product_page_parse)

    def product_page_parse(self, response):
        
        yield {
            
            "title" : response.xpath("//*[@id='content_inner']/article/div[1]/div[2]/h1/text()").get(),
            "price" : response.xpath("//*[@id='content_inner']/article/div[1]/div[2]/p[1]/text()").get(),
            # "stock_availabilty" : response.xpath("//p[@class = 'instock availability']/text()").get(),
            "rating": response.xpath("//*[@id='content_inner']/article/div[1]/div[2]/p[ contains(@class, 'star-rating')]/@class").get(),
            "desc": response.xpath("//*[@id='content_inner']/article/p/text()").get(),
            # "UPC": response.css("content_inner.article table.tbody.tr:nth-child(1).td::text").get(),
            
        }
        
def send_email():
    
    import smtplib
    from email.message import EmailMessage
    
    msg = EmailMessage()
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = os.getenv("EMAIL_USER")
    msg['subject'] = "scrapy mail"
    msg.set_content("This mail is from book to scrap csv file")
    with open('books.csv', 'r') as f:
        data = f.read()
    msg.add_attachment(data, filename = 'books.csv')
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.ehlo()    
    server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
    server.send_message(msg)
    server.quit()
        
process = CrawlerProcess(settings={
    "TWISTED_REACTOR" : 'asyncio'
})
process.crawl(BookscraperSpider)    
process.start()
send_email()


 #
#    /div/div/div/div/section/div[2]/ol/li[1]/article/h3/a
#    /p[@class = 'price_color']/text()

# // //*[@id="content_inner"]/article/div[1]/div[2]/p[3]  
# //h1  
# //article[@class = 'product_page']/p
# catalogue/page-%s" % page for page in list(range(5))  