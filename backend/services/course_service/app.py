import os

from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from services.course_service.routes import course_routes


load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    JWTManager(app)

    app.register_blueprint(course_routes)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5002,
        debug=True,
    )