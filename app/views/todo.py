# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request, session
from flask import redirect, url_for
from flask import render_template

from models import Member


bp = Blueprint(
    name=__name__.split(".")[-1],
    import_name=__name__,
    url_prefix=f"/{__name__.split('.')[-1]}"
)


@bp.route("")
def dashboard():
    member = Member.query.filter_by(
        idx=session.get("user_idx", -1)
    ).first()
    if member is None:
        return redirect(url_for("member.login", login="need"))

    if len(member.secret) != 0 and not session.get("2fa_status", False):
        return redirect(url_for("2fa.verify"))

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
