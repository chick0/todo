# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request, session
from flask import redirect, url_for
from flask import render_template

from app import db
from models import Member, Todo


bp = Blueprint(
    name=__name__.split(".")[-1],
    import_name=__name__,
    url_prefix=f"/{__name__.split('.')[-1]}"
)


def get_member():
    return Member.query.filter_by(
        idx=session.get("user_idx", -1)
    ).first()


@bp.route("")
def dashboard():
    member = get_member()
    if member is None:
        return redirect(url_for("member.login", login="need"))

    try:
        page = int(request.args.get("page", "1"))

        if page < 1:
            page = 1
    except ValueError:
        page = 1

    return render_template(
        "todo/dashboard.html",
        page=page
    )


@bp.route("/clear")
def clear():
    member = get_member()
    if member is None:
        return redirect(url_for("member.login", login="need"))

    for todo in Todo.query.filter_by(owner=member.idx).all():
        db.session.delete(todo)

    db.session.commit()

    return redirect(url_for("todo.dashboard"))
