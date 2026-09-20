from flask import Flask

from api_gateway.routes import gateway_routes


def create_app():
    app = Flask(__name__)

    app.register_blueprint(gateway_routes)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)