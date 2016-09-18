import BaseHTTPServer
import os
import sys
import subprocess
import traceback


class case_no_file(object):
    '''File or directory does not exists.'''

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


class case_cgi_file(object):
    '''Something runnable.'''

    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.py')

    def act(self, handler):
        handler.run_cgi(handler.full_path)


class case_existing_file(object):
    """File exists."""

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        handler.handle_file(handler.full_path)


class case_directory_index_file(object):
    '''Serve index.html page for a directory.'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
                os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.handle_file(self.index_path(handler))


class case_directory_no_index_file(object):
    '''Serve listing for a directory without an index.html page.'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
                not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.list_dir(handler.full_path)


class case_always_fail(object):
    """Base case if nothing else worked."""

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknow object '{0}'".format(handler.path))


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """handler request and return html page in command."""

    Cases = [case_no_file(),
             case_cgi_file(),
             case_existing_file(),
             case_directory_index_file(),
             case_directory_no_index_file(),
             case_always_fail()]

    # How to display an error.
    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    # How to display a directory listing.
    Listing_Page = '''\
        <html>
        <body>
        <ul>
        {0}
        </ul>
        </body>
        </html>
        '''

    def do_GET(self):
        '''Hander the GET request.'''
        try:

            self.full_path = os.getcwd() + self.path.replace('/', "\\")
            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break

        except Exception as msg:
            traceback.print_exc()
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

    def list_dir(self, full_path):
        '''list dir'''
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets))
            self.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

    def run_cgi(self, full_path):
        data = subprocess.check_output(["E:\python\python 2.7.9\python.exe", full_path])
        self.send_content(data)

    def handle_error(self, msg):
        '''Handle error msg and return a Error_Page.'''
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)

    def send_content(self, page, status=200):
        '''Send response to client.'''
        self.send_response(status)
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
