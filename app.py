from flask import Flask, render_template, request, redirect, url_for

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
      return redirect(url_for('contact', 
        name=request.form.get('name'),
        phone=request.form.get('phone'),
        email=request.form.get('email'),
        message=request.form.get('message')
      ))
  # Return the index.html file for any other type of request
  else:
    return render_template('routes/index.html')

@app.route('/contact')
def contact():
  form = { 
    'name': request.args.get('name'), 
    'phone': request.args.get('phone'),
    'email': request.args.get('email'),
    'message': request.args.get('message')
  }
  # Will need to add logic here
  return render_template('routes/contact.html', form=form)

@app.route('/blog')
def blog():
  # Will need to add logic here
  return render_template('routes/blog.html')

@app.route('/post/<int:post_id>')
def post(post_id):
  # Will need to add logic here
  return render_template('routes/post.html', id=post_id)

app.run(host='127.0.0.1', port=5000, debug=True)
