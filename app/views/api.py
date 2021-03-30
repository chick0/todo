# -*- coding: utf-8 -*-
from json import dumps

from flask import Blueprint
from flask import request, session
from flask import url_for
from flask import Response

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
def get():
    member = get_member()
    if member is None:
        return Response(
            status=401,
            mimetype="application/json",
            response=dumps({
                "error": "인증 실패, 로그인이 필요합니다!"
            })
        )

    if len(member.secret) != 0 and not session.get("2fa_status", False):
        return Response(
            status=401,
            mimetype="application/json",
            response=dumps({
                "error": "요청 거부, 2단계 인증을 통과한 상태가 아닙니다"
            })
        )

    try:
        page = int(request.args.get("page", "1"))

        if page <= 0:
            page = 1
    except ValueError:
        page = 1

    todo = Todo.query.filter_by(
        owner=member.idx
    ).order_by(
        Todo.idx.desc()
    ).paginate(page)

    return Response(
        status=200,
        mimetype="application/json",
        response=dumps({
            "page": page,
            "prev": url_for("todo.dashboard", page=todo.prev_num),
            "next": url_for("todo.dashboard", page=todo.next_num),
            "todo": [
                dict(
                    idx=item.idx,
                    text=item.text,
                    date=item.register.isoformat()
                ) for item in todo.items]
        })
    )


@bp.route("/append", methods=['POST'])
def append():
    member = get_member()
    if member is None:
        return Response(
            status=401,
            mimetype="application/json",
            response=dumps({
                "error": "인증 실패, 로그인이 필요합니다!"
            })
        )

    if len(member.secret) != 0 and not session.get("2fa_status", False):
        return Response(
            status=401,
            mimetype="application/json",
            response=dumps({
                "error": "요청 거부, 2단계 인증을 통과한 상태가 아닙니다"
            })
        )

    text = request.form.get("todo", "").strip()
    if len(text) != 0:
        todo = Todo()
        todo.owner = member.idx
        todo.text = text

        db.session.add(todo)
        db.session.commit()

        return Response(
            status=201,
            mimetype="application/json",
            response=dumps({
                "alert": "추가 완료"
            })
        )
    else:
        return Response(
            status=200,
            mimetype="application/json",
            response=dumps({
                "alert": "할 일을 입력해야 합니다"
            })
        )


@bp.route("/pop")
def pop():
    member = get_member()
    if member is None:
        return Response(
            status=401,
            mimetype="application/json",
            response=dumps({
                "error": "인증 실패, 로그인이 필요합니다!"
            })
        )

    if len(member.secret) != 0 and not session.get("2fa_status", False):
        return Response(
            status=401,
            mimetype="application/json",
            response=dumps({
                "error": "요청 거부, 2단계 인증을 통과한 상태가 아닙니다"
            })
        )

    try:
        idx = int(request.args.get("idx", "-1"))

        if idx <= 0:
            raise ValueError
    except ValueError:
        return Response(
            status=400,
            mimetype="application/json",
            response=dumps({
                "error": "잘못된 요청 입니다"
            })
        )

    todo = Todo.query.filter_by(
        idx=idx,
        owner=member.idx
    ).first()

    if todo is None:
        return Response(
            status=404,
            mimetype="application/json",
            response=dumps({
                "error": "삭제할 투두를 찾지 못했습니다"
            })
        )

    db.session.delete(todo)
    db.session.commit()

    return Response(
        status=200,
        mimetype="application/json",
        response=dumps({
            "alert": "삭제 완료"
        })
    )
