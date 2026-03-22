from fastapi import FastAPI
import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    format="({time:HH:mm:ss}) [{name} / {function} {level}] {message}",
    level="INFO",
    enqueue=True
)

app = FastAPI()

@app.get("/")
async def health_check():
    logger.info("Health check OK")
