"""
WSGI entry point for PythonAnywhere deployment.

On PythonAnywhere, point your Web app's WSGI file to this file (or copy its
contents). It ensures the project root is on sys.path and exposes `application`.

Typical PythonAnywhere WSGI file:

    import sys
    path = '/home/youruser/gaming_store'   # the folder containing this wsgi.py
    if path not in sys.path:
        sys.path.insert(0, path)

    from wsgi import application
"""
import os
import sys

# Project root = the directory that contains this wsgi.py (i.e. gaming_store/)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
except Exception:
    pass

from app import create_app

# Use 'production' config on PythonAnywhere; override via the CONFIG_NAME env var.
config_name = os.environ.get('CONFIG_NAME', 'production')
application = create_app(config_name)
