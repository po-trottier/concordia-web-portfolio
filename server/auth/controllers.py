from flask import Blueprint, request, jsonify
from passlib.hash import sha256_crypt

from server.auth.models import User, users_schema
from server.auth.functions.login import login_func
from server.auth.functions.logout import logout_func
from server.auth.functions.register import register_func
from server.auth.functions.refresh import refresh_func
from server.auth.functions.modify import modify_func, delete_func, get_func

# Define the blueprint: 'auth', set its url prefix: app.url/auth
auth = Blueprint('auth', __name__, url_prefix='/')

# Register a New User
@auth.route('/register', methods=['POST'])
def register():
  return register_func(
    request.json.get('email'), 
    sha256_crypt.hash(request.json.get('password')),
    request.json.get('name')
  )

# Login an Existing User
@auth.route('/login', methods=['POST'])
def login():
  return login_func(
    request.json.get('email'), 
    request.json.get('password')
  )

# Refresh an Existing User Login
@auth.route('/refresh', methods=['POST'])
def refresh():
  return refresh_func()
  
# Logout Current User
@auth.route('/logout', methods=['POST'])
def logout():
  return logout_func()

# Get, Modify or Delete an Existing User
@auth.route('/user', methods=['GET', 'PUT', 'DELETE'])
def user():
  email = request.json.get('email')
  password = request.json.get('password')
  name = request.json.get('name')

  # Modify user by email
  if request.method == 'PUT':
    return modify_func(email, password, name)

  # Delete user by email
  if request.method == 'DELETE':
    return delete_func(email, password)

  # Get user by email
  else:
    return get_func(email)

# Get all Users
@auth.route('/users', methods=['GET'])
def users():
  all_users = User.query.all()
  return jsonify(users_schema.dump(all_users))