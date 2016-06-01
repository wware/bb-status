import sys
import os


sys.path.insert(0, '/var/www/wsgi/bb-reports')
os.chdir('/var/www/wsgi/bb-reports')
from app import app as application

