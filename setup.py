# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


version = "0.1"

install_requires = [
    'biscuits >= 0.3.0',
    'multifruits >= 0.1.5 ',
    'orjson >= 3.5',
]

test_requires = [
    'WebTest',
    'pytest',
]


setup(
    name='horseman',
    version=version,
    author='Souheil CHELFOUH',
    author_email='trollfot@gmail.com',
    url='http://gitweb.dolmen-project.org',
    download_url='http://pypi.python.org/pypi/horseman',
    description='Headless WSGI API',
    long_description=(open("README.txt").read() + "\n" +
                      open(os.path.join("docs", "HISTORY.txt")).read()),
    license='ZPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python:: 3 :: Only',
        ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': test_requires,
        },
    )
