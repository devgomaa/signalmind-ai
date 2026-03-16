import json
from engine.utils.logger import get_logger

logger = get_logger("DataWriter")


def save_json(path, data):

    with open(path, "w", encoding="utf-8") as f:

        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved data → {path}")