from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db  = SQLAlchemy()
mg  = Migrate()
bc  = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    CORS(app,
         origins=[
            "http://localhost:5173",
            "https://voteright.onrender.com",
         ],
         supports_credentials=True)

    db.init_app(app)
    mg.init_app(app, db)
    bc.init_app(app)
    jwt.init_app(app)

    # 👇 MOVE THIS IMPORT INSIDE THE FUNCTION
    from app import models

    from app.auth   import auth_bp
    from app.routes import poll_bp
    from app.admin  import admin_bp

    app.register_blueprint(auth_bp,   url_prefix="/api/auth")
    app.register_blueprint(poll_bp,   url_prefix="/api/polls")
    app.register_blueprint(admin_bp,  url_prefix="/api")

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return {"message": "API is running"}

    return app
