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

