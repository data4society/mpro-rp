import sys
import os
import pwd


if "worker" in sys.argv:
    celery = True
else:
    celery = False

home_dir = pwd.getpwuid(os.getuid()).pw_dir
"""
if celery:
    home_dir = pwd.getpwuid(os.getuid()).pw_dir
else:
    home_dir = os.path.expanduser("~")
"""