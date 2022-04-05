from setuptools import setup


setup(
    name='horseman',
    install_requires=[
        'biscuits >= 0.3.0',
        'multidict >= 5.1',
        'multifruits >= 0.1.5',
        'orjson >= 3.5',
        'frozendict >= 2.0',
    ],
    extras_require={
        'test': [
            'WebTest',
            'pytest',
            'pyhamcrest'
        ]
    }
)
