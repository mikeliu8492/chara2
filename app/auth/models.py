import ldap
from flask_wtf import Form
from sqlalchemy.orm import relationship
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from app import db, app

from datetime import datetime


class User(db.Model):
   __tablename__ = 'user'
   id = db.Column(db.Integer, primary_key=True)
   question_id = relationship('Question', backref='person', uselist=False)
   course_id = db.Column(db.Integer, db.ForeignKey('queue.course_id'))

   netid = db.Column(db.String(8), unique=True, nullable=False)
   first_name = db.Column(db.String(16))
   last_name = db.Column(db.String(16))
   nickname = db.Column(db.String(16))
   location = db.Column(db.String(8))

   @staticmethod
   def try_login(netid, password):
      ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
      conn = ldap.initialize(app.config['AD_PROVIDER_URL'])
      conn.start_tls_s()
      conn.simple_bind_s(app.config['AD_BASE_DN'] % netid, password)

   @property
   def is_authenticated(self):
      return True

   @property
   def is_active(self):
      return True

   @property
   def is_anonymous(self):
      return False

   def __init__(self, netid):
      self.netid = netid

      l = ldap.initialize("ldap://ldap.illinois.edu:389")
      searchScope = ldap.SCOPE_SUBTREE
      retrieveAttributes = ['givenName', 'sn']
      searchFilter = "uid=" + netid

      try:
         ldap_result_id = l.search("OU=People,DC=uiuc,DC=edu", searchScope, searchFilter, retrieveAttributes)
         result_set = []
         while 1:
            result_type, result_data = l.result(ldap_result_id, 0)
            if not result_data:
               break
            else:
               if result_type == ldap.RES_SEARCH_ENTRY:
                  result_set.append(result_data)
         try:
            entry = result_set[0][0][1]
            self.first_name = entry['givenName'][0]
            self.last_name = entry['sn'][0]
         except:
            print("failed to parse name")
      except ldap.LDAPError, e:
         print e

   def get_id(self):
      return unicode(self.id)

   @property
   def full_name(self):
      return self.first_name + " " + self.last_name

   @property
   def email(self):
      return "%s@illinois.edu" % self.netid

   def __repr__(self):
      return '<User %r>' % self.netid


class Question(db.Model):
   __tablename__ = 'question'
   id = db.Column(db.Integer, primary_key=True)
   timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
   resolved = db.Column(db.Integer, nullable=False, default=0)

   user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
   queue_id = db.Column(db.Integer, db.ForeignKey('queue.id'), nullable=False)
   topic = db.Column(db.String(128), nullable=False)

   def __init__(self, user_id, queue_id, topic):
      self.user_id = user_id
      self.course_id = queue_id
      self.topic = topic

   def get_id(self):
      return unicode(self.id)

   def location(self):
      return "%s" % User.query.filter_by(id=self.user_id).first().location

   def user_full_name(self):
      return "%s" % User.query.filter_by(id=self.user_id).first().full_name

   def __repr__(self):
      return '<Question %s>' % self.topic

class Queue(db.Model):
   __tablename__ = 'queue'
   id = db.Column(db.Integer, primary_key=True)
   timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
   course_id = db.Column(db.String(16), unique=True, nullable=False)
   course_name = db.Column(db.String(64), unique=True)

   questions = relationship("Question", backref="queue")
   active_question_id = db.Column(db.Integer, nullable=True)
   users = relationship("User", backref="queue")

   def __init__(self, course_id):
      self.course_id = course_id

   def get_id(self):
      return unicode(self.id)


class LoginForm(Form):
   netid = StringField('netid', [InputRequired()])
   password = PasswordField('password', [InputRequired()])
