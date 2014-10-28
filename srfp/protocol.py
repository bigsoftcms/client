import struct
from binascii import crc32

_HEADER_SPEC = '!BHH'
_FOOTER_SPEC = '!I'
_HEADER_LEN = struct.calcsize(_HEADER_SPEC)
_FOOTER_LEN = struct.calcsize(_FOOTER_SPEC)

class _Message (object):
    @classmethod
    def parse(cls, data, response):
        expected_crc = crc32(data[:-_FOOTER_LEN]) & 0xffffffff
        (actual_crc,) = struct.unpack(_FOOTER_SPEC, data[-_FOOTER_LEN:])
        assert expected_crc == actual_crc

        msgtype, id, length = struct.unpack(_HEADER_SPEC, data[:_HEADER_LEN])
        assert len(data) == length + _HEADER_LEN + _FOOTER_LEN

        if cls == _Message:
            subcls = (REQUEST_CLASSES if not response
                    else RESPONSE_CLASSES)[msgtype]
        else:
            subcls = cls

        obj = subcls()
        obj.id = id
        obj._parse_message_body(data[_HEADER_LEN:-_FOOTER_LEN])
        return obj

    def encode(self, id):
        body = self._encode_message_body()
        header = struct.pack(_HEADER_SPEC, self.msgtype, id, len(body))
        raw_crc = crc32(body, crc32(header)) & 0xffffffff
        print('crc32 = {:#010x}'.format(raw_crc))
        crc = struct.pack(_FOOTER_SPEC, raw_crc)
        return b''.join((header, body, crc))


class DirectoryListRequest (_Message):
    msgtype = 0x01

    def __init__(self, path=[]):
        self.path = path

    def _parse_message_body(self, body):
        self.path = body.split(b'\0')

    def _encode_message_body(self):
        return b'\0'.join(self.path)

class DirectoryListResponse (_Message):
    msgtype = 0x01

    def __init__(self, listing=[]):
        self.listing = listing

    def _parse_message_body(self, body):
        self.listing = body.split(b'\0')

    def _encode_message_body(self):
        return b'\0'.join(self.listing)

class NodeInfoRequest (_Message):
    msgtype = 0x02

    def __init__(self, path=[]):
        self.path = path

    def _parse_message_body(self, body):
        self.path = body.split(b'\0')

    def _encode_message_body(self):
        return b'\0'.join(self.path)

class NodeInfoResponse (_Message):
    msgtype = 0x02

    def __init__(self, isfile=False, size=0, created=0, accessed=0, modified=0):
        self.isfile = isfile
        self.size = size
        self.created = created
        self.accessed = accessed
        self.modified = modified

    def _parse_message_body(self, body):
        (self.isfile, self.size, self.created,
                self.accessed, self.modified) = struct.unpack('!?IIII', body)

    def _encode_message_body(self):
        return struct.pack('!?IIII', self.isfile, self.size,
                self.created, self.accessed, self.modified)

class FileContentsRequest (_Message):
    msgtype = 0x03

    def __init__(self, offset=0, requested_length=0, path=[]):
        self.offset = offset
        self.requested_length = length
        self.path = path

    def _parse_message_body(self, body):
        self.offset, self.requested_length = struct.unpack('!II', body[:8])
        self.path = body[8:].split(b'\0')

    def _encode_message_body(self):
        return (struct.pack('!II', self.offset, self.requested_length) +
                '\0'.join(path))

class FileContentsResponse (_Message):
    msgtype = 0x03

    def __init__(self, data):
        self.data = data

    def _parse_message_body(self, body):
        self.data = body

    def _encode_message_body(self):
        return self.data

class VersionRequest (_Message):
    msgtype = 0x7F

    def _parse_message_body(self, body):
        pass

    def _encode_message_body(self):
        return b''

class VersionResponse (_Message):
    """The Python representation of the version should be a 3-tuple: (major, minor, bugfix)"""
    msgtype = 0x7F

    def __init__(self, version):
        self.version = version

    def _parse_message_body(self, body):
        self.version = struct.unpack('!BBB', body)

    def _encode_message_body(self):
        return struct.pack('!BBB', *self.version)

REQUEST_CLASSES = {
    0x01: DirectoryListRequest,
    0x02: NodeInfoRequest,
    0x03: FileContentsRequest,
    0x7F: VersionRequest,
}
RESPONSE_CLASSES = {
    0x01: DirectoryListResponse,
    0x02: NodeInfoResponse,
    0x03: FileContentsResponse,
    0x7F: VersionResponse,
}
