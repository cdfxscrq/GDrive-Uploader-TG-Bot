from sqlalchemy import Column, String, Numeric
from helpers import SESSION, BASE
from sqlalchemy.exc import NoResultFound

class ParentID(BASE):
    __tablename__ = "ParentID"
    chat_id = Column(Numeric, primary_key=True)
    parent_id = Column(String)

    def __init__(self, chat_id, parent_id):
        self.chat_id = chat_id
        self.parent_id = parent_id

# Table creation; in production, you might want to use migrations instead
ParentID.__table__.create(checkfirst=True)

def get_id(chat_id):
    """
    Fetch the ParentID record for the given chat_id.
    Returns the ParentID instance or None if not found.
    """
    try:
        return SESSION.query(ParentID).filter(ParentID.chat_id == chat_id).one()
    except NoResultFound:
        return None
    except Exception:
        return None
    finally:
        SESSION.close()

def set_id(chat_id, parent_id):
    """
    Set or update the parent_id for a given chat_id.
    """
    try:
        instance = SESSION.get(ParentID, chat_id)
        if instance:
            instance.parent_id = parent_id
        else:
            instance = ParentID(chat_id, parent_id)
            SESSION.add(instance)
        SESSION.commit()
    except Exception:
        SESSION.rollback()
        raise
    finally:
        SESSION.close()

def del_id(chat_id):
    """
    Delete the ParentID record for the given chat_id.
    """
    try:
        instance = SESSION.get(ParentID, chat_id)
        if instance:
            SESSION.delete(instance)
            SESSION.commit()
    except Exception:
        SESSION.rollback()
        raise
    finally:
        SESSION.close()
