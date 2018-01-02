# -*- coding: utf-8 -*-

import os
import random
from scrapy.conf import settings
import logging
from scrapy.http import HtmlResponse
from selenium import webdriver
import base64
from settings import PROXIES


class RandomUserAgentMiddleware(object):

    def process_request(self, request, spider):
        ua = random.choice(settings.get('USER_AGENT_LIST'))
        if ua:
            request.headers.setdefault('User-Agent', ua)
            #logging.info('User-Agent: ' + ua)


class ProxyMiddleware(object):

    def process_request(self, request, spider):
        proxy = random.choice(PROXIES)
        if proxy['user_pass'] is not None:
            request.meta['proxy'] = "http://%s" % proxy['ip_port']
            encoded_user_pass = base64.encodestring(proxy['user_pass'])
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
        else:
            request.meta['proxy'] = "%s" % proxy['ip_port']


class PhantomJSMiddleware(object):

    def process_request(self, request, spider):

        if 'PhantomJS' in request.meta.keys():
            logging.info('PhantomJS Requesting: '+request.url)
            try:
                driver = request.meta['driver']
                driver.get(request.url)
                content = driver.page_source.encode('utf-8')
                url = driver.current_url.encode('utf-8')
                return HtmlResponse(url, encoding='utf-8', status=200, body=content, request=request)

            except Exception, e:
                driver = request.meta['driver']
                logging.error('PhantomJS Exception!!! ' + driver.current_url.encode('utf-8'))
                return HtmlResponse(request.url, encoding='utf8', status=503, body='')

