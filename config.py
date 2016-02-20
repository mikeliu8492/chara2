import os
basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'chara'
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'csrf-chara'

LDAP_PROTOCOL_VERSION = 3
AD_PROVIDER_URL = 'ldap://ad.uillinois.edu:389/'
AD_BASE_DN = 'cn=%s,OU=People,DC=ad,DC=uillinois,DC=edu'
LDAP_PROVIDER_URL = 'ldap://ldap.illinois.edu:389'
LDAP_BASE_DN = 'OU=People,DC=uiuc,DC=edu'
if os.environ.get('DATABASE_URL') is None:
   print("database url not found")
   SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
   SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True