=============
File REST API
=============

* URLs below are relative to a ``base_url``.

``file/<uuid>/stat/``
=====================
Accepts a ``GET`` requests.
Returns a JSON response with an file metadata in a JSON object.
A file metadata contains following keys:

* ``create_datetime`` - File creation date and time in ISO format
* ``size`` - File size in bytes
* ``mimetype`` - File MIME type
* ``name`` - Display name of the file

If a file is not found, HTTP code 404 is returned.

``file/<uuid>/read/``
=====================
Accepts a ``GET`` requests.
Returns a response with the file contents.
A ``Content-Disposition`` header contains a display name of the file.
A ``Content-Type`` header contains a MIME type of the file.

If a file is not found, HTTP code 404 is returned.
