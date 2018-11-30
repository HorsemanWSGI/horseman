# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


version = "0.1"


install_requires = [
    'autoroutes >= 0.2.0',
    'cromlech.jwt >= 0.1',
    'setuptools',
    'webob',
]

zope_requires = [
    'zope.interface',
    'zope.schema',
]

json_requires = [
    'jsonschema'
]

test_requires = [
    'WebTest',
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
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'zope': zope_requires,
        'json': json_requires,
        'test': test_requires,
        },
    )
