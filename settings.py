from dotenv import load_dotenv
import json
from pathlib import Path
import logging
load_dotenv()
# noinspection PyArgumentList
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", mode='w'),
        logging.StreamHandler()
    ],
    datefmt='%Y-%m-%d %H:%M:%S')

with open('config.json') as config_file:
    config = json.load(config_file)

Path(f"{config['output_dir']}/lab").mkdir(parents=True, exist_ok=True)

