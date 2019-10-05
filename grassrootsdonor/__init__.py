from flask import Flask
app = Flask(__name__)
import grassrootsdonor.config as cfg
from grassrootsdonor import views


