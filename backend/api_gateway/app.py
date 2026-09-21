from flask import Flask
from flask_cors import CORS

from api_gateway.routes import gateway_routes


def create_app():
    app = Flask(__name__)

    CORS(
        app,
        resources={r"/api/*": {"origins": [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "OPTIONS"],
    )

    app.register_blueprint(gateway_routes)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)