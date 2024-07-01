from flask import Flask
from flask_mongoengine import MongoEngine
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
scheduler = BackgroundScheduler()
db = MongoEngine()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    from app.main import bp as main_blueprint
    app.register_blueprint(main_blueprint,url_prefix='/api')
    db.init_app(app)

    scheduler.start()
    return app