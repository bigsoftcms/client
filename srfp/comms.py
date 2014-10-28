from urllib.parse import urlparse
import socket

def open(address):
    """Opens a communication channel and returns a stream object that is
    guaranteed to have send(bytes) and recv(bufsize) methods.

    Example address values:

        unix:/tmp/virtualbox-sock
        serial:/dev/ttyS1
        serial:COM1
    """

    method, path = address.split(':', 1)

    if method == 'unix':
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(path)
        return sock

    if method == 'serial':
        raise NotImplemented('TODO: support serial')

    raise ValueError('{} is not a valid method'.format(method))
