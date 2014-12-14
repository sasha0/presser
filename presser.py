# -*- coding: utf-8 -*-
from optparse import OptionParser
from benchmark import Presser
                   
parser = OptionParser()
parser.add_option('-m', '--method', dest='method', action='store', type='string', help='POST or GET HTTP method.')
parser.add_option('-r', '--rate', dest='rate', action='store', type="int", help='Number or requests per second.')
parser.add_option('-c', '--requests', dest='requests', action='store', help='Number of concurrent requests.')
parser.add_option('-q', '--random', dest='random', action='store_true', help='Do requests to list of URLs randomly.')
parser.add_option('-l', '--list', dest='url_list', action='store', type='string', help='List of URLs for benchmarking.')
parser.add_option('-s', '--scenario', dest='scenario', action='store', type='string',
                  help='Path to file with benchmarking scenario.')
parser.add_option('-f', '--follow', dest='follow_redirection', action='store_true', help='Follow or skip redirection.')
parser.add_option('-n', '--number', dest='requests', action='store', type='int', help='Total number of requests.')
parser.add_option('-u', '--auth_user', dest='auth_user', action='store', help='Username for HTTP authorization.')
parser.add_option('-p', '--auth_password', dest='auth_password', action='store',
                  help='Password for HTTP authorization.')

(options, args) = parser.parse_args()

if __name__ == '__main__':
    url = args[0] if len(args) > 0 else None
    presser = Presser(url, options)
    presser.run_benchmark()