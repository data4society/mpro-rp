"""some useful variables and functions"""

import sys
import os
import pwd


# check is it celery based running
if "worker" in sys.argv:
    celery = True
else:
    celery = False

# home path with celery based or not running:
if celery:
    home_dir = pwd.getpwuid(os.getuid()).pw_dir
else:
    home_dir = os.path.expanduser("~")
