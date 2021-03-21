# -*- coding: utf-8 -*-
from hashlib import sha384, sha512

from flask import Blueprint
from flask import request, session
from flask import redirect, url_for
from flask import render_template
from sqlalchemy.exc import IntegrityError

from app import db
from models import Member


bp = Blueprint(
    name=__name__.split(".")[-1],
    import_name=__name__,
    url_prefix=f"/{__name__.split('.')[-1]}"
)


@bp.route("/logout")
def logout():
    try:
        del session['user_idx']
    except KeyError:
        pass

    return redirect(url_for(".login", login="need"))


@bp.route("/login", methods=['GET', 'POST'])
def login():
    if session.get("user_idx", None) is not None:
        return redirect(url_for("todo.dashboard"))

    if request.method == "GET":
        return render_template(
            "member/login.html"
        )
    elif request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        if len(email) == 0 or len(password) <= 5:
            return redirect(url_for(".login", login="cancel"))

        member = Member.query.filter_by(
            email=sha384(email.encode()).hexdigest(),
            password=sha512(password.encode()).hexdigest()
        ).first()

        if member is None:
            return redirect(url_for(".login", login="unregistered"))

        session['user_idx'] = member.idx

        return redirect(url_for("todo.dashboard"))


@bp.route("/register", methods=['GET', 'POST'])
def register():
    if session.get("user_idx", None) is not None:
        return redirect(url_for("todo.dashboard"))

    if request.method == "GET":
        return render_template(
            "member/register.html"
        )
    elif request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        if len(email) == 0:
            return redirect(url_for(".register", e="en"))

        if len(password) < 8:
            return redirect(url_for(".register", e="pws"))

        hashed_email = sha384(email.encode()).hexdigest()
        hashed_password = sha512(password.encode()).hexdigest()

        member = Member()
        member.email = hashed_email
        member.password = hashed_password

        try:
            db.session.add(member)
            db.session.commit()
        except IntegrityError:
            return redirect(url_for(".register", e="ue"))

        return redirect(url_for(".login", login="need"))


@bp.route("/update", methods=['GET', 'POST'])
def update():
    if session.get("user_idx", None) is None:
        return redirect(url_for(".login", login="need"))

    if request.method == "GET":
        return render_template(
            "member/update.html"
        )
    elif request.method == "POST":
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if len(password2) < 8:
            return redirect(url_for(".update", e="pws"))

        hashed_password = sha512(password.encode()).hexdigest()
        hashed_password2 = sha512(password2.encode()).hexdigest()

        member = Member.query.filter_by(
            idx=session['user_idx'],
            password=hashed_password
        ).first()

        member.password = hashed_password2
        db.session.commit()

        del session['user_idx']
        return redirect(url_for(".login", login="need"))
