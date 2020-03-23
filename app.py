# Import Flask
from flask import Flask, render_template, request, redirect, url_for

# Import Python Packages
import datetime

# Import Extra Dependencies
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm

# Import Form Fields & Validators
from wtforms import StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, InputRequired

# Initialize app
app = Flask(__name__,
            static_url_path='',
            static_folder='assets',
            template_folder='templates')

# Configure Bootstrap
Bootstrap(app)

# Get Configuration File
app.config.from_object('config')

# Initialize Database
db = SQLAlchemy(app)

# Initialize Database Models
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

# Create a form validator
class ContactForm(FlaskForm):
  name = StringField('Name:', validators=[InputRequired()])
  phone = StringField('Phone Number:', validators=[])
  email = EmailField('Email Address:', validators=[InputRequired(), Email()])
  message = TextAreaField('Message:', validators=[InputRequired()])

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
  # Will need to add logic here
  return render_template('routes/blog.html')

@app.route('/post/<int:post_id>')
def post(post_id):
  # Will need to add logic here
  return render_template('routes/post.html', id=post_id)

# This route is only to show that the database is correctly setup
@app.route('/admin')
def admin():
  results = list(Message.query.all())
  # Render a list of all the messagesin the DB
  return render_template('routes/admin.html', messages=results)

# Build the database
db.create_all()

app.run(host='127.0.0.1', port=5000, debug=True)
