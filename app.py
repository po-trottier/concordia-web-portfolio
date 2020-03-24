##################################################################
#
# README
#
# There is an Admin area that is only linked in the footer.
# It is located at /admin and let's an admin manage the messages
# received as well as the posts visible on the website.
#
# Default Account
#
# Email: test@test.com
# Password: test
#
##################################################################

# Import Flask
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Import Python Packages
import datetime
import bcrypt

# Import Extra Dependencies
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

# Import Form Fields & Validators
from wtforms import StringField, TextAreaField
from wtforms.fields import PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, InputRequired

# Initialize app
app = Flask(__name__,
            static_url_path='',
            static_folder='assets',
            template_folder='templates')

#Initialize the Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure Bootstrap
Bootstrap(app)

# Get Configuration File
app.config.from_object('config')

# Initialize Database
db = SQLAlchemy(app)

# Initialize Database Models
class User(db.Model, UserMixin):
  id = db.Column(db.Integer(), primary_key=True)
  email = db.Column(db.String(128), nullable=False, unique=True)
  password = db.Column(db.String(64), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def get_id(self):
    return self.email

  def __init__(self, email, password):
    self.email = email
    self.password = password

  def __repr__(self):
    return '<User %r>' % (self.email)

class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False)
  phone = db.Column(db.String(16), nullable=True)
  email = db.Column(db.String(128), nullable=False)
  message = db.Column(db.Text, nullable=False)
  sent_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, name, phone, email, message):
    self.name = name
    self.phone = phone
    self.email = email
    self.message = message

  def __repr__(self):
    return '<Message #%r: %r>' % (self.id, self.message)

class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  author = db.Column(db.String(128))
  title = db.Column(db.String(512))
  content = db.Column(db.Text)
  published_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, author, title, content):
    self.author = author
    self.title = title
    self.content = content

  def __repr__(self):
    return '<Post %r>' % (self.id)

# Create form validators
class LoginForm(FlaskForm):
  email = EmailField('Email:', validators=[InputRequired(), Email()])
  password = PasswordField('Password:', validators=[InputRequired()])

class ContactForm(FlaskForm):
  name = StringField('Name:', validators=[InputRequired()])
  phone = StringField('Phone Number:', validators=[])
  email = EmailField('Email Address:', validators=[InputRequired(), Email()])
  message = TextAreaField('Message:', validators=[InputRequired()])

class PostForm(FlaskForm):
  author = StringField('Author:', validators=[InputRequired()])
  title = StringField('Title:', validators=[InputRequired()])
  content = TextAreaField('Content:', validators=[InputRequired()])

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(email=user_id).first()

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
  form = LoginForm()
  if request.method == "POST":
    if form.validate_on_submit():
      if User.query.filter_by(email=form.email.data).first():
        flash('User already exists. Please use a different email.')
        return render_template('routes/signup.html', form=form)
      salt = bcrypt.gensalt()
      hash = bcrypt.hashpw(form.password.data.encode(), salt)
      user = User(form.email.data, hash)
      db.session.add(user)
      db.session.commit()
      flash('User successfully created.')
      return redirect(url_for('admin'))
    else:
      flash('Invalid Form Data')
      return render_template('routes/signup.html', form=form)
  else:
    return render_template('routes/signup.html', form=form)

# Define the routes
@app.route('/', methods=['GET', 'POST'])
def home():
  form = ContactForm()
  # If we receive a POST request then it's a form submission
  if request.method == "POST":
    # Deal with the form
    if form.validate_on_submit():
      # Add the message to the DB
      message = Message(form.name.data, form.phone.data, form.email.data, form.message.data)
      db.session.add(message)
      db.session.commit()
      # Redirect
      return redirect(url_for('contact',
        name=form.name.data,
        phone=form.phone.data,
        email=form.email.data,
        message=form.message.data
      ))
    else:
      flash('Invalid Form Data')
      return render_template('routes/index.html', form=form)
  else:
    # Return the index.html file for any other type of request
    return render_template('routes/index.html', form=form)

@app.route('/contact')
def contact():
  form = {
    'name': request.args.get('name'),
    'phone': request.args.get('phone'),
    'email': request.args.get('email'),
    'message': request.args.get('message')
  }
  return render_template('routes/contact.html', form=form)

@app.route('/blog')
def blog():
  posts = Post.query.order_by(Post.published_at.desc()).all()
  return render_template('routes/blog.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
  post = Post.query.filter_by(id=post_id).first()
  return render_template('routes/post.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if request.method == "POST":
    if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      if user and bcrypt.checkpw(form.password.data.encode(), user.password):
        login_user(User.query.filter_by(email=form.email.data).first(), remember=True)
        next_page = session.get('next', url_for('home'))
        session['next'] = url_for('home')
        return redirect(next_page)
      else:
        flash('Incorrect email or password')
        return render_template('routes/login.html', form=form)
    else:
      flash('Invalid Form Data')
      return render_template('routes/login.html', form=form)
  else:
    return render_template('routes/login.html', form=form)

@app.route('/logout')
def logout():
  logout_user()
  flash('Succesfully logged out!')
  return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin():
  # Query messages and posts
  messages = list(Message.query.order_by(Message.sent_at.desc()).all())
  posts = list(Post.query.order_by(Post.published_at.desc()).all())
  # Render a list of all the messages & posts in the DB
  return render_template('routes/admin.html', messages=messages, posts=posts)

@app.route('/admin/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
  form = PostForm()
  # If this is a POST request, we're getting data from the form
  if request.method == "POST":
    if form.validate_on_submit():
      # Add a new post to the DB
      post = Post(form.author.data, form.title.data, form.content.data)
      db.session.add(post)
      db.session.commit()
      # Render a list of all the messages & posts in the DB
      return redirect(url_for('admin'))
    else:
      flash('Invalid Form Data')
      return render_template('routes/add-post.html', form=form)
  # Otherwise render the add-post page
  else:
    return render_template('routes/add-post.html', form=form)

@app.route('/admin/posts/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
  # Delete the requested message
  post = Post.query.filter_by(id=post_id).first()
  db.session.delete(post)
  db.session.commit()
  # Render a list of all the messages & posts in the DB
  return redirect(url_for('admin'))

@app.route('/admin/messages/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
  # Delete the requested message
  message = Message.query.filter_by(id=message_id).first()
  db.session.delete(message)
  db.session.commit()
  # Render a list of all the messages & posts in the DB
  return redirect(url_for('admin'))

# Build the database
db.create_all()

app.run(host='127.0.0.1', port=5000, debug=True)
