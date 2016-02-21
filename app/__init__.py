
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app.auth.views import auth
app.register_blueprint(auth)
db.create_all()
"""
from app.auth import models
if models.Queue.query.count() == 0:
   courses = [('CS125', 'Introduction to Programming'),
              ('CS225', 'Data Structures and Programming Principles'),
              ('CS233', 'Computer Architecture'),
              ('CS241', 'Systems Programming'),
              ('ECE391', 'Computer Systems Engineering'),
            ]
   for course in courses:
      queue = models.Queue(course[0])
      queue.course_name = course[1]
      db.session.add(queue)
   db.session.commit()
"""