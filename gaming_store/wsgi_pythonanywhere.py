"""
Corrected WSGI file for PythonAnywhere deployment.

PASTE THIS ENTIRE CONTENT into your PythonAnywhere WSGI file at:
    /var/www/gamingstore7683_pythonanywhere_com_wsgi.py

It puts your project on sys.path and adds your virtualenv's site-packages
so that `flask` (and all other dependencies) are importable. This fixes the
"ModuleNotFoundError: No module named 'flask'" error.

Paths used:
    Project root : /home/gamingstore7683/GAMING-S/gaming_store
    Virtualenv   : /home/gamingstore7683/.virtualenvs/gamingstore
"""

import sys
import os
import glob

# 1) Make sure the project root is importable
PROJECT_ROOT = '/home/gamingstore7683/GAMING-S/gaming_store'
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2) Add the virtualenv's site-packages to sys.path (works for venv & virtualenv)
VENV_PATH = '/home/gamingstore7683/.virtualenvs/gamingstore'
for sp in glob.glob(os.path.join(VENV_PATH, 'lib', 'python3.*', 'site-packages')):
    if os.path.isdir(sp) and sp not in sys.path:
        sys.path.insert(0, sp)

# 2b) Bonus: run virtualenv's activate_this.py if it exists
ACTIVATE_THIS = os.path.join(VENV_PATH, 'bin', 'activate_this.py')
if os.path.exists(ACTIVATE_THIS):
    with open(ACTIVATE_THIS) as f:
        exec(f.read(), {'__file__': ACTIVATE_THIS})

# 3) Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
except Exception:
    pass

# 4) Expose the WSGI application
from run import app as application  # noqa
