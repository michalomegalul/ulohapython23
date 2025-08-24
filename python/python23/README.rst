==========
Assignment
==========

Create a simple CLI application which retrieves and prints data from one of the described backends.

Environment
===========

There are two servers providing a service, one is using gRPC and the other one REST API.

gRPC server uses `<service_file.proto>`_

REST API is described in `<rest_file.rst>`_

Command line
============

Provide a command ``file-client`` with following usage::

    Usage: file-client [options] stat UUID
           file-client [options] read UUID
           file-client --help

    Subcommands:
      stat                  Prints the file metadata in a human-readable manner.
      read                  Outputs the file content.

    Options:
      --help                Show this help message and exit.
      --backend=BACKEND     Set a backend to be used, choices are grpc and rest. Default is grpc.
      --grpc-server=NETLOC  Set a host and port of the gRPC server. Default is localhost:50051.
      --base-url=URL        Set a base URL for a REST server. Default is http://localhost/.
      --output=OUTPUT       Set the file where to store the output. Default is -, i.e. the stdout.


All commands and options need to work as described, but the usage may be formatted differently.
Other options may be provided.

Requirements
============

* Use supported python version (3.7-3.10).
* Third party open source libraries are allowed.
* Linux OS support.
* Unit tests are required.
* Only one of the protocols (REST/gRPC) is required. Implementing both is a bonus.
