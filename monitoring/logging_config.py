import logging
import os

def setup_logging():
    os.makedirs("output", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.FileHandler("output/monitor.log", mode="a"),
            logging.StreamHandler()
        ]
    )