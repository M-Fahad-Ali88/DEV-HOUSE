from fastapi import FastAPI, Depends
from Database import DatabaseSession
from Dependencies import get_database

app = FastAPI()


@app.get("/users")
def get_users(
    db: DatabaseSession = Depends(get_database)
):
    return db.get_users()