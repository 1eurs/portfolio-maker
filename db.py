# from flask_sqlalchemy import SQLAlchemy
#
#
# class User(db.Model):
#     __tablename__ = "user"
#     name = db.Column(db.Integer, primary_key=True)
#     role = db.Column(db.String(250), nullable=False)
#     about = db.Column(db.String(250), unique=True, nullable=False)
#     resume = db.Column(db.String(250), unique=True, nullable=False)
#     github = db.Column(db.String(250), nullable=False)
#     linkedin = db.Column(db.String(250), nullable=False)
#     email = db.Column(db.String(250), unique=True, nullable=False)
#
# class project(db.Model):
#     __tablename__ = "project"
#     project_name = db.Column(db.String(250), nullable=False)
#     description = db.Column(db.String(250), nullable=False)
#     tools = db.Column(db.String(250), unique=True, nullable=False)
#     github = db.Column(db.String(250), unique=True, nullable=False)
#     link = db.Column(db.String(250), nullable=False)
#
# class skills(db.Model):
#     __tablename__ = "skills"
#     skill = db.Column(db.String(250), nullable=False)
#
