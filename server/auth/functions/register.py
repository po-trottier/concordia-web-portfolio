from flask import request, session, jsonify
from passlib.hash import sha256_crypt

from server import db
from server.auth.models import User, user_schema
from server.auth.functions.login import login_func

def register_func(email, password, name):
  user = User.query.filter(User.email == email).first()
  if user:
    return jsonify({ 'error': 'Email already in use' }), 400

  # Create the user
  new_user = User(email, password, name)
  token = new_user.generate_auth_token()
  new_user.session_token = token
  db.session.add(new_user)
  db.session.commit()

  # Login the user with the session token
  return login_func(email, None)