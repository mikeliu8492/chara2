import ldap
from flask import request, render_template, flash, redirect, url_for, \
   Blueprint, g
from flask_login import current_user, login_user, logout_user, \
   login_required
from app import login_manager, db
from app.auth.models import User, LoginForm, Question, Queue

auth = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(id):
   return User.query.get(id)


@auth.before_request
def get_current_user():
   g.user = current_user


@auth.route('/')
@auth.route('/home')
def home():
   return render_template('home.html')


@auth.route('/queue/<course_id>')
def queue(course_id):
   if (course_id != 'select'):
      queue = Queue.query.filter_by(course_id=course_id).first()
      if (queue == None):
         return render_template('notfound.html')
      current_user.course_id = queue.course_id
      queue.questions.sort(key=lambda question: question.timestamp)
      return render_template('queue.html', course_id=course_id, course_name=queue.course_name,
                             questions=queue.questions)
   else:
      return render_template('queue.html', course_id=course_id)


@login_required
@auth.route('/queue/<course_id>', methods=['POST'])
def new_question(course_id):

   queue = Queue.query.filter_by(course_id=course_id).first()
   if (queue == None):
      return render_template('notfound.html')

   if current_user.question_id == None:
      question = Question(current_user.id, queue.id, request.form['topic'])
      queue.questions.append(question)
      current_user.question_id = question.id
      db.session.add(question)
      db.session.commit()

   return render_template('queue.html', course_id=course_id, course_name=queue.course_name,
                             questions=queue.questions)


@auth.route('/gradebook')
def gradebook():
   return render_template('gradebook.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
   if current_user.is_authenticated:
      flash('You are already logged in.')
      return redirect(url_for('auth.home'))

   form = LoginForm(request.form)

   if request.method == 'POST' and form.validate():
      netid = request.form['netid']
      password = request.form['password']

      try:
         User.try_login(netid, password)
      except ldap.INVALID_CREDENTIALS:
         flash('Invalid netid or password. Please try again.', 'danger')
         return render_template('login.html', form=form)

      user = User.query.filter_by(netid=netid).first()

      if not user:
         user = User(netid)
         db.session.add(user)
         db.session.commit()
      login_user(user)
      flash('You have successfully logged in.', 'success')
      return redirect(url_for('auth.home'))

   if form.errors:
      flash(form.errors, 'danger')

   return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('auth.home'))


@auth.route('/')
@auth.route('/notfound')
def notfound():
   return render_template('notfound.html')


