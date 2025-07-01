from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from routes import setup_routes
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

setup_routes(app, db)

if __name__ == '__main__':
    app.run(debug=True)
