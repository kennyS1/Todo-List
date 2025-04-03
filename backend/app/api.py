from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "home page"}

@app.post("/user/login")
async def userLogin():
    return {"message": "login page"}
