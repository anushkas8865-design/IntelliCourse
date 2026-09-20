from flask import Flask

from services.ai_service.routes import ai_routes


def create_app():
    app = Flask(__name__)

    app.register_blueprint(ai_routes)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5003, debug=True)