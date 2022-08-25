CHANGES
=======

0.6 (2022-08-25)
----------------

Major update.

  * Simplified the parsing `Data` class by dropping the attempts at
    mimicking `MultiDict`. Parsing no longer separate files from form
    data and values are stored as a list of tuples containing (name, value).

  * `FormData`, `TypeCastingDict` and `Query` classes were removed.


0.5 (2022-05-31)
----------------

  * Multipart parser no longer adds empty values to the form multidict.

0.4 (2022-04-06)
----------------

  * Fixed `FormData.to_dict` to handle empty or false values.

0.3 (2022-04-05)
----------------

  * PATH_INFO is no longer expected to be there in the environ.
    Some WSGI Servers do NOT provide it if empty.
  * Added path normalization in the Node `__call__` to avoid malformed
    path info.

0.2 (2021-10-08)
----------------

  * First upload on pypi. Stable 0.2.

0.1 (2021-10-08)
----------------

  * Initial release.
