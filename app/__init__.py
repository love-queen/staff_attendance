from flask import Flask

app = Flask(__name__)

# Set secret key for session and flash messages
app.secret_key = "admin_harvesters"

from app import routes

