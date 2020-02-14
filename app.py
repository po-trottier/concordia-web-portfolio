from flask import Flask, render_template

# Initialize app
app = Flask(__name__,
            static_url_path='',
            static_folder='assets',
            template_folder='templates')

# Get Configuration File
app.config.from_object('config')

# Define the routes
@app.route('/')
def home():
  return render_template('routes/index.html')
@app.route('/blog')
def blog():
  return render_template('routes/blog.html')

app.run(host='127.0.0.1', port=5000, debug=True)
