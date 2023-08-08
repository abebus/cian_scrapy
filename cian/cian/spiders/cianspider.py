import scrapy
from cian.items import CianItem
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cian.http import SeleniumRequest
# from requests import request
# from bs4 import BeautifulSoup

class CianspiderSpider(scrapy.Spider):
    name = "cianspider"

    def __init__(self):
        self.driver: Firefox
        self.driver = None


    def start_requests(self):
        req = SeleniumRequest(url='https://kazan.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=1&region=4777&room1=1', callback=self.parse)
        yield req


    def click_more(self):
        more_btn_xpath = '//a[contains(@class, "more-button")]'
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, more_btn_xpath)))
            more_button = self.driver.find_element(By.XPATH, more_btn_xpath)
            print('more btn found')
        except NoSuchElementException:
            return
        except TimeoutException:
            return
        else:
            self.driver.execute_script(r'window.scrollTo(0, document.body.scrollHeight);')
            self.driver.execute_script("arguments[0].click();", more_button)
            print('more btn clicked')
            self.click_more()

    # def parse_additional(self, flat_url):
    #     '''
    #     Реализовать возможность сбора дополнительных деталей об объявлениях, таких как описание объекта,
    #     контактные данные продавца/арендодателя и т.д. при подробном просмотре объявления,
    #     то есть при клике на страницу объявления.
    #     '''
    #     response = request('GET', flat_url)
    #     data = response.text
    #     soup = BeautifulSoup(data, 'lxml')
    #     description = soup.findAll('div', {'data-id': 'content'})
    #     for elem in description:
    #         print(elem)
    #     # phone_button = soup.find(name='div', attrs={'data-name': "PhonesContainer"})
    #     return description

    def parse_flats(self, response):
        flat: scrapy.Selector
        for flat in response.css('article > div[data-testid="offer-card"]'):
            url = flat.css('a').attrib['href']
            # desc = self.parse_additional(url)
            yield CianItem(url=url,
                           header=flat.css('span[data-mark=OfferTitle] > span::text').get(),
                           addr=' '.join(flat.css('a[data-name=GeoLabel]::text').getall()),
                           price=flat.css('span[data-mark=MainPrice] > span::text').get(),
                           page=self.cur_page_num,
                           description='')

    def parse(self, response: scrapy.Request):
        if self.driver is None:
            self.driver = response.meta['driver']

        self.cur_page_num = int(response.css('nav[data-name=Pagination] > ul > li > button[disabled] > span::text').get())

        yield from self.parse_flats(response)

        next_button: scrapy.Selector
        next_button = response.css('nav[data-name=Pagination] > a').xpath('//span[text()="Дальше"]/parent::button')

        if next_button.attrib.get('disabled') is None:
            yield SeleniumRequest(url=f'https://kazan.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p={self.cur_page_num+1}&region=4777&room1=1', callback=self.parse)
        else:
            print('MORE BUTTTN')
            self.click_more()
            yield from self.parse_flats(response)

