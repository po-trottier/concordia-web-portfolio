from flask import request, session, jsonify

from server import db
from server.auth.models import User, user_schema

# Refresh the token for the current email
def refresh_func(email):
  if not email:
    email = session.get('email')
  token = session.get('token')
  user = User.query.filter(User.email == email).first()

  if not user or not token or not user.verify_auth_token(token):
    return jsonify({ 'error': 'Invalid Session Token' }), 400

  # If the user has a valid auth token then refresh it
  else:
    session.clear()
    token = user.generate_auth_token()
    user.session_token = token
    db.session.commit()

    session['logged_in'] = True
    session['email'] = user.email
    session['name'] = user.name
    session['token'] = user.session_token

    return user_schema.jsonify(user)