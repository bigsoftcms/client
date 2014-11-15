# SRFP Client for Mac OS X (and Windows and Linux, soon)

A SRFP server, written in Python, for Windows, Mac and Linux. Currently, it is tested on Mac OS X, but it should work on Linux, and Windows should be trivial to add support.

SRFP is a read-only file access protocol for data preservation. The SRFP client is designed to be simple to use; it will eventually expose a graphical user interface for mounting and unmounting volumes, so that it can be used 

At current, it is designed to work with the SRFP client for 32-bit DOS, but it should work with any client that implements SRFP over a serial interface. The `comms` module provides communication layer abstraction, so that the client can be extended to work with any bidirectional data stream that is provided to it.

At current, it also provides support for Unix domain sockets, which can be used for testing on Mac OS X and Linux by exposing the serial port of a Virtualbox virtual machine using the 'Host Pipe' method.

## Installation 

First, install Then install OSXFUSE by [downloading the latest stable release](http://osxfuse.github.io/), and Pip, with the following command:

    curl -oget-pip.py https://bootstrap.pypa.io/get-pip.py && python get-pip.py

Then, install SRFP:

    pip install srfp

## Usage

To mount a volume, run:

    srfpmnt <SERVER PATH> <MOUNT PATH>

where `<SERVER PATH>` is either a path to a serial port or a Unix domain socket, e.g. `serial:/dev/tty.usbserial` or `unix:/tmp/virtualbox.sock`, and `<MOUNT PATH>` is the path to mount the SRFP directory on.

To list the contents of a SRFP remote, run:

    srfptree <SERVER PATH>
    
where `<SERVER PATH>` is specified as above.