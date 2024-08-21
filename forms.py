from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email, Length
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    name= StringField("Full Name", validators=[DataRequired(message='Full Name is required')])
    email = StringField("Email", validators=[DataRequired(message='Email is required'), Email(message='Invalid email address')])
    password = PasswordField("Password", validators=[DataRequired(message='Password is required'), Length(min=8)])
    submit = SubmitField("Sign Me Up")


# TODO: Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(message='Email is required'), Email(message='Invalid email address')])
    password = PasswordField("Password", validators=[DataRequired(message='Password is required'), Length(min=8)])
    submit = SubmitField("Let Me In")


# TODO: Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    comment = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit comment")
