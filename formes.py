from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class Loginform(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in!")


class UserForm(FlaskForm):
    role = StringField("role", validators=[DataRequired()])
    about = CKEditorField("about", validators=[DataRequired()])
    linkedin = StringField("linkedin", validators=[URL()])
    github = StringField("github", validators=[URL()])
    resume = StringField("resume", validators=[URL()])
    submit = SubmitField("Submit")


class ProjectsForm(FlaskForm):
    project_name = StringField("project_name", validators=[DataRequired()])
    tools = StringField("tools", validators=[DataRequired()])
    description = CKEditorField("description", validators=[DataRequired()])
    github = StringField("github", validators=[ URL()])
    link = StringField("link", validators=[ URL()])
    submit = SubmitField("submit")


class SkillsForm(FlaskForm):
    skill = StringField("skill", validators=[DataRequired()])
    submit = SubmitField("submit")
