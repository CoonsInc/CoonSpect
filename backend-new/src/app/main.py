from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def health_check():
    print("[HEALTH] Health check OK")
