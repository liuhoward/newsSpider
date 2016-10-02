#encoding: utf-8
import scrapy
import re
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from newsSpider.items import NewsspiderItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider,Rule,BaseSpider
from scrapy.http import Request,FormRequest
from selenium import webdriver
import time
import random
import json
import datetime
import logging
import redis
import urllib
import os

class ExampleSpider(scrapy.Spider):
    name = "newsSpider"

    username = "howard0601@163.com"
    password = "testsb"

    account = [
        'howard0601@163.com',
        'h1746664@mvrht.com',
        'h1746795@mvrht.com',
        'h1746883@mvrht.com',
        'h1746998@mvrht.com'
    ]

    start_urls = ["https://www.glassdoor.com/index.htm",
                  "https://www.glassdoor.com/Reviews/us-reviews-SRCH_IL.0,2_IN1.htm",
                  "https://www.glassdoor.com/Reviews/Apple-Reviews-E1138.htm",
                  ]

    index_url = '''https://www.glassdoor.com/index.htm'''

    driver = None
    cookies = None

    recaptchaStatus = False
    loginTime = None
    index = 4

    last_url = ""

    company = set()
    def get_company_list(self, companFile):


        with open(companFile, "r") as file:
            data = json.load(file)

        for entry in data:
            comName = entry["company"]
            if comName in self.company:
                continue
            self.company.add(comName)

        #for com in self.company:
        #    print(com)



    def __init__(self):
        service_args_debug = ['--load-images=false', '--disk-cache=true', '--debug=true', '--webdriver-loglevel=debug']
        service_args = ['--disk-cache=true']
        self.driver = webdriver.PhantomJS(
            service_args=service_args)
        #self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        #time.sleep(5)
        self.driver.set_window_size(1280,1024)#640, 960)
        comListFile = "companyProfile.json"
        self.get_company_list(comListFile)

    def __del__(self):
        self.driver.close()

        print "=================last_url:" + self.last_url


    def logout(self):
        try:
            self.driver.find_element_by_css_selector("i.profile").click()
            self.driver.find_element_by_css_selector("input.antiBtn").click()
            time.sleep(2)
        except:
            logging.error("fail to sign out")


    def login(self):

        while self.recaptchaStatus:
            time.sleep(10)

        self.logout()
        self.driver.implicitly_wait(10)
        self.driver.get(self.index_url)
        time.sleep(2)
        count = 1
        while True:
            try:
                self.driver.find_element_by_css_selector("span.hideHH").click()
                # self.driver.find_element_by_class_name("hideHH").click()
                self.driver.implicitly_wait(10)
                break

            except:
                # print "==============try fail, sleep"
                logging.error("fail to sign in")
                # time.sleep(20)
                self.driver.implicitly_wait(20)
            count += 1
            if count == 5:
                with open("login.html", "w") as file:
                    file.write(self.driver.page_source.encode('utf-8'))
                return

        self.driver.find_element_by_id("signInUsername").clear()
        self.driver.find_element_by_id("signInUsername").send_keys(self.username)
        self.driver.find_element_by_id("signInPassword").clear()
        self.driver.find_element_by_id("signInPassword").send_keys(self.password)
        self.driver.find_element_by_id("signInBtn").click()
        time.sleep(5)
        self.cookies = self.driver.get_cookies()
        time.sleep(1)
        self.loginTime = datetime.datetime.now()
        self.index = 1
        return

    def relogin(self):

        while self.recaptchaStatus:
            time.sleep(10)

        self.logout()
        self.driver.implicitly_wait(10)
        self.driver.get(self.index_url)
        time.sleep(2)
        count = 1
        while True:
            try:
                self.driver.find_element_by_css_selector("span.hideHH").click()
                # self.driver.find_element_by_class_name("hideHH").click()
                self.driver.implicitly_wait(10)
                break

            except:
                # print "==============try fail, sleep"
                logging.error("fail to sign in")
                # time.sleep(20)
                self.driver.implicitly_wait(20)
            count += 1
            if count == 5:
                with open("login.html", "w") as file:
                    file.write(self.driver.page_source.encode('utf-8'))
                return

        username = random.choice(self.account)
        self.driver.find_element_by_id("signInUsername").clear()
        self.driver.find_element_by_id("signInUsername").send_keys(username)
        self.driver.find_element_by_id("signInPassword").clear()
        self.driver.find_element_by_id("signInPassword").send_keys(self.password)
        self.driver.find_element_by_id("signInBtn").click()
        time.sleep(5)
        self.cookies = self.driver.get_cookies()
        time.sleep(1)
        self.loginTime = datetime.datetime.now()
        self.index = 1
        return

    def recaptcha(self):
        self.recaptchaStatus = True
        self.driver.get(self.index_url)
        time.sleep(2)
        while True:
            try:
                captcha = self.driver.find_element_by_id('recaptcha_response_field')
                img = self.driver.find_element_by_id("recaptcha_challenge_image")
                if img:
                    src=img.get_attribute('src')
                    urllib.urlretrieve(src, "captcha.jpg")
                    #os.system("display /home/howard/workspace/newsSpider/captcha.jpg")

                else:
                    break

                logging.error('input captcha!!!!!!!!!!')
                captcha_input = raw_input(">>> Input: ")
                #captcha_input = self.r_local.get(
                #    'captcha_input')
                if captcha_input:
                    captcha.clear()
                    captcha.send_keys(captcha_input)
                    self.driver.find_element_by_id("dCF_input_complete").click()
                    #WebElement.sendKeys(Keys.RETURN);
                else:
                    time.sleep(10)

                #time.sleep(15)

            except:
                logging.info("sucess recaptcha!!!!!!!!!")
                break
        self.recaptchaStatus = False
        self.cookies = self.driver.get_cookies()
        time.sleep(1)

        return

    def start_requests(self):
        print "==========================request"

        self.recaptcha()
        self.login()

        return [
            scrapy.Request(self.start_urls[0], meta={'driver': self.driver, 'PhantomJS': True}, dont_filter=True)
        ]


    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        captcha = soup.find("div", id="recaptcha_image")
        if captcha:
            self.recaptcha()

        yield scrapy.Request(self.start_urls[1], callback=self.parse_company,  meta={'driver': self.driver, 'PhantomJS': True}, dont_filter=True)


    def parse_company(self, response):

        nowTime = datetime.datetime.now()
        delta = (nowTime - self.loginTime).seconds
        if  delta >= 400:
            #yield scrapy.Request(response.url, callback=self.parse_company, meta={'driver': self.driver, 'PhantomJS': True}, dont_filter=True)
            #time.sleep(30)
            # self.logout()
            self.relogin()

        soup = BeautifulSoup(response.body, 'lxml')
        signin = soup.find("span", class_="signin acctMenu")
        if signin:
            self.relogin()

        captcha = soup.find("div", id="recaptcha_image")
        if captcha:
            self.recaptcha()

        domain = "https://www.glassdoor.com"
        #self.cookies = self.driver.get_cookies()
        for comModule in soup.find_all("div", class_="eiHdrModule module snug notranslate "):
            comTag = comModule.find("a", class_="h1 tightAll")
            if comTag and comTag.string:
                comName = comTag.string.strip()
                if comName in self.company:
                    comLink = soup.find("a", class_="eiCell cell reviews")
                    if comLink:
                        titleLink = domain + comLink['href']
                        yield scrapy.Request(titleLink, callback=self.parse_page,
                                             meta={'driver': self.driver, 'PhantomJS': True}, dont_filter=True)

        '''
        for comLink in soup.find_all("a", class_="eiCell cell reviews"):
            titleLink = domain + comLink['href']
            #print "=================================company link:" + titleLink
            #time.sleep(random.random())
            yield scrapy.Request(titleLink, callback=self.parse_page, meta={'driver': self.driver, 'PhantomJS': True}, dont_filter=True)
        '''


        nextlink = response.xpath('//li[@class="next"]/a/@href').extract()

        if nextlink:
            link = domain + nextlink[0]
            #print "==================================nextlink " + link
            #time.sleep(random.random())

            yield scrapy.Request(link, callback=self.parse_company, meta={'driver': self.driver, 'PhantomJS': True}, dont_filter=True)
            self.last_url = link
            #self.index += 1


    def parse_page(self, response):

        nowTime = datetime.datetime.now()
        delta = (nowTime - self.loginTime).seconds
        if delta >= 400:
            self.relogin()

        soup = BeautifulSoup(response.body, 'lxml')

        signin = soup.find("span", class_="signin acctMenu")
        if signin:
            self.relogin()

        captcha = soup.find("div", id="recaptcha_image")
        if captcha:
            self.recaptcha()

        companyName = soup.find("p", class_="h1 strong tightAll")
        if companyName:
            company = companyName['data-company']
        else:
            print "=============================error name:" + response.url
            company = response.url.split("/")[-1]

        if company in self.company:
            count = 0
            for entry in soup.find_all("li", class_="empReview padVert cf "):
                item = NewsspiderItem()
                item['company'] = company
                self.get_review(entry, item)
                yield item
                count += 1

            if count == 0:
                print "=====================no items:" + response.url

        domain = "https://www.glassdoor.com"

        nextlink = response.xpath('//li[@class="next"]/a/@href').extract()

        if nextlink:
            link = domain + nextlink[0]
            # time.sleep(random.random())
            yield scrapy.Request(link, callback=self.parse_page, meta={'driver': self.driver, 'PhantomJS': True}, dont_filter=True)
            self.index += 1


    def get_review(self, container, item):

        reviewID = container['id']
        if reviewID:
            item['reviewID'] = reviewID

        reviewDate = container.find("time", class_="date subtle small")
        if reviewDate:
            item['reviewDate'] = reviewDate.string.strip()

        reviewTitle = container.find("span", class_="summary ")
        item['reviewTitle'] = reviewTitle.get_text().replace("\"", "").strip()

        reviewRating = container.find("span", class_="value-title")
        if reviewRating:
            item['reviewRating'] = float(reviewRating['title'])
        else:
            item['reviewRating'] = 0

        '''
        aspects = []
        for innerRating in container.find_all("span", class_="notranslate notranslate_title gdBars gdRatings med "):
            val = innerRating['title']
            aspects.append(float(val))

        if len(aspects) != 5:
            print "================================number of aspects is wrong"

        item['workRating'] = aspects[0]
        item['cultureRating'] = aspects[1]
        item['careerRating'] = aspects[2]
        item['compensationRating'] = aspects[3]
        item['managementRating'] = aspects[4]
        '''

        workRating = container.find("div", text=re.compile(r"Work/Life Balance"))
        if workRating and workRating.next_sibling and workRating.next_sibling.next_sibling:
            item['workRating'] = float(workRating.next_sibling.next_sibling['title'])

        cultureRating = container.find("div", text=re.compile(r"Culture & Values"))
        if cultureRating and cultureRating.next_sibling and cultureRating.next_sibling.next_sibling:
            item['cultureRating'] = float(cultureRating.next_sibling.next_sibling['title'])

        careerRating = container.find("div", text=re.compile("Career Opportunities"))
        if careerRating and careerRating.next_sibling and careerRating.next_sibling.next_sibling:
            item['careerRating'] = float(careerRating.next_sibling.next_sibling['title'])

        compensationRating = container.find("div", text=re.compile("Comp & Benefits"))
        if compensationRating and compensationRating.next_sibling and compensationRating.next_sibling.next_sibling:
            item['compensationRating'] = float(compensationRating.next_sibling.next_sibling['title'])

        managementRating = container.find("div", text=re.compile("Senior Management"))
        if managementRating and managementRating.next_sibling and managementRating.next_sibling.next_sibling:
            item['managementRating'] = float(managementRating.next_sibling.next_sibling['title'])


        jobTitle = container.find("span", class_=re.compile("authorJobTitle"))
        if jobTitle:
            item['jobTitle'] = jobTitle.get_text().strip()


        jobLocation = container.find("span", class_=re.compile("authorLocation"))
        if jobLocation:
            item['jobLocation'] = jobLocation.get_text().strip()

        workingYear = container.find("p", class_="notranslate tightBot")
        if workingYear:
            item['workingYear'] = workingYear.get_text().strip()

        pros = container.find("p", class_=re.compile("^pros"))
        if pros:
            item['pros'] = pros.get_text().strip()
        else:
            print "===============fail to pros"
            item['pros'] = ""

        cons = container.find("p", class_=re.compile("^cons"))
        if cons:
            item['cons'] = cons.get_text().strip()
        else:
            item['cons'] = ""

        voteCount = container.find("span", class_="count")
        if voteCount and voteCount.span:
            item['voteCount'] = int(voteCount.span.string.strip())
        else:
            item['voteCount'] = 0

        advice = container.find("p", class_=re.compile("adviceMgmt"))
        if advice:
            item['advice'] = advice.get_text().strip()
        else:
            item['advice'] = ""
