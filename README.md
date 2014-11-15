# SRFP Client for Windows, Mac and Linux

A SRFP server, written in Python, for Windows, Mac and Linux.

SRFP is a read-only file access protocol for data preservation. The SRFP client is designed to be simple to use; it will eventually expose a graphical user interface for mounting and unmounting volumes, so that it can be used 

At current, it is designed to work with the SRFP client for 32-bit DOS, but it should work with any client that implements SRFP over a serial interface. The `comms` module provides communication layer abstraction, so that the client can be extended to work with any bidirectional data stream that is provided to it.

At current, it also provides support for Unix domain sockets, which can be used for testing on Mac OS X and Linux by exposing the serial port of a Virtualbox virtual machine using the 'Host Pipe' method.