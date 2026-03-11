import os

from flask import Flask
from flask_cors import CORS

from core.config import UPLOAD_DIR
from core.db import init_db
from routes.auth_routes import auth_bp
from routes.history_routes import history_bp
from routes.predict_routes import predict_bp
from routes.report_routes import report_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, "gradcam"), exist_ok=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(report_bp)
    return app


app = create_app()


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
