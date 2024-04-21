from database.models import Comment
from database.database import db


def add_comment_to_database(content, time, project_id, task_id, user_id):
    new_comment = Comment(content=content,date=time,project_id=project_id, task_id=task_id, user_id=user_id)
    db.session.add(new_comment)
    db.session.commit()
    return new_comment


