from typing import Generator
from Database import DatabaseSession


def get_database() -> Generator[DatabaseSession, None, None]:
    db = DatabaseSession()
    try:
        db.connect()
        yield db
    finally:
        db.close()