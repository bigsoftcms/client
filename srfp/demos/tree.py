from srfp import comms, protocol

mio = comms.MessageIO('unix:/tmp/virtualbox-sock')

def print_tree(mio, path=tuple()):
    mio.send_msg(protocol.DirectoryListRequest(path))
    listing_resp = mio.recv_msg()

    for i in listing_resp.listing:
        print("{}| {}".format(' '*len(path)*4, i.decode('utf8')))
        if i in (b'.', b'..'):
            continue

        full_path = path + (i,)
        mio.send_msg(protocol.NodeInfoRequest(full_path))
        info_resp = mio.recv_msg()
        if not info_resp.isfile:
            print_tree(mio, full_path)

if __name__ == "__main__":
    print_tree(mio)
