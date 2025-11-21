from fastapi import FastAPI

app = FastAPI(title="Collabook API")

@app.get("/")
async def root():
    return {"message": "Welcome to Collabook API"}
