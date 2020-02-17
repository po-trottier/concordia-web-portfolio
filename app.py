from flask import Flask, render_template, request

# Initialize app
app = Flask(__name__,
            static_url_path='',
            static_folder='assets',
            template_folder='templates')

# Get Configuration File
app.config.from_object('config')

# Define the routes
@app.route('/', methods=['GET', 'POST'])
def home():
  # If we receive a POST request then it's a form submission
  if request.method == "POST":
    # If the anti-bot field is filled, a bot filled the form
    if request.form.get('subject') != '':
      return 'Bot Detected'
    # Otherwise deal with the form
    else:
      print(request.form)
      return render_template('routes/index.html')
  # Return the index.html file for any other type of request
  else:
    return render_template('routes/index.html')

@app.route('/blog')
def blog():
  # Will need to add logic here
  return render_template('routes/blog.html')

app.run(host='127.0.0.1', port=5000, debug=True)
