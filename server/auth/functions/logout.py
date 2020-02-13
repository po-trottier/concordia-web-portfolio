from flask import session, jsonify

from server import db
from server.auth.models import User

def logout_func():
  if not session.get('logged_in'):
    return jsonify({ 'error': 'Not logged in' }), 400

  # Clear the session token
  user = User.query.filter(User.email == session.get('email')).first()
  user.session_token = ''
  db.session.commit()

  # Close the session
  session.clear()
  return jsonify({ 'message': 'Successfuly logged out' })