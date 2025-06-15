import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger()
# Silence noisy logs from faker
logging.getLogger("faker.factory").setLevel(logging.ERROR)

ENV = os.environ.get("ENVIRONMENT", "local")
env_file: str = os.environ.get("ENV_FILE", f"./env/{ENV}.env")
logger.info(f"Loading environment variables from : {env_file}")
load_dotenv(env_file)
