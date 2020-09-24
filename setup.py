from setuptools import setup

setup(
    name='watson-stt',
    version='0.1',
    py_modules=['watson_stt'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
            watson-stt=watson_stt:cli
    ''',
)
