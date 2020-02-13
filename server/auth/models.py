import datetime
from flask import session
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

from server import app, db, ma

# Define the User Class
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  password = db.Column(db.String(128))
  email = db.Column(db.String(128), unique=True)
  name = db.Column(db.String(128))
  session_token = db.Column(db.String(256))
  created_at = db.Column(db.DateTime, default = datetime.datetime.utcnow)
  updated_at = db.Column(db.DateTime, default = datetime.datetime.utcnow)

  def __init__(self, email, password, name):
    self.email = email
    self.password = password
    self.name = name

  def __repr__(self):
    return '<User %r>' % (self.name)    

  # Tokens expire after 1 month
  def generate_auth_token(self, expiration = app.config['TOKEN_EXPIRATION']):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

  @staticmethod
  def verify_auth_token(token):
      s = Serializer(app.config['SECRET_KEY'])
      try:
          data = s.loads(token)
      except SignatureExpired:
          return None # valid token, but expired
      except BadSignature:
          return None # invalid token
      user = User.query.get(data['id'])
      return user

# Define the User Schema
class UserSchema(ma.Schema):
  class Meta:
    fields = ('id', 'email', 'name', 'session_token', 'created_at', 'updated_at')

# Instantiate the Schema
user_schema = UserSchema()
users_schema = UserSchema(many = True)