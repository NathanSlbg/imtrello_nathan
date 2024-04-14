import hashlib
from functools import wraps
from datetime import datetime
import flask
from flask import Flask, render_template, request, redirect, session, url_for, jsonify

from comment import add_comment_to_database
from manage_users import *
from database.database import db, init_database
from projects import add_project, update_project, get_all_projects, get_project_by_id, update_project_in_database, \
    delete_project_in_database, add_task_to_project, get_tasks_in_project, get_task_by_id, update_task_in_project, \
    delete_task_from_project

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../database/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = 'imtrello'

db.init_app(app)
with app.test_request_context():
    init_database()


@app.route('/')
def display_home_page():  # put application's code here
    return flask.render_template("welcome_page.html.jinja2")


@app.route('/login')
def display_login_page():
    return flask.render_template("login_page.html.jinja2")


@app.route('/register')
def display_register_page():
    return flask.render_template("register_page.html.jinja2")


def is_connected(f):
    @wraps(f)
    def fonction_decorateur(*args, **kwargs):
        if 'username' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for("display_login_page"))

    return fonction_decorateur


@app.route('/myprojects')
@is_connected
def display_projects():
    projects = get_all_projects(session.get('username'))
    return flask.render_template("my_projects.html.jinja2", projects=projects)


@app.route('/projet/<int:project_id>/<int:task_id>')
@is_connected
def display_task(project_id, task_id):
    task = get_task_by_id(task_id)

    project = get_project_by_id(project_id)
    user = User.query.filter_by(username=session.get('username')).first()
    return flask.render_template("task.html.jinja2", task=task, project=project, user=user)


@app.route('/register', methods=['GET', 'POST'])
def register_function():
    donnees = request.form
    email = donnees.get("email")
    first_name = donnees.get("first_name")
    last_name = donnees.get("last_name")
    username = donnees.get("username")
    password = donnees.get("password")
    password_confirm = donnees.get("password_confirm")
    register_check, errors_data, errors_password = register_checker(email, username, password, password_confirm)
    if register_check:
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password1 = hash.hexdigest()
        create_user(first_name, last_name, email, username, password1)
        return display_login_page()
    else:
        return display_home_page()


def register_checker(email, username, password, password_confirm):
    '''
    vérifier que les mots de passe correspondent
    vérifier qu'ils respectent certains critères
    vérifier que l'username ou l'email n'existe pas déjà
    '''
    register_check = True
    errors_data = register_check_data(email, username)
    print(errors_data)
    password_error = []
    if password != password_confirm:
        password_error.append("Passwords don't match")
        register_check = False
    print(register_check)
    if len(password) < 8:
        password_error.append("Password too short, use at least 8 caracteres")
        register_check = False
    print(register_check)
    if len(errors_data) != 0:
        register_check = False
    print(register_check)
    return register_check, errors_data, password_error


@app.route('/login', methods=['GET', 'POST'])
# @app.route('/myprojects', methods=['GET', 'POST'])
def login_function():
    donnees = request.form
    username = donnees.get("username")
    password = donnees.get("password")
    login_check, error = login_checker(username, password)
    if login_check:
        session['username'] = username
        return display_projects()
    else:
        return display_login_page()


def login_checker(username, password):
    login_check = False
    hash = password + app.secret_key
    hash = hashlib.sha1(hash.encode())
    password = hash.hexdigest()
    print("app.py", username, password)
    if check_password(username, password):
        error = None
        login_check = True
        return login_check, error
    error = "User doesn't exist or wrong password"
    return login_check, error


@app.route('/home_page', methods=['GET', 'POST'])
def logout_function():
    session.pop('username', None)
    return display_home_page()


@app.route('/addproject')
@is_connected
def display_add_project():
    return flask.render_template("add_project.html.jinja2")


@app.route('/projet/<int:project_id>/addtask')
@is_connected
def display_add_task(project_id):
    project = get_project_by_id(project_id)
    if project:
        return flask.render_template("add_task.html.jinja2", project=project)
    else:
        return "Project not found", 404


@app.route('/projet/<int:project_id>')
@is_connected
def display_project(project_id):
    project = get_project_by_id(project_id)
    tasks = get_tasks_in_project(project_id)
    if project:
        return render_template("project.html.jinja2", project=project, tasks=tasks)
    else:
        return "Project not found", 404


@app.route('/projet/<int:project_id>/project_details')
@is_connected
def display_project_details(project_id):
    project = get_project_by_id(project_id)
    user = User.query.filter_by(username=session.get('username')).first()
    if project:
        return render_template("project_details.html.jinja2", project=project, user=user)
    else:
        return "Project not found", 404


@app.route('/addproject', methods=['GET', 'POST'])
@is_connected
def fonction_formulaire_create_project():
    if request.method == 'POST':
        form_est_valide, errors = formulaire_est_valide(flask.request.form)
        if not form_est_valide:
            print("Le formulaire n'est pas valide. Erreurs :", errors)
            return display_add_project()
        else:
            manager_name = session.get('username')
            project_name = request.form.get("project_name")
            description = request.form.get("description")
            deadline_date = request.form.get("deadline_date")
            deadline_time = request.form.get("deadline_time")
            deadline_str = deadline_date + ' ' + deadline_time
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
            add_project(project_name, description, deadline, manager_name)
            return redirect(url_for('display_projects'))
    else:

        return display_add_project()


def formulaire_est_valide(form):
    project_name = request.form.get("project_name")
    description = request.form.get("description")
    deadline_time = request.form.get("deadline_time")
    deadline_date = request.form.get("deadline_time")

    result = True
    errors = []

    if not project_name:
        errors += ["Error: Project name is required"]
        result = False

    if not deadline_date:
        errors += ["Error: Project date deadline is required"]
        result = False

    if not deadline_time:
        errors += ["Error: Project time deadline is required"]
        result = False

    return result, errors


@app.route('/projet/<int:project_id>/addtask', methods=['GET', 'POST'])
@is_connected
def fonction_formulaire_create_task(project_id):
    if request.method == 'POST':
        form_est_valide, errors = formulaire_task_est_valide(flask.request.form)
        if not form_est_valide:
            print("Le formulaire n'est pas valide. Erreurs :", errors)
            return display_add_task(project_id)
        else:
            task_name = request.form.get("task_name")
            deadline_date = request.form.get("deadline_date")
            deadline_time = request.form.get("deadline_time")
            deadline_str = deadline_date + ' ' + deadline_time
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
            add_task_to_project(project_id, task_name, deadline)
            return redirect(url_for('display_project', project_id=project_id))
    else:

        return display_add_task(project_id)


def formulaire_task_est_valide(form):
    task_name = request.form.get("task_name")
    deadline_time = request.form.get("deadline_time")
    deadline_date = request.form.get("deadline_time")

    result = True
    errors = []

    if not task_name:
        errors += ["Error: Task name is required"]
        result = False

    if not deadline_date:
        errors += ["Error: Project date deadline is required"]
        result = False

    if not deadline_time:
        errors += ["Error: Project time deadline is required"]
        result = False

    return result, errors


@app.route('/delete_project/<int:project_id>', methods=['POST'])
@is_connected
def delete_project(project_id):
    delete_project_in_database(project_id)
    return redirect(url_for('display_projects'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
@is_connected
def delete_task(task_id):
    delete_task_from_project(task_id)
    return redirect(url_for('display_projects'))


@app.route('/edit_project_form/<int:project_id>', methods=['GET', 'POST'])
@is_connected
def edit_project_form(project_id):
    project = get_project_by_id(project_id)
    if project:
        if request.method == 'POST':
            project_name = request.form.get('project_name')
            description = request.form.get('description')
            deadline_date = request.form.get('deadline_date')
            deadline_time = request.form.get('deadline_time')
            new_developers = request.form.get('new_developers')
            if new_developers != "":
                users = new_developers.split(',')
            else:
                users = None
            is_done = True if request.form.get('is_done') == 'on' else False

            # Valider et convertir la date et l'heure de la deadline en un objet datetime
            if deadline_date and deadline_time:
                deadline_str = deadline_date + ' ' + deadline_time
                try:
                    deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
                except ValueError:
                    return "Format de date invalide", 400
            else:
                return "Les champs de date et d'heure sont requis", 400

            # Mettre à jour le projet dans la base de données
            update_project_in_database(project_id, developers=users,
                                       project_name=project_name,
                                       description=description,
                                       deadline=deadline,
                                       is_done=is_done)
            # Rediriger l'utilisateur vers une page de confirmation ou toute autre page appropriée
            return redirect(url_for('display_projects'))
        else:
            return render_template('edit_project_form.html.jinja2', project=project)
    else:
        return jsonify({'error': 'Project not found'}), 404


@app.route('/edit_task_form/<int:task_id>', methods=['GET', 'POST'])
@is_connected
def edit_task_form(project_id, task_id):
    project = get_project_by_id(project_id)
    task = get_task_by_id(task_id)
    if task:
        if request.method == 'POST':
            task_name = request.form.get('task_name')
            deadline_date = request.form.get('deadline_date')
            deadline_time = request.form.get('deadline_time')

            # Valider et convertir la date et l'heure de la deadline en un objet datetime
            if deadline_date and deadline_time:
                deadline_str = deadline_date + ' ' + deadline_time
                try:
                    deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
                except ValueError:
                    return "Format de date invalide", 400
            else:
                return "Les champs de date et d'heure sont requis", 400

            # Mettre à jour le projet dans la base de données
            update_task_in_project(task_id, task_name=task_name,
                                   deadline=deadline)
            # Rediriger l'utilisateur vers une page de confirmation ou toute autre page appropriée
            return redirect(url_for('display_task', project_id=project.id, task_id=task.id))
        else:
            return render_template('edit_task_form.html.jinja2', project=project, task=task)
    else:
        return jsonify({'error': 'Task not found'}), 404


@app.route('/profile', methods=['GET', 'POST'])
@is_connected
def profile():
    user = User.query.filter_by(username=session.get('username')).first()
    return render_template("profile_page.html.jinja2", user=user)


@app.route('/projet/<int:project_id>/<int:task_id>', methods=['POST'])
@is_connected
def add_comment(project_id, task_id):
    content = request.form['content']
    time = datetime.now()

    user = User.query.filter_by(username=session.get('username')).first()
    user_id = user.id

    add_comment_to_database(content,time,project_id,task_id, user_id)

    return redirect(url_for('display_task', project_id=project_id, task_id=task_id))


if __name__ == '__main__':
    app.run()
