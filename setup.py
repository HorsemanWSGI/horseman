import os
from setuptools import setup, find_packages

version = "0.1"

install_requires = [
    'biscuits >= 0.3.0',
    'multidict >= 5.1',
    'multifruits >= 0.1.5',
    'orjson >= 3.5',
    'frozendict >= 2.0',
]

test_requires = [
    'WebTest',
    'pytest',
    'pyhamcrest',
]

setup(
    name='horseman',
    version=version,
    author='Souheil CHELFOUH',
    author_email='trollfot@gmail.com',
    url='https://github.com/HorsemanWSGI/horseman',
    download_url='http://pypi.python.org/pypi/horseman',
    description='Headless WSGI API',
    long_description=(
        open("README.rst").read() + "\n" +
        open(os.path.join("docs", "HISTORY.rst")).read()
    ),
    license='ZPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python:: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
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
