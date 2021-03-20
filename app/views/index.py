# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import session
from flask import render_template
from flask import redirect, url_for


bp = Blueprint(
    name=__name__.split(".")[-1],
    import_name=__name__,
    url_prefix="/"
)


@bp.route("/")
def index():
    if session.get("user_idx", None) is not None:
        return redirect(url_for("todo.dashboard"))

    return render_template(
        "index/index.html"
    )
