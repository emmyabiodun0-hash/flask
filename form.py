from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import StringField,  EmailField, PasswordField, DateField, SubmitField, TextAreaField
from wtforms.validators import InputRequired
from models import User




class Logins(FlaskForm):
    email = EmailField(
        'Email',
        validators=[InputRequired(),],
    
    )
    password = PasswordField(
        'Password',
        validators=[InputRequired(),],
    )

    full_name = StringField(
        'full_name',
        validators=[InputRequired(),],
    )
   
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email is register")
        

    def validate_full_name(self, field):
        # print(field.data)
        # print(f"Query: {User.query.filter_by(username=field.data).all()}")
        if user := User.query.filter_by(username=field.data).first():
            # print(f"User found: {user}")
            raise ValidationError("Username is register")
        


class PostForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    body = TextAreaField("Body")
