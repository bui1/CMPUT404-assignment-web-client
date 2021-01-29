#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self, data):
        return None

    def get_body(self, data):
        return None

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def get_url_parts(self, url):
        # Parsing for url contents
        # From https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse
        # From Python3 Docs
        parsed = urllib.parse.urlparse(url)
        port = ""
        if not parsed.port:
            if parsed.scheme == "http":
                port = 80
            elif parsed.scheme == "https":
                port = 443
        else:
            port = parsed.port

        host = parsed.hostname

        path = parsed.path
        if parsed.path == "":
            path = "/"

        if parsed.query:
            path += ("?" + parsed.query)

        return host, port, path

    def parse_server_response(self, response):
        response_parts = response.split("\r\n")
        first_line = response_parts[0].split(" ")
        http_code = first_line[1]

        code = 500
        body = ""
        if int(http_code) == 404:
            code = 404
            body = ""
        elif int(http_code) == 200:
            code = 200
            body = response_parts[-1]
        elif int(http_code) == 301:
            code = 301
            body = response_parts[-1]
        elif int(http_code) == 302:
            code = 302
            body = response_parts[-1]

        return code, body

    def GET(self, url, args=None):
        code = 500
        body = ""

        # parse url for host and port to connect to socket
        host, port, path = self.get_url_parts(url)
        self.connect(host, int(port))

        # make the request to send to socket
        # Using Connection:Close to send new requests after a connection is done
        # From Kannan Mohan https://stackoverflow.com/users/1198887/kannan-mohan
        # From StackOveflow
        # From https://stackoverflow.com/a/20402215
        self.sendall(
            "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % (path, host))

        # get the response from socket
        response = self.recvall(self.socket)

        # create the HTTP response object
        print(response)
        if not response:
            return HTTPResponse(404, "")

        code, body = self.parse_server_response(response)

        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        # parse url for host and port to connect to socket
        host, port, path = self.get_url_parts(url)
        self.connect(host, int(port))

        total_length = 0
        final_request_body = ""

        if args is None:
            total_length = 0
            final_request_body = ""
        else:
            # Encoding url arguments
            # https://docs.python.org/3/library/urllib.request.html#urllib-examples
            # From Python3 Docs
            final_request_body = urllib.parse.urlencode(args)
            total_length = len(final_request_body)

        # Example of HTTP POST Request
        # From https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST#example
        # From MDN Docs
        if args:
            request = """POST %s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %s\r\nConnection: close\r\n\r\n%s\r\n
                        """ % (path, host, total_length, str(final_request_body))
        else:
            request = """POST %s HTTP/1.1\r\nHost: %s\r\nContent-Length: 0\r\nConnection: close\r\n\r\n
                        """ % (path, host)

        self.sendall(request)

        # get the response from socket
        response = self.recvall(self.socket)

        # create the HTTP response object
        print(response)

        if not response:
            return HTTPResponse(404, "")

        code, body = self.parse_server_response(response)

        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
