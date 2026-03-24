from setuptools import setup


setup(
    name='horseman',
    install_requires=[
        'biscuits >= 0.3.2',
        'multidict >= 6.7',
        'multifruits >= 0.1.7',
        'orjson >= 3.11',
        'frozendict >= 2.4',
    ],
    extras_require={
        'test': [
            'WebTest',
            'pytest',
            'pyhamcrest'
        ]
    }
)
