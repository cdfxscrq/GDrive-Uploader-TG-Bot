from sqlalchemy import Column, String, Numeric
from helpers import SESSION, BASE


class ParentID(BASE):
    __tablename__ = "ParentID"
    chat_id = Column(Numeric, primary_key=True)
    parent_id = Column(String)

    def __init__(self, chat_id, parent_id):
        self.chat_id = chat_id
        self.parent_id = parent_id


ParentID.__table__.create(checkfirst=True)


def get_id(chat_id):
    try:
        return SESSION.query(ID).filter(ParentID.chat_id == chat_id).one()
    except:
        return None
    finally:
        SESSION.close()


def set_id(chat_id, parent_id):
    adder = SESSION.query(ParentID).get(chat_id)
    if adder:
        adder.parent_id = parent_id
    else:
        adder = ParentID(
            chat_id,
            parent_id
        )
    SESSION.add(adder)
    SESSION.commit()


def del_id(chat_id):
    rem = SESSION.query(ParentID).get(chat_id)
    if rem:
        SESSION.delete(rem)
        SESSION.commit()
