"""
WSGI config for agrisurvey project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os,sys
import site
from django.core.wsgi import get_wsgi_application






ALLDIRS = ['/home/pierluigi/.virtualenvs/agrisurvey/lib/python2.7/site-packages/']

prev_sys_path = list(sys.path)
for directory in ALLDIRS:
    site.addsitedir(directory)
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
        sys.path[:0] = new_sys_path

sys.path.append('/home/pierluigi/agrisurvey/')


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agrisurvey.settings")

application = get_wsgi_application()