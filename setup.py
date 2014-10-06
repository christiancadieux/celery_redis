#!/usr/bin/env python
from setuptools import setup

setup(
    name='celery-redis',
    description='''A redis result backend for celery that uses pubsub to wait for results''',
    version='0.1.1',
    author='Simon Hewitt',
    author_email='si@sjhewitt.co.uk',
    url='http://github.com/sjhewitt/celery_redis',
    packages=['celery_redis'],
    install_requires=[
        'celery>=3.1.15',
        'redis>=2.10.0',
    ],
)
