from flask import Flask
app = Flask(__name__)
from myflask import views
from myflask import pipeline