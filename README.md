# Flask Server Template

This is a simple Flask API Server that connects to a SQLite database using SQLAlchimist.

#### Features

* Flask MVC architecture
* User authorization and session management
* Simple setup and deployment

---

### Get Started

1) Install any version of `Python 3`
1) Make sure `pip` is installed
1) Install `pipenv` using `pip install pipenv` (if you are on Linux or macOS run the command as `sudo`)
1) Open a terminal/command-prompt window in the project folder
1) Run `pipenv shell` to enter the virtual environment shell
1) Run `pipenv install` to install the dependencies

### Setup the server

1) Add the `config.py` file to the `.gitignore` file 
1) Change the `config.py` file's `SECRET_KEY` to a proper secure key
  * If you're planning on deploying this project, also set `DEBUG = False`
1) Push the `config.py` file manually to your FTP if you want to host the project
1) Start the server with the `python run.py` command
