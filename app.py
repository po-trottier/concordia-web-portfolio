from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
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

# Initialize Marshmallow
ma = Marshmallow(app)

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

# Build the database
db.create_all()

app.run(host='127.0.0.1', port=5000, debug=True)
