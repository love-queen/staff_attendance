from flask import Flask
from app.routes import main

app = Flask(__name__)
app.secret_key = "admin_harvesters"
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)

