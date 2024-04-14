from database.models import Comment
from database.database import db


def add_comment_to_database(content, datetime, project_id, task_id, user_id):
    new_comment = Comment(content=content,datetime=datetime,project_id=project_id, task_id=task_id, user_id=user_id)
    db.session.add(new_comment)
    db.session.commit()
    return new_comment


