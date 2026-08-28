from fastapi import FastAPI, Depends

from Dependencies import get_database
from Database import DatabaseSession


app = FastAPI()


@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: DatabaseSession = Depends(get_database)
):
    return db.get_user(user_id)