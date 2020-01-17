"""Integrte the local django service through a head instance.
"""

import os
import sys

path = os.path
join = path.join
append = sys.path.append

NAME = 'sm'
SETTINGS_NAME = F'{NAME}.settings'

ROOT = join(path.dirname(__file__), '..', NAME)
APP_ROOT = path.abspath(ROOT)


def mutate():
    base = join(APP_ROOT, NAME)
    append(APP_ROOT)
    append(base)
    print(f'Django scope: {base}')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_NAME)

import django


def setup():
    django.setup()
    print('Django setup ready')


def bind():
    mutate()
    setup()


from django.core import  exceptions

def safe_bind():

    try:
        from machine import models
    except exceptions.ImproperlyConfigured:
        print('machine.main is not within the django context; binding.')
        bind()
        from machine import models
