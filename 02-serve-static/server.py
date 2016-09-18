import BaseHTTPServer
import os
import sys


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """handler request and return html page in command."""

    # How to display an error.
    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    def do_GET(self):
        '''Hander the GET request.'''
        try:
            full_path = os.getcwd() + self.path
            if not os.path.exists(full_path):
                raise ServerException("'{}' not found".format(self.path))
            elif os.path.isfile(full_path):
                self.handle_file(full_path)
            else:
                raise ServerException("Unknow object '{}'".format(self.path))
        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        '''Read static file from local.'''
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)

    def handle_error(self, msg):
        '''Handle error msg and return a Error_Page.'''
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content)

    def send_content(self, page):
        '''Send response to client.'''
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)


class ServerException(Exception):
    '''For internal error reporting.'''
    pass

if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
