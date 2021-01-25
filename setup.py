# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


version = "0.1"

install_requires = [
    'autoroutes >= 0.2.0',
    'setuptools',
    'biscuits',
    'multifruits',
    'wrapt',
]

test_requires = [
    'WebTest',
    'pytest',
    'tox',
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
