import os
from flask import Flask
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')