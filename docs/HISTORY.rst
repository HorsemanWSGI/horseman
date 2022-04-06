CHANGES
=======

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
