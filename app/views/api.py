# -*- coding: utf-8 -*-
from json import dumps

from flask import Blueprint
from flask import request, session
from flask import Response

from app import db
from models import Member, Todo


bp = Blueprint(
    name=__name__.split(".")[-1],
    import_name=__name__,
    url_prefix=f"/{__name__.split('.')[-1]}"
)


@bp.route("/todo", methods=['GET', 'POST', 'PATCH'])
def todo():
    member = Member.query.filter_by(
        idx=session.get("user_idx", -1)
    ).first()
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

    if request.method == "GET":
        try:
            page = int(request.args.get("page", "1"))

            if page <= 0:
                page = 1
        except ValueError:
            page = 1

        td = Todo.query.filter_by(
            owner=member.idx
        ).order_by(
            Todo.idx.desc()
        ).paginate(page)

        return Response(
            status=200,
            mimetype="application/json",
            response=dumps({
                "page": page,
                "prev": td.prev_num,
                "next": td.next_num,
                "todo": [
                    dict(
                        idx=item.idx,
                        text=item.text,
                        date=item.register.isoformat()
                    ) for item in td.items]
            })
        )
    elif request.method == "POST":
        text = request.form.get("todo", "").strip()[:1000]
        if len(text) != 0:
            td = Todo()
            td.owner = member.idx
            td.text = text

            db.session.add(td)
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
    elif request.method == "PATCH":
        try:
            idx = int(request.form.get("idx", "-1"))
        except ValueError:
            idx = -1

        target = Todo.query.filter_by(
            idx=idx,
            owner=member.idx
        ).first()
        if target is None:
            return Response(
                status=404,
                mimetype="application/json",
                response=dumps({
                    "error": "삭제할 투두를 찾지 못했습니다"
                })
            )

        text = request.form.get("todo", "").strip()
        if len(text) != 0:
            target.text = text
            db.session.commit()

            return Response(
                status=200,
                mimetype="application/json",
                response=dumps({
                    "alert": "수정 완료"
                })
            )
        else:
            db.session.delete(target)
            db.session.commit()

            return Response(
                status=200,
                mimetype="application/json",
                response=dumps({
                    "alert": "삭제 완료"
                })
            )
