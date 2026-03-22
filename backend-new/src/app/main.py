from fastapi import FastAPI
import logging

logging.basicConfig(
    level=logging.INFO,
    format='(%(name)s / %(funcName)s) [%(levelname)s] %(message)s'
)

logger = logging.getLogger(__name__)
app = FastAPI()

@app.get("/")
async def health_check():
    logger.info("Health check OK")
