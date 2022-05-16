from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from formes import UserForm, ProjectsForm, SkillsForm, RegisterForm, Loginform
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    resume = db.relationship('UserResume', backref='user')
    projects = db.relationship('Project', backref='user')
    skills = db.relationship('Skill', backref='user')


class UserResume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(250), nullable=True)
    about = db.Column(db.String(250), unique=False, nullable=True)
    resume = db.Column(db.String(250), unique=False, nullable=True)
    github = db.Column(db.String(250), nullable=True)
    linkedin = db.Column(db.String(250), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(250), nullable=True)
    description = db.Column(db.String(250), nullable=True)
    tools = db.Column(db.String(250), unique=False, nullable=True)
    github = db.Column(db.String(250), unique=False, nullable=True)
    link = db.Column(db.String(250), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill = db.Column(db.String(250), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


db.create_all()


# user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('index.html', current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hash_and_salted_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("make_cv", id=new_user.id))
        except IntegrityError:
            flash("ur email already exist pls use it to login")
            return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = Loginform()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("wrong email")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, form.password.data):
            flash("wrong pass")
            return redirect(url_for('login'))
        else:
            login_user(user)
            flash('You were successfully logged in')
            return redirect(url_for('portfolio', name=user.name))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/make-portfolio', methods=["GET", "POST"])
def make_cv():
    form = UserForm()
    user_id = request.args.get('id')
    if form.validate_on_submit():
        resume = UserResume(
            role=form.role.data,
            about=form.about.data,
            resume=form.resume.data,
            github=form.github.data,
            linkedin=form.linkedin.data,
            user_id=user_id
        )
        db.session.add(resume)
        db.session.commit()
        return redirect(url_for('add_project', id=resume.user_id))
    return render_template('make-cv.html', form=form)


@app.route('/add-projects', methods=["GET", "POST"])
def add_project():
    form = ProjectsForm()
    user_id = request.args.get('id')
    if form.validate_on_submit():
        new_project = Project(
            project_name=form.project_name.data,
            description=form.description.data,
            tools=form.tools.data,
            github=form.github.data,
            link=form.link.data,
            user_id=user_id
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('add_skills', id=new_project.user_id))
    return render_template('add-projects.html', form=form)


@app.route('/add-skills', methods=["GET", "POST"])
def add_skills():
    form = SkillsForm()
    user_id = request.args.get('id')
    if form.validate_on_submit():
        new_skill = Skill(
            skill=form.skill.data,
            user_id=user_id
        )
        db.session.add(new_skill)
        db.session.commit()
        return redirect(url_for('portfolio', name=User.query.filter_by(id=new_skill.user_id).first().name))
    return render_template('add-skills.html', form=form)


@app.route('/pr/<name>')
def portfolio(name):
    user = User.query.filter_by(name=name).first()
    resume = UserResume.query.filter_by(user_id=user.id).first()
    projects = Project.query.filter_by(user_id=user.id).all()
    skills = Skill.query.filter_by(user_id=user.id).all()
    return render_template('portfolio.html', user=user, projects=projects, skills=skills, resume=resume)


@app.route('/edit/', methods=['GET', 'POST'])
def edit():
    user_id = request.args.get('id')
    resume = UserResume.query.filter_by(user_id=user_id).first()
    user = User.query.get(user_id)
    edit_resume = UserForm(
        role=resume.role,
        about=resume.about,
        linkedin=resume.linkedin,
        github=resume.github,
        resume=resume.resume,
    )
    if edit_resume.validate_on_submit():
        resume.role = edit_resume.role.data
        resume.about = edit_resume.about.data
        resume.linkedin = edit_resume.linkedin.data
        resume.github = edit_resume.github.data
        resume.resume = edit_resume.resume.data
        db.session.commit()
        return redirect(url_for('portfolio', name=user.name))
    return render_template('make-cv.html', form=edit_resume)


@app.route('/add-new-project', methods=["GET", "POST"])
def add_new_project():
    form = ProjectsForm()
    user_id = request.args.get('id')
    if form.validate_on_submit():
        new_project = Project(
            project_name=form.project_name.data,
            description=form.description.data,
            tools=form.tools.data,
            github=form.github.data,
            link=form.link.data,
            user_id=user_id
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('portfolio', name=User.query.filter_by(id=user_id).first().name))
    return render_template('add-projects.html', form=form)


@app.route('/add-new-skills', methods=["GET", "POST"])
def add_new_skills():
    form = SkillsForm()
    user_id = request.args.get('id')
    user = User.query.filter_by(id=user_id).first()
    if form.validate_on_submit():
        new_skill = Skill(
            skill=form.skill.data,
            user_id=user_id
        )
        db.session.add(new_skill)
        db.session.commit()
        return redirect(url_for('portfolio', name=user.name))
    return render_template('add-skills.html', form=form)


# @app.route('/add-projects/', methods=["GET", "POST"])
# def add_add_project():
#     form = ProjectsForm()
#     name = request.args.get('name')
#     if form.validate_on_submit():
#         new_project = Project(
#             project_name=form.project_name.data,
#             description=form.description.data,
#             tools=form.tools.data,
#             github=form.github.data,
#             link=form.link.data,
#             user_id=name
#         )
#         db.session.add(new_project)
#         db.session.commit()
#         return redirect(url_for('portfolio', name=new_project.user_id))
#     return render_template('add-projects.html', form=form)
#
#
# @app.route('/add-skills', methods=["GET", "POST"])
# def add_add_skills():
#     form = SkillsForm()
#     name = request.args.get('name')
#     if form.validate_on_submit():
#         new_skill = Skill(
#             skill=form.skill.data,
#             user_id=name
#         )
#         db.session.add(new_skill)
#         db.session.commit()
#         return redirect(url_for('portfolio', name=new_skill.user_id))
#     return render_template('add-skills.html', form=form)

@app.route('/edit-project/', methods=["GET", "POST"])
def edit_project():
    project_id = request.args.get('id')
    project = Project.query.get(project_id)
    user_id = project.user_id
    user = User.query.get(user_id)
    edited_project = ProjectsForm(
        project_name=project.project_name,
        description=project.description,
        tools=project.tools,
        github=project.github,
        link=project.link,
    )
    if edited_project.validate_on_submit():
        project.project_name = edited_project.project_name.data
        project.description = edited_project.description.data
        project.tools = edited_project.tools.data
        project.github = edited_project.github.data
        project.link = edited_project.link.data
        db.session.commit()
        return redirect(url_for('portfolio',name=user.name))
    return render_template('edit-project.html', form=edited_project)


@app.route('/delete-project')
def delete_project():
    project_id = request.args.get('id')
    project_to_delete = Project.query.get(project_id)
    user_id = project_to_delete.user_id
    user = User.query.get(user_id)
    db.session.delete(project_to_delete)
    db.session.commit()
    return redirect(url_for('portfolio', name=user.name))

if __name__ == "__main__":
    app.run(debug=True)
