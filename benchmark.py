# -*- coding: utf-8 -*-
from random import shuffle
from time import time
from urlparse import urlparse
import simplejson
import requests
from constants import HTTP_RESPONSE_CODES

class Presser:
    allowed_methods = ['GET', 'POST']

    def __init__(self, url, options):
        self.url = url
        self.urls = []
        self.options = options
        self.method = getattr(self.options, 'method', 'GET') or 'GET'
        self.repeats = getattr(self.options, 'requests', 1)
        scenario_path = getattr(options, 'scenario', None)
        url_list = getattr(self.options, 'url_list', None)
        shuffle_urls = getattr(self.options, 'random', None)

        # loading list of URLs, credentials and other settings from JSON file
        if scenario_path:
            urls = self._load_scenario(scenario_path)
            for u in urls:
                u = self._prepare_url(u)
                r = requests.get(u)
                # checking if status code is 4xx or 5xx
                if r.status_code >= 400:
                    print '%s %s' % (r.status_code, HTTP_RESPONSE_CODES[r.status_code])

        # loading list of URLs from text file
        if url_list:
            self._load_url_list(url_list)

        # following URLs from list randomly, not one by one
        if shuffle_urls and self.urls:
            shuffle(self.urls)


    def validate(self):
        if not self.url or len(self.urls) == 0:
            print 'Please provide URL(s) for HTTP benchmarking'

        if self.method not in self.allowed_methods:
            print 'Request method "%s" is not supported. Please do %s requests.' % (self.method,
                                                                                    ','.join(self.allowed_methods))


    def _prepare_url(self, url):
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = 'http://' + url
        return url

    def _load_scenario(self, scenario_path):
        f = open(scenario_path, 'r')
        content = f.read()
        content = '"' + content + '"'
        content = content.replace('\n', '')
        content = content.replace('\r', '')
        content = content.replace('\t', '')
        scenario = simplejson.loads(content)
        return scenario

    def _load_url_list(self, url_list):
        f = open(url_list, 'r')
        content = f.read()
        urls = content.split('\n')
        self.urls = filter(None, urls)
        f.close()

    def start_measure(self):
        self.start_time = time()

    def stop_measure(self):
        return time() - self.start_time

    def run_benchmark(self):
        self.validate()
        if self.method == 'GET':
            urls = self.urls or [self.url]
            for url in urls:
                url = self._prepare_url(url)
                for i in range(self.repeats):
                    self.start_measure()
                    r = requests.get(url)
                    # checking if status code is 4xx or 5xx
                    if r.status_code >= 400:
                        print '%s %s' % (r.status_code, HTTP_RESPONSE_CODES[r.status_code])
                    spent_time = self.stop_measure()
                    print '%s - %.2fs' % (url, spent_time)