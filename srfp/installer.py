import sys
from time import sleep

import begin

from . import comms

@begin.start
def install(filepath, address):
    """Dumps the contents of filepath into the stream at address."""

    sock = comms.open(address)
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(10)
            if data:
                print(data)
                sock.send(data)
            else:
                sock.send(bytes((26,)))
                break
