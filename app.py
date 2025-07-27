from flask import Flask
from routes import setup_routes
from models import *
from cache import cache
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600
cache.init_app(app)

with app.app_context():
    db.create_all()

setup_routes(app, db)

if __name__ == '__main__':
    app.run(debug=True)
