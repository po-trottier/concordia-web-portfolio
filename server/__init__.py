from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Initialize app
app = Flask(__name__)

# Configuration
app.config.from_object('config')

# Initialize Database
db = SQLAlchemy(app)

#Initialize Marshmallow
ma = Marshmallow(app)

# Home Page
@app.route('/', methods=['GET'])
def home():
  return render_template('index.html')

# Import modules using blueprints
from server.auth.controllers import auth

# Register blueprints
app.register_blueprint(auth)

# Build the database
db.create_all()