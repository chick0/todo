# -*- coding: utf-8 -*-

from flask import render_template


def render(error, message):
    return render_template(
        "error/error.html",
        message=message
    ), getattr(error, "code")  # `werkzeug`의 오류 클래스에 있는 응답 코드를 가져옴 (werkzeug.exceptions 참고)

# # # # # # # # # # # # # # # # # # # # # #


def bad_request(error):
    return render(error, "잘못된 요청입니다")


def unauthorized(error):
    return render(error, "유효한 인증 자격이 없습니다")


def forbidden(error):
    return render(error, "해당 페이지를 볼 수 있는 권한이 없습니다")


def page_not_found(error):
    return render(error, "해당 페이지를 찾을 수 없습니다")


def method_not_allowed(error):
    return render(error, "잘못된 요청 방법 입니다")


def request_entity_too_large(error):
    return render(error, "업로드 하려는 파일의 크기가 허용 용량을 초과하고 있습니다")


def internal_server_error(error):
    return render(error, "내부 스크립트 오류가 발생하였습니다")
