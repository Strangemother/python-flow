import os
import sys

pt = os.path
jn = pt.join

NAME = 'sm'
SETTINGS_NAME = F'{NAME}.settings'

ROOT = jn(pt.dirname(__file__), '..')
APP_ROOT = pt.abspath(ROOT)

_ap = sys.path.append

_ap(APP_ROOT)
_ap(jn(APP_ROOT, NAME))


os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_NAME)

import django
django.setup()

from flow.machine import models
