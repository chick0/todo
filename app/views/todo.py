# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request, session
from flask import redirect, url_for
from flask import render_template
from sqlalchemy.orm.exc import UnmappedInstanceError

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


@bp.route("/dashboard")
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

    todo = Todo.query.filter_by(
        owner=member.idx
    ).order_by(
        Todo.idx.desc()
    ).paginate(page)

    return render_template(
        "todo/dashboard.html",
        todo=todo
    )


@bp.route("/append", methods=['POST'])
def append():
    member = get_member()
    if member is None:
        return "", 401

    if len(request.form.get("todo", "")) != 0:
        todo = Todo()
        todo.owner = member.idx
        todo.text = request.form.get("todo")

        db.session.add(todo)
        db.session.commit()

    return "", 200


@bp.route("/pop")
def pop():
    member = get_member()
    if member is None:
        return "", 401

    try:
        idx = int(request.args.get("idx", "-1"))
        if idx == -1:
            return "", 400
    except ValueError:
        return "", 400

    todo = Todo.query.filter_by(
        idx=idx
    ).first()

    try:
        db.session.delete(todo)
        db.session.commit()
    except UnmappedInstanceError:
        pass

    return "", 200
