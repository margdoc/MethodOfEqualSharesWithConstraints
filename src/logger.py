import logging
import os
from io import StringIO
    

report_stream = StringIO()
memory_handler = logging.StreamHandler(stream=report_stream)
memory_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

stderr_handler = logging.StreamHandler()
stderr_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

logger = logging.getLogger("Method of Equal Shares")
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())
logger.addHandler(memory_handler)
logger.addHandler(stderr_handler)

def get_logs() -> str:
    return report_stream.getvalue()