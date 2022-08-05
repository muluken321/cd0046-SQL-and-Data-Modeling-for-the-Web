import os
from flask import Flask

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456@localhost:5432/fyyur_db'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
