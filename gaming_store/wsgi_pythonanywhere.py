"""
Corrected WSGI file for PythonAnywhere deployment.

PASTE THIS ENTIRE CONTENT into your PythonAnywhere WSGI file at:
    /var/www/gamingstore7683_pythonanywhere_com_wsgi.py

It auto-detects your project folder and virtualenv, puts them on sys.path,
loads your .env, creates DB tables if missing (SQLite safe), and exposes the
WSGI application. This fixes both "ModuleNotFoundError: No module named 'flask'"
and the "502-backend" worker-crash errors.

You do NOT need to edit any paths below — it searches common locations.
"""

import sys
import os
import glob

HOME = '/home/gamingstore7683'

# 1) Auto-detect the project root (the folder that contains run.py AND app/__init__.py)
CANDIDATE_ROOTS = [
    os.path.join(HOME, 'GAMING-S', 'gaming_store'),
    os.path.join(HOME, 'GAMING SW', 'gaming_store'),
    os.path.join(HOME, 'gaming_store'),
    os.path.join(HOME, 'GAMING-S'),
    os.path.join(HOME, 'GAMING SW'),
    os.path.join(HOME, 'mysite', 'gaming_store'),
    os.path.join(HOME, 'mysite'),
]
PROJECT_ROOT = None
for cand in CANDIDATE_ROOTS:
    if os.path.isfile(os.path.join(cand, 'run.py')) and os.path.isfile(os.path.join(cand, 'app', '__init__.py')):
        PROJECT_ROOT = cand
        break

# Fallback: search the whole HOME tree for the real project root, regardless of
# the folder name you uploaded it to. Skips hidden / virtualenv folders for speed.
if PROJECT_ROOT is None:
    for root, dirs, files in os.walk(HOME):
        if any(seg.startswith('.') for seg in root.split(os.sep)[1:]):
            continue
        if 'run.py' in files and os.path.isfile(os.path.join(root, 'app', '__init__.py')):
            PROJECT_ROOT = root
            break

if PROJECT_ROOT is None:
    # Last resort: just use the most likely path
    PROJECT_ROOT = os.path.join(HOME, 'GAMING-S', 'gaming_store')

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2) Auto-detect the virtualenv and add its site-packages to sys.path
CANDIDATE_VENVS = [
    os.path.join(HOME, '.virtualenvs', 'gamingstore'),
    os.path.join(HOME, 'venv'),
    os.path.join(HOME, '.venv'),
    os.path.join(PROJECT_ROOT, 'venv'),
    os.path.join(PROJECT_ROOT, '.venv'),
]
VENV_PATH = None
for cand in CANDIDATE_VENVS:
    if os.path.isdir(cand):
        VENV_PATH = cand
        break

if VENV_PATH is None:
    # Search .virtualenvs for any env
    venvs_dir = os.path.join(HOME, '.virtualenvs')
    if os.path.isdir(venvs_dir):
        subs = [os.path.join(venvs_dir, d) for d in os.listdir(venvs_dir)
                if os.path.isdir(os.path.join(venvs_dir, d))]
        if subs:
            VENV_PATH = subs[0]

if VENV_PATH:
    for sp in glob.glob(os.path.join(VENV_PATH, 'lib', 'python3.*', 'site-packages')):
        if os.path.isdir(sp) and sp not in sys.path:
            sys.path.insert(0, sp)
    # Bonus: run virtualenv's activate_this.py if it exists
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

# 4) Expose the WSGI application (with a safe fallback import)
try:
    from run import app as application  # noqa
except Exception:
    from app import create_app
    application = create_app('default')  # noqa

# 5) Create tables if they don't exist yet (safe for SQLite; no-op if present).
#    This avoids "no such table" 500s on a fresh deploy.
try:
    with application.app_context():
        from app import db
        db.create_all()
except Exception:
    pass
