# -*- coding: utf-8 -*-
import json
from random import shuffle
from time import time
from urlparse import urlparse

import grequests
import requests
from constants import HTTP_RESPONSE_CODES


class Presser:
    allowed_methods = ['delete', 'get', 'head', 'options', 'patch', 'post', 'put']

    def __init__(self, url, options):
        self.url = url
        self.urls = []
        self.options = options
        self.method = getattr(self.options, 'method', 'get') or 'get'
        self.method = self.method.lower()
        self.repeats = getattr(self.options, 'requests', 1) or 1
        self.concurrent_requests = getattr(self.options, 'concurrent_requests', 1) or 1
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
        content = content.replace('\n', '')
        content = content.replace('\r', '')
        content = content.replace('\t', '')
        scenario_data = json.loads(content)
        scenarios = []
        for params in scenario_data:
            url = params.get('url', None)
            method = params.get('method', 'get') or 'get'
            repeats = params.get('repeats', 1)
            concurrent_requests = params.get('concurrent_requests', 1)
            follow_redirection = params.get('follow_redirection', False)
            cookies = params.get('cookies', {})
            data = params.get('data', {})
            headers = params.get('headers', {})
            scenarios.append({'url': url,
                              'method': method,
                              'repeats': repeats,
                              'follow_redirection': follow_redirection,
                              'data': data,
                              'headers': headers,
                              'concurrent_requests': concurrent_requests,
                              'cookies': cookies})
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

    def get_status_message(self, status_code):
        return HTTP_RESPONSE_CODES.get(status_code, 'Unknown status code')

    def check_response_status(self, response):
        # checking if status code is 4xx or 5xx
        if response.status_code >= 400:
            status_message = self.get_status_message(response.status_code)
            print '%s %s' % (response.status_code, status_message)

    def measure_request_time(self, concurrent_requests, url, request_method_name, **params):
        """Making request with given parameters and calculating time, spent on request."""

        concurrent_requests = int(concurrent_requests)
        requests_module = grequests if concurrent_requests > 1 else requests
        request_method = getattr(requests_module, request_method_name, None)

        self.start_measure()
        try:
            status_message = ''
            if concurrent_requests > 1:
                r = [request_method(url, **params) for i in range(concurrent_requests)]
                responses = grequests.map(r)
                status_codes = []
                for response in responses:
                    status_codes.append(response.status_code)
                    self.check_response_status(response)
                status_codes = set(status_codes)
                status_messages = ['%s %s' % (s, self.get_status_message(s)) for s in status_codes]
                status_message = ', '.join(status_messages)
            else:
                r = request_method(url, **params)
                self.check_response_status(r)
                status_message = '%s %s' % (r.status_code, self.get_status_message(r.status_code))

            spent_time = self.stop_measure()
            if spent_time > 1:
                spent_time = '%.3fs' % spent_time
            else:
                spent_time = '%ims' % (spent_time * 1000)
            print '%s - %s (%s)' % (url, spent_time, status_message)
        except Exception as e:
            print "Trying to perform %s request to URL %s" % (request_method_name.upper(), url)
            print "Got exception: %s" % e

    def measure_requests_time(self, repeats, concurrent_requests, url, request_method_name, **params):
        """Iterate through list of requests and measure loading time for each of them."""
        for i in range(repeats):
            self.measure_request_time(concurrent_requests, url, request_method_name, **params)

    def run_benchmark(self):
        """Loading and validating options, doing performance testing actually."""

        self.validate()
        if self.scenarios:
            for scenario in self.scenarios:
                params = {'stream': True}
                url = self._prepare_url(scenario['url'])
                request_method_name = scenario['method'].lower()
                allow_redirects = scenario.get('follow_redirection', None)
                timeout = scenario.get('timeout', None)
                data = scenario.get('data', None)
                repeats = scenario.get('repeats', 1)
                headers = scenario.get('headers', None)
                concurrent_requests = scenario.get('concurrent_requests', 1)
                cookies = scenario.get('cookies', {})
                if allow_redirects:
                    params['allow_redirects'] = allow_redirects
                if timeout:
                    params['timeout'] = timeout
                if data:
                    params['data'] = data
                if headers:
                    params['headers'] = headers
                if cookies:
                    params['cookies'] = cookies
                self.measure_requests_time(repeats, concurrent_requests, url, request_method_name, **params)

        else:
            params = {'allow_redirects': self.follow_redirection, 'timeout': self.timeout, 'stream': True}
            if self.auth:
                params['auth'] = self.auth
            for url in self.urls:
                url = self._prepare_url(url)
                self.measure_requests_time(self.repeats, self.concurrent_requests, url, self.method, **params)