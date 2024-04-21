from database.models import User, Project
from database.database import db, init_database


def create_user(first_name, last_name, email, username, password):
    new_user = User(email=email,first_name=first_name,last_name=last_name,username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return

def check_password(username, password):
    if User.query.filter_by(username=username).first()!=None:
        if username == User.query.filter_by(username=username).first().username:
            return password == User.query.filter_by(username=username).first().password
    return False

def register_check_data(email, username):
    error=[]
    if User.query.filter_by(email=email).first()!=None:
        error.append("Email already registered")
    if User.query.filter_by(username=username).first()!=None:
        error.append("Username already registered")
    return error
def create_project():
    new_project = Project()
    return

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()