Buildbot Status Thing
=====================

This is a WSGI app that Ken set up on the Buildbot system. He put this
in the /var/www/wsgi directory in an Apache setup.

This stuff goes in /etc/httpd/conf/httpd.conf.
```
# Buildbot info, status, and report pages
WSGIPythonHome /var/www/wsgi/flask
WSGIDaemonProcess bb-reports user=apache group=apache threads=5
WSGIScriptAlias /bb-reports /var/www/wsgi/bb-reports/bb-reports.wsgi
WSGISocketPrefix /var/www/wsgi/
<Directory /var/www/wsgi/bb-reports>
    WSGIProcessGroup bb-reports
    WSGIApplicationGroup %{GLOBAL}
    Order deny,allow
    Allow from all
</Directory>
<Directory /var/www/wsgi/bb-reports/app>
    WSGIProcessGroup bb-reports
    WSGIApplicationGroup %{GLOBAL}
    Order deny,allow
    Allow from all
</Directory>

# Buildbot artifacts
<Directory /artifacts>
    Options Indexes FollowSymLinks
    AllowOverride None
    Order deny,allow
    Allow from all
</Directory>
Alias /artifacts /artifacts
```

See that `WSGIPythonHome` thing? That is likely to change because I discarded
a bunch of pip-installed stuff that was in a `flask` directory, figuring it
didn't belong in a source repository. It might be reconstructable like this:

```
cd /var/www/wsgi
# unpack all this stuff
virtualenv flask
source flask/bin/activate
pip install -r requirements.txt
deactivate
```
