#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import getLogger
from logging import FileHandler

from waitress import serve
from paste.translogger import TransLogger

from app import create_app
from conf import conf


if __name__ == "__main__":
    # 로거 핸들러 가져오기, 파일 핸들러 등록하기
    logger = getLogger("wsgi")
    logger.addHandler(FileHandler("wsgi.log"))

    # `conf/server.ini`에 설정된 포트로 웹 서버 시작
    serve(
        app=TransLogger(
            application=create_app()
        ),
        port=conf['server']['port'],
    )
