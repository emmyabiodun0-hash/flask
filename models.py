from datetime import datetime, timezone
from db import db
from flask_login import UserMixin
from sqlalchemy import ForeignKey, Integer, String, Boolean, Text, DateTime,func
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), unique=True)
    is_verified = db.Column(db.Boolean, nullable=True, default=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship("Post", back_populates='author')
    tokens = db.relationship('OTPToken', back_populates='user')
    reset = db.relationship('ResetPasswordToken', back_populates='user')

    def __repr__(self):
        return f"<User {self.email}>"
    


class Post(db.Model):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    body: Mapped[str] = mapped_column(Text)
    created_at :Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    authod_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    author:Mapped[User] = relationship('User', back_populates='posts')





class OTPToken(db.Model):
    __tablename__ = "tokens"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(5))
    is_expired = db.Column(db.Boolean, default=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())
    expires_at = db.Column(db.DateTime())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates='tokens')




class ResetPasswordToken(db.Model):
    __tablename__ = "reset"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(5))
    is_expired = db.Column(db.Boolean, default=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now())
    expires_at = db.Column(db.DateTime())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates='reset')


    