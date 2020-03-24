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
import uuid

# Import Extra Dependencies
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from mailjet_rest import Client

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
  reset_token = db.Column(db.String(64), nullable=True)
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

# Create forms
class LoginForm(FlaskForm):
  email = EmailField('Email:', validators=[InputRequired(), Email()])
  password = PasswordField('Password:', validators=[InputRequired()])

class ResetForm(FlaskForm):
  name = StringField('Name:', validators=[InputRequired()])
  email = EmailField('Email:', validators=[InputRequired(), Email()])

class ContactForm(FlaskForm):
  name = StringField('Name:', validators=[InputRequired()])
  phone = StringField('Phone Number:', validators=[])
  email = EmailField('Email Address:', validators=[InputRequired(), Email()])
  message = TextAreaField('Message:', validators=[InputRequired()])

class PostForm(FlaskForm):
  author = StringField('Author:', validators=[InputRequired()])
  title = StringField('Title:', validators=[InputRequired()])
  content = TextAreaField('Content:', validators=[InputRequired()])

# Set custom load_user method for flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(email=user_id).first()

# Define the routes for the app
# Home page
@app.route('/', methods=['GET', 'POST'])
def home():
  form = ContactForm()
  # If we receive a POST request then it's a contact form submission
  if request.method == "POST":
    # Deal with the form
    if form.validate_on_submit():
      # Add the message to the DB
      message = Message(form.name.data, form.phone.data, form.email.data, form.message.data)
      db.session.add(message)
      db.session.commit()
      # Redirect to success page
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

# Successfully sent message page
@app.route('/contact')
def contact():
  form = {
    'name': request.args.get('name'),
    'phone': request.args.get('phone'),
    'email': request.args.get('email'),
    'message': request.args.get('message')
  }
  return render_template('routes/contact.html', form=form)

# Contains blog posts
@app.route('/blog')
def blog():
  posts = Post.query.order_by(Post.published_at.desc()).all()
  return render_template('routes/blog.html', posts=posts)

# Single blog post
@app.route('/post/<int:post_id>')
def post(post_id):
  post = Post.query.filter_by(id=post_id).first()
  return render_template('routes/post.html', post=post)

# Login as an admin
@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  # If the request is a POST request then it's a form submission
  if request.method == "POST":
    if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      # If the user exists and the password is valid then log in
      if user and bcrypt.checkpw(form.password.data.encode(), user.password):
        # When a user logs in, remove any pending reset_token
        if user.reset_token:
          user.reset_token = None
          db.session.commit()
        # Log in user and remember in the cookies
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

# Log out user
@app.route('/logout')
def logout():
  logout_user()
  flash('Succesfully logged out!')
  return redirect(url_for('home'))

# Create a new administrator
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
  form = LoginForm()
  # If the request is a POST request then it's a form submission
  if request.method == "POST":
    if form.validate_on_submit():
      # Make sure the emails are unique
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

# Reset forgotten password
@app.route('/reset', methods=['GET', 'POST'])
def reset():
  form = ResetForm()
  # If the request is a POST request then it's a form submission
  if request.method == "POST":
    if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      if not user:
        flash('There are no users associated with the email provided')
        return render_template('routes/reset.html', form=form)
      # Generate a unique ID that will serve as reset_token
      token = uuid.uuid4().hex[:16].lower()
      user.reset_token = token
      db.session.commit()
      # Create the reset URL dynamically
      url = request.url_root + 'reset/' + token
      # Send the email using MailJet
      mailjet = Client(auth=(app.config["MAILJET_API_KEY"], app.config["MAILJET_API_SECRET"]), version='v3.1')
      data = {
        'Messages': [
          {
            "From": { "Email": "po.trottier@gmail.com", "Name": "Pierre-Olivier" },
            "To": [{ "Email": form.email.data }],
            "Subject": "[PO_Design] Password Reset Link",
            "HTMLPart": "<h2>Hello " + form.name.data + ",</h2><p>We recently received a password reset request regarding your account as a PO_Design administrator.</p><p>To reset your password, please open the following link in your web browser.</p><a href=" + url + ">" + url + "</a>"
          }
        ]
      }
      mailjet.send.create(data=data)
      flash('The recovery email was successfully sent')
      return redirect(url_for('login'))
    else:
      flash('Invalid Form Data')
      return render_template('routes/reset.html', form=form)
  else:
    return render_template('routes/reset.html', form=form)

# Password change page
@app.route('/reset/<reset_token>', methods=['GET', 'POST'])
def change(reset_token):
  form = LoginForm()
  # If the request is a POST request then it's a form submission
  if request.method == "POST":
    if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      if not user:
        flash('There are no users associated with the email provided')
        return render_template('routes/change.html', form=form)
      if not user.reset_token == reset_token:
        flash('The reset token for the requested user has been invalidated')
        return redirect(url_for('login'))
      salt = bcrypt.gensalt()
      hash = bcrypt.hashpw(form.password.data.encode(), salt)
      user.password = hash
      user.reset_token = None
      db.session.commit()
      flash('The password was successfully changed')
      return redirect(url_for('login'))
    else:
      flash('Invalid Form Data')
      return render_template('routes/change.html', form=form)
  else:
    return render_template('routes/change.html', form=form, reset_token=reset_token)

# Administration Dashbard
@app.route('/admin')
@login_required
def admin():
  # Query messages and posts
  messages = list(Message.query.order_by(Message.sent_at.desc()).all())
  posts = list(Post.query.order_by(Post.published_at.desc()).all())
  # Render a list of all the messages & posts in the DB
  return render_template('routes/admin.html', messages=messages, posts=posts)

# Add a new post to the blog
@app.route('/admin/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
  form = PostForm()
  # If the request is a POST request then it's a form submission
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

# Delete a given post
@app.route('/admin/posts/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
  # Delete the requested message
  post = Post.query.filter_by(id=post_id).first()
  db.session.delete(post)
  db.session.commit()
  # Render a list of all the messages & posts in the DB
  return redirect(url_for('admin'))

# Delete a given message
@app.route('/admin/messages/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
  # Delete the requested message
  message = Message.query.filter_by(id=message_id).first()
  db.session.delete(message)
  db.session.commit()
  # Render a list of all the messages & posts in the DB
  return redirect(url_for('admin'))

# Build the database tables
db.create_all()

# Run the debug server
app.run(host='127.0.0.1', port=5000, debug=True)
