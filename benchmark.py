# -*- coding: utf-8 -*-
from random import shuffle
from time import time
from urlparse import urlparse
import simplejson
import requests
from constants import HTTP_RESPONSE_CODES


METHODS_MAPPING = {'GET', requests.get,
                   }


class Presser:
    allowed_methods = ['delete', 'get', 'head', 'options', 'patch', 'post', 'put']

    def __init__(self, url, options):
        self.url = url
        self.urls = []
        self.options = options
        self.method = getattr(self.options, 'method', 'get') or 'get'
        self.repeats = getattr(self.options, 'requests', 1)
        self.auth_user = getattr(self.options, 'auth_user', None)
        self.auth_password = getattr(self.options, 'auth_password', None)
        self.auth = (self.auth_user, self.auth_password)
        self.follow_redirection = getattr(self.options, 'follow_redirection', False)
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

        self.urls = self.urls or [self.url]


    def validate(self):
        if not self.urls:
            print 'Please provide URL(s) for HTTP benchmarking.'

        if self.method not in self.allowed_methods:
            print 'Request method "%s" is not supported. Please do %s requests.' % (self.method,
                                                                                    ','.join(self.allowed_methods))

        if any(self.auth) and not all(self.auth):
            print 'Please provide both login ans password for HTTP authorization.'


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
        request_method = getattr(requests, self.method, None)
        for url in self.urls:
            url = self._prepare_url(url)
            for i in range(self.repeats):
                self.start_measure()
                params = {'allow_redirects': self.follow_redirection}
                if self.auth:
                    params['auth'] = self.auth
                r = request_method(url, **params)
                # checking if status code is 4xx or 5xx
                if r.status_code >= 400:
                    print '%s %s' % (r.status_code, HTTP_RESPONSE_CODES[r.status_code])
                spent_time = self.stop_measure()
                print '%s - %.2fs' % (url, spent_time)