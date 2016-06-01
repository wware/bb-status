from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db_uri = 'mysql://buildbot_prod:buildbot_prod@amber-buildbot-1.veracode.local:3306/buildbot_prod_master'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)

class Buildrequests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buildsetid = db.Column(db.Integer, db.ForeignKey('buildsets.id'))
    buildername = db.Column(db.String(256))
    priority = db.Column(db.Integer)
    complete = db.Column(db.Integer)
    results = db.Column(db.Integer)
    submitted_at = db.Column(db.Integer)
    complete_at = db.Column(db.Integer)


class Buildsets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    external_idstring = db.Column(db.String(256))
    reason = db.Column(db.String(256))
    sourcestampsetid = db.Column(db.Integer)
    submitted_at = db.Column(db.Integer)
    complete = db.Column(db.Integer)
    complete_at = db.Column(db.Integer)
    results = db.Column(db.Integer)


class Builds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    brid = db.Column(db.Integer, db.ForeignKey('buildrequests.id'))
    start_time = db.Column(db.Integer)
    finish_time = db.Column(db.Integer)


class BuildsetProperties(db.Model):
    buildsetid = db.Column(db.Integer, db.ForeignKey('buildsets.id'), primary_key=True)
    property_name = db.Column(db.String(256), primary_key=True)
    property_value = db.Column(db.String(256))

class SourcestampChanges(db.Model):
    sourcestampid = db.Column(db.Integer, primary_key=True)
    changeid = db.Column(db.Integer)

class ChangeProperties(db.Model):
    changeid = db.Column(db.Integer, primary_key=True)
    property_name = db.Column(db.String(256))
    property_value = db.Column(db.String(1024))

class Changes(db.Model):
    changeid = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(256))
    comments = db.Column(db.String(256))
    is_dir = db.Column(db.Integer)
    branch = db.Column(db.String(256))
    revision = db.Column(db.String(256))
    revlink = db.Column(db.String(256))
    when_timestamp = db.Column(db.Integer)
    category = db.Column(db.String(256))
    repository = db.Column(db.String(512))
    project = db.Column(db.String(512))
    codebase = db.Column(db.String(256))

