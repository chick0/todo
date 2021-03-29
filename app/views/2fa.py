# -*- coding: utf-8 -*-
from io import BytesIO

from flask import Blueprint
from flask import request, session
from flask import redirect, url_for
from flask import send_file
from flask import render_template

from qrcode import make
from pyotp import TOTP, random_base32

from app import db
from models import Member

bp = Blueprint(
    name=__name__.split(".")[-1],
    import_name=__name__,
    url_prefix=f"/{__name__.split('.')[-1]}"
)


def get_secret():
    secret = session.get("2fa_secret", None)
    if secret is None:
        secret = random_base32()
        session['2fa_secret'] = secret

    return secret


@bp.route("/qrcode")
def qrcode():
    email = session.get("email", None)
    if email is None:
        return redirect(url_for("member.login", login="need"))

    img = BytesIO()
    make(f"otpauth://totp/{email}?secret={get_secret()}&issuer=Todo",
         border=0).save(img)
    img.seek(0)

    return send_file(
        img,
        mimetype="image/png"
    )


@bp.route("/setup", methods=['GET', 'POST'])
def setup():
    member = Member.query.filter_by(
        idx=session.get("user_idx", -1)
    ).first()
    if member is None:
        return redirect(url_for("member.login", login="need"))

    if len(member.secret) != 0:
        return redirect(url_for(".verify"))

    if request.method == "GET":
        session['2fa_secret'] = random_base32()
        return render_template(
            "2fa/setup.html"
        )
    elif request.method == "POST":
        otp_pin = request.form.get("otp_pin", None)
        if otp_pin is None:
            return redirect(url_for(".verify", e="missing"))

        secret = get_secret()
        result = TOTP(secret).verify(otp_pin)

        if not result:
            return redirect(url_for(".verify", e="fail"))

        session['2fa_status'] = True
        member.secret = secret
        db.session.commit()

        return redirect(url_for(".verify"))


@bp.route("/verify", methods=['GET', 'POST'])
def verify():
    member = Member.query.filter_by(
        idx=session.get("user_idx", -1)
    ).first()
    if member is None:
        return redirect(url_for("member.login", login="need"))

    if len(member.secret) == 0:
        return redirect(url_for(".setup"))

    if session.get("2fa_status", False):
        return redirect(url_for("todo.dashboard"))

    if request.method == "GET":
        return render_template(
            "2fa/verify.html"
        )
    elif request.method == "POST":
        otp_pin = request.form.get("otp_pin", None)
        if otp_pin is None:
            return redirect(url_for(".verify", e="missing"))

        result = TOTP(member.secret).verify(otp_pin)

        if not result:
            return redirect(url_for(".verify", e="fail"))

        session['2fa_status'] = True
        return redirect(url_for("todo.dashboard"))
