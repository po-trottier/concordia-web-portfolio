###########################################
# To use this file, simply rename it to
# config.py and change the MailJet key
# and secret to proper value.
###########################################


import os

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'data', 'db.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret key for signing cookies
SECRET_KEY = 'T^Bru8XwE4WYatyxIRP*T1QA#GZ%b7NS'

# Login Manager Option
USE_SESSION_FOR_NEXT = True

# Mailjet Keys
MAILJET_API_KEY = 'PUT KEY HERE'
MAILJET_API_SECRET = 'PUT SECRET HERE'
