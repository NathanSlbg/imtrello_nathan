from database.models import Notif
from database.database import db

def add_notif_to_database(type, content, date, user_id):
    new_notif = Notif(type=type, content=content, date=date, user_id=user_id)
    db.session.add(new_notif)
    db.session.commit()
    return new_notif
