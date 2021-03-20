# -*- coding: utf-8 -*-
from io import BytesIO

from flask import Flask
from flask import request
from flask import send_file
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.module import error
from conf import conf

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = conf['db']['url']
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    except KeyError:
        raise Exception("데이터베이스 접속 링크를 전달받지 못함")

    try:
        app.config['SECRET_KEY'] = open(".SECRET_KEY", mode="rb").read()
    except FileNotFoundError:
        from secrets import token_bytes
        app.config['SECRET_KEY'] = token_bytes(32)
        open(".SECRET_KEY", mode="wb").write(app.config['SECRET_KEY'])

    @app.route("/robots.txt")
    def robots():
        return send_file(
            BytesIO(b"\n".join([
                b"User-agent: *",
                b"Allow: /$",
                b"Disallow: /",
            ])),
            mimetype="text/plain"
        )

    @app.before_request
    def for_uptime_bot():
        if "Uptime" in request.user_agent.string:
            return "OK", 200

    @app.after_request
    def set_header(response):
        response.headers['X-Frame-Options'] = "deny"  # Clickjacking
        response.headers['X-Powered-By'] = "chick_0"
        return response

    # DB 모델 등록
    __import__("models")

    # ORM 등록 & 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    from app import views
    for view_point in views.__all__:
        app.register_blueprint(
            blueprint=getattr(getattr(views, view_point), "bp")
        )

    app.add_template_filter(lambda dt: dt.strftime("%Y-%m-%d"), "date")

    # 오류 핸들러
    app.register_error_handler(400, error.bad_request)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(403, error.forbidden)
    app.register_error_handler(404, error.page_not_found)
    app.register_error_handler(405, error.method_not_allowed)
    app.register_error_handler(413, error.request_entity_too_large)

    app.register_error_handler(500, error.internal_server_error)

    return app
