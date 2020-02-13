from flask import request, session, jsonify
from passlib.hash import sha256_crypt

from server import db
from server.auth.models import User, user_schema
from server.auth.functions.refresh import refresh_func

def login_func(email, password):
  token = session.get('token')
  user = User.query.filter(User.email == email).first()

  # If the user has a valid auth token then refresh it
  if not password and token:
    response = refresh_func(email)
    # If we succesfully logged in using the session token 
    if response.status_code == 200:
      return response

  if not user:
    return jsonify({ 'error': 'Invalid Email' }), 400
  if not password or not sha256_crypt.verify(password, user.password):
    return jsonify({ 'error': 'Invalid Password' }), 400
  
  token = user.generate_auth_token()
  user.session_token = token
  db.session.commit()

  session['logged_in'] = True
  session['email'] = user.email
  session['name'] = user.name
  session['token'] = user.session_token

  return user_schema.jsonify(user)