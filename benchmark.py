# -*- coding: utf-8 -*-
from random import shuffle
from time import time
from urlparse import urlparse
import simplejson
import requests
from constants import HTTP_RESPONSE_CODES


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
        self.timeout = getattr(self.options, 'timeout', None)
        self.scenarios = []
        scenario_path = getattr(options, 'scenario', None)
        url_list = getattr(self.options, 'url_list', None)
        shuffle_urls = getattr(self.options, 'random', None)

        # loading list of URLs, credentials and other settings from JSON file
        if scenario_path:
            self.scenarios = self._load_scenario(scenario_path)

        # loading list of URLs from text file
        if url_list:
            self._load_url_list(url_list)

        # following URLs from list randomly, not one by one
        if shuffle_urls and self.urls:
            shuffle(self.urls)

        self.urls = self.urls or [self.url]


    def validate(self):
        """Making sure all provided parameters correct."""

        if not self.urls:
            print 'Please provide URL(s) for HTTP benchmarking.'

        if self.method not in self.allowed_methods:
            print 'Request method "%s" is not supported. Please do %s requests.' % (self.method,
                                                                                    ','.join(self.allowed_methods))

        if any(self.auth) and not all(self.auth):
            print 'Please provide both login ans password for HTTP authorization.'


    def _prepare_url(self, url):
        """Prepending URL schema, if missing."""

        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = 'http://' + url
        return url

    def _load_scenario(self, scenario_path):
        """Parsing JSON file with scenario, which contains options for batch benchmark testing."""

        f = open(scenario_path, 'r')
        content = f.read()
        content = '"' + content + '"'
        content = content.replace('\n', '')
        content = content.replace('\r', '')
        content = content.replace('\t', '')
        scenario_data = simplejson.loads(content)
        scenarios = []
        for params in scenario_data:
            url = params.get('url', None)
            method = params.get('method', 'get') or 'get'
            repeats = params.get('repeats', 1)
            follow_redirection = params.get('follow_redirection', False)
            scenarios.append({'url': url,
                              'method': method,
                              'repeats': repeats,
                              'follow_redirection': follow_redirection})
        return scenarios

    def _load_url_list(self, url_list):
        """Parsing test file with list of URLs, separated with linebreak."""

        f = open(url_list, 'r')
        content = f.read()
        urls = content.split('\n')
        self.urls = filter(None, urls)
        f.close()

    def start_measure(self):
        self.start_time = time()

    def stop_measure(self):
        return time() - self.start_time

    def measure_request_time(self, url, request_method, **params):
        self.start_measure()
        r = request_method(url, **params)
        # checking if status code is 4xx or 5xx
        if r.status_code >= 400:
            print '%s %s' % (r.status_code, HTTP_RESPONSE_CODES[r.status_code])
        spent_time = self.stop_measure()
        print '%s - %.2fs' % (url, spent_time)

    def run_benchmark(self):
        """Loading and validating options, doing performance testing actually."""

        self.validate()
        if self.scenarios:
            for scenario in self.scenarios:
                url = self._prepare_url(scenario['url'])
                request_method = getattr(requests, scenario['method'], None)
                params = {'allow_redirects': scenario['follow_redirection']}
                for i in range(self.repeats):
                    self.measure_request_time(url, request_method, **params)

        else:
            request_method = getattr(requests, self.method, None)
            params = {'allow_redirects': self.follow_redirection, 'timeout': self.timeout}
            if self.auth:
                params['auth'] = self.auth
            for url in self.urls:
                url = self._prepare_url(url)
                for i in range(self.repeats):
                    self.measure_request_time(url, request_method, **params)