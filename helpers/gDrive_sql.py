import pickle
import threading
from sqlalchemy import Column, Integer, LargeBinary, String
from sqlalchemy.exc import SQLAlchemyError
from helpers import BASE, SESSION

class gDriveCreds(BASE):
    """
    SQLAlchemy model for storing Google Drive credentials.
    """
    __tablename__ = "gDrive"
    chat_id = Column(Integer, primary_key=True)
    credential_string = Column(LargeBinary)

    def __init__(self, chat_id: int, credential_string: bytes = None):
        self.chat_id = chat_id
        if credential_string is not None:
            self.credential_string = credential_string

gDriveCreds.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()

def set_credential(chat_id: int, credential) -> None:
    """
    Stores or updates the Google Drive credential for the given chat_id.
    """
    with INSERTION_LOCK:
        try:
            cred_bin = pickle.dumps(credential)
            saved_cred = SESSION.get(gDriveCreds, chat_id)
            if not saved_cred:
                saved_cred = gDriveCreds(chat_id, cred_bin)
            else:
                saved_cred.credential_string = cred_bin

            SESSION.merge(saved_cred)
            SESSION.commit()
        except SQLAlchemyError as e:
            SESSION.rollback()
            raise
        # Optionally, log exception

def get_credential(chat_id: int):
    """
    Retrieves the Google Drive credential for the given chat_id, or None.
    """
    with INSERTION_LOCK:
        try:
            saved_cred = SESSION.get(gDriveCreds, chat_id)
            if saved_cred and saved_cred.credential_string is not None:
                return pickle.loads(saved_cred.credential_string)
            return None
        except Exception:
            return None

def clear_credential(chat_id: int) -> None:
    """
    Deletes the stored credential for the given chat_id.
    """
    with INSERTION_LOCK:
        try:
            saved_cred = SESSION.get(gDriveCreds, chat_id)
            if saved_cred:
                SESSION.delete(saved_cred)
                SESSION.commit()
        except SQLAlchemyError:
            SESSION.rollback()
            # Optionally, log exception
