from __future__ import division, print_function, unicode_literals

"""
Use this in the same way as Python's SimpleHTTPServer:

  python -m RangeHTTPServer [port]

The only difference from SimpleHTTPServer is that RangeHTTPServer supports
'Range:' headers to load portions of files. This is helpful for doing local web
development with genomic data files, which tend to be to large to load into the
browser all at once.

https://github.com/danvk/RangeHTTPServer

https://docs.python.org/3/library/http.server.html


Consider something with asyncio framework
https://github.com/aio-libs/aiohttp
"""

import http.server
import os
import re
import socket
import socketserver
import sys
import threading
import urllib.parse


BYTE_RANGE_RE = re.compile(r'bytes=(\d+)-(\d+)?$')
def parse_byte_range(byte_range):
    """
    Returns the two numbers in 'bytes=123-456' or throws ValueError.

    The last number or both numbers may be None.
    """
    if byte_range.strip() == '':
        return None, None

    m = BYTE_RANGE_RE.match(byte_range)
    if not m:
        raise ValueError('Invalid byte range: {}'.format(byte_range))

    first, last = [x and int(x) for x in m.groups()]
    # if last and last < first:
    #     raise ValueError('Invalid byte range: {}'.format(byte_range))

    return first, last

#------------------------------------------------


# class PathHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
class PathHTTPServer(http.server.HTTPServer):
    """
    http://louistiao.me/posts/python-simplehttpserver-recipe-serve-specific-directory/
    """
    def __init__(self, path_base, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RequestHandlerClass.path_base = path_base

        # https://github.com/rust-lang/rust/issues/18847
        self.request_queue_size = 25



class RangeRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Adds support for HTTP 'Range' requests to SimpleHTTPRequestHandler

    The approach is to:
    - Override send_head to look for 'Range' and respond appropriately.
    - Override copyfile to only transmit a range when requested.
    """
    verbose = False
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol_version = 'HTTP/1.1'

    def handle(self):
        """
        http://stackoverflow.com/questions/6063416/python-basehttpserver-how-do-i-catch-trap-broken-pipe-errors
        """
        try:
            http.server.SimpleHTTPRequestHandler.handle(self)
        except socket.error:
            pass

    def log_message(self, *args, **kwargs):
        """
        Log an arbitrary message.  This is used by all other logging functions.

        Overridden here to enable/disable writing to stderr.
        """
        if self.verbose:
            super().log_message(*args, **kwargs)

    def do_GET(self):
        """
        Serve a GET request
        """
        path_work = self.translate_path(self.path)
        self.file_size = None

        if os.path.isfile(path_work):
            fp = self.send_file_head()
        else:
            fp = self.send_directory_head()

        if fp:
            try:
                self.copy_chunks(fp, self.wfile)
            finally:
                fp.close()

    def send_directory_head(self):
        """
        Parse contents of directory and generate a respones.
        """
        path_work = self.translate_path(self.path)
        parts = urllib.parse.urlsplit(self.path)

        # List directory contents into string buffer
        buffer = self.list_directory(path_work)

        # Store file size
        buffer.seek(0, os.SEEK_END)
        self.file_size = buffer.tell()
        buffer.seek(0)

        path_work = buffer

        self.range = 0, self.file_size-1

        return path_work

    def send_file_head(self, path_work=None):
        """
        Derived from SimpleHTTPServer.py with added support for byte-range requests.
        """
        # Handle ranges
        if 'Range' in self.headers:
            try:
                self.range = parse_byte_range(self.headers['Range'])
            except ValueError:
                self.send_error(400, 'Invalid byte range')
                return None
        else:
            self.range = 0, None

        # Extract requested byte range
        first, last = self.range

        # Continue with serving requested file data
        if not path_work:
            path_work = self.translate_path(self.path)

        fp = None
        try:
            fp = open(path_work, 'rb')
        except IOError:
            self.send_error(404, 'File not found')
            return None

        fs = os.fstat(fp.fileno())
        if not self.file_size:
            self.file_size = fs[6]

        if first is None:
            raise ValueError('errrr need to figure out this part: {}'.format(self.range))

        if first >= self.file_size:
            # https://tools.ietf.org/html/rfc7233
            self.send_error(416, 'Requested Range Not Satisfiable')
            return None

        if last is None:
            # Range end is unspecified, so server gets to decide.
            last = first + self.file_size  #1024*1024

        if last >= self.file_size:
            # Don't go past end of file
            last = self.file_size - 1

        # Update internal range values
        self.range = first, last

        response_length = last - first + 1

        try:
            self.send_response(206)
            self.send_header('Content-type', self.guess_type(path_work))
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Range', 'bytes {}-{}/{}'.format(first, last, self.file_size))
            self.send_header('Content-Length', str(response_length))
            self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))

            # Cache stuff, but doesn't appear to work woith range requests :(
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
            self.send_header('Cache-Control', 'public, max-age=31536000')

            self.end_headers()
            return fp
        except:
            fp.close()
            raise


    def copy_chunks(self, src, dst):
        """
        Copy data from source file to destination file in little chunks.
        """
        buffer_size = 256*1024

        first, last = self.range  # defined earlier in method send_head()

        if last is None or last >= self.file_size:
            # This issue should have been handled earlier.
            raise ValueError('Unexpected range: {}'.format(self.range))
            # last = self.file_size - 1
            # self.range = first, last

        # Keep reading/writing until nothing left tot copy.
        position = first
        src.seek(first)
        while last - position + 1 > 0:
            # Read it
            buffer_read = min(buffer_size, last-position+1)
            data = src.read(buffer_read)
            if len(data) == 0:
                break

            # Count it
            position += len(data)

            # Write it
            try:
                dst.write(data)
            except ConnectionResetError as e:
                # print(e)
                # print(first, position, last)
                break

        # Finish
        bytes_copied = position - first + 1
        return bytes_copied

    def translate_path(self, path):
        """
        Derived from:
        http://louistiao.me/posts/python-simplehttpserver-recipe-serve-specific-directory/
        """
        path = os.path.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)

        path_work = self.path_base
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue

            path_work = os.path.join(path_work, word)

        return path_work


#------------------------------------------------



def normalize_url(url):
    """
    https://docs.python.org/3.0/library/urllib.parse.html#urllib.parse.ParseResult.geturl
    """
    parts = urllib.parse.urlsplit(url)
    nice_url = parts.geturl()

    return nice_url


class Server():
    """
    Handy wrapper for my http file server.
    """
    def __init__(path_serve=None, port=None):
        """
        Make a new server instance
        """
        if not path_serve:
            path_serve = os.path.abspath(os.path.curdir)

        if not port:
            port = 9876

        self._path_serve = path_serve
        self._port = port

    def __repr__(self):
        return self.status()

    @property
    def path_serve(self):
        """
        Local folder that maps to root url.
        """
        return self._path_serve

    @property
    def port(self):
        return self._port

    @property
    def is_running(self):
        pass

    def status(self):
        pass

    @property
    def url_root(self):
        """
        Complete url to root address
        """
        url = 'http://127.0.0.1:{:d}'.format(self.port)
        return normalize_url(url)

    def filename_to_url(self, fname):
        """
        Convert local filename to url handled by this server.
        """
        fname = os.path.abspath(os.path.normpath(fname))

        a, b = fname.split(os.path.normpath(self.path_serve))
        url = normalize_url(self.url_root + b)

        return url

    def start(self):
        pass

    def stop(self):
        pass




#------------------------------------------------


def main(path_base='.', port=9998, bind='localhost'):
    """
    https://docs.python.org/3/library/http.server.html
    https://docs.python.org/3/library/socketserver.html#server-objects
    https://docs.python.org/3.5/library/socketserver.html#socketserver.TCPServer
    """
    path_base = os.path.normpath(os.path.abspath(path_base))

    server_address = bind, port

    ServerClass = PathHTTPServer
    HandlerClass = RangeRequestHandler

    httpd = ServerClass(path_base, server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    tpl = "Serving HTTP on {host} port {port} (http://{host}:{port}/) ..."
    print(tpl.format(host=sa[0], port=sa[1]))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received, exiting.')

    print('Done')


###########################################

if __name__ == '__main__':

    main(path_base='/home/pierre/Videos/GoPro/Malibu/')
