# -*- coding: utf-8 -*-

from sqlalchemy import func

from app import db


class Member(db.Model):
    idx = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    email = db.Column(
        db.String(96),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(128),
        nullable=False
    )

    register = db.Column(
        db.DateTime,
        nullable=False,
        default=func.now()
    )

    secret = db.Column(
        db.String(32),
        nullable=False,
    )

    def __repr__(self):
        return f"<Member idx={self.idx}>"


class Todo(db.Model):
    idx = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    owner = db.Column(
        db.Integer,
        nullable=False
    )

    register = db.Column(
        db.DateTime,
        nullable=False,
        default=func.now()
    )

    text = db.Column(
        db.Text,
        nullable=False
    )

    def __repr__(self):
        return f"<Todo idx={self.idx}, owner={self.owner}>"
