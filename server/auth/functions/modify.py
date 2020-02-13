import datetime
from flask import request, session, jsonify
from passlib.hash import sha256_crypt

from server import db
from server.auth.models import User, user_schema

# Modify and existing user
def modify_func(email, password, name):
  users = User.query.filter(User.email == email)
  user = users.first()

  if not user:
    return jsonify({ 'error': 'Email does not exist' }), 400

  if not password or not sha256_crypt.verify(password, user.password):
    return jsonify({ 'error': 'Invalid Password' }), 400

  if name:
    user.name = name
    user.updated_at = datetime.datetime.utcnow()
    db.session.commit() 

  return user_schema.jsonify(user), 201

# Delete an existing user
def delete_func(email, password):
  users = User.query.filter(User.email == email)
  user = users.first()

  if not user:
    return jsonify({ 'error': 'Email does not exist' }), 400

  if not password or not sha256_crypt.verify(password, user.password):
    return jsonify({ 'error': 'Invalid Password' }), 400
  
  session.clear()
  users.delete()
  db.session.commit()

  return jsonify({ 'message': 'Deleted ' + email + ' succesfully' })

# Get an existing user
def get_func(email):
  return user_schema.jsonify(User.query.filter(User.email == email).first())