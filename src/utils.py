import logging
import os

log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.log"))
views_logger = logging.getLogger("views")

file_handler = logging.FileHandler(f"{log_path}", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)

views_logger.addHandler(file_handler)
views_logger.setLevel(logging.DEBUG)

services_logger = logging.getLogger("services")
services_logger.addHandler(file_handler)
services_logger.setLevel(logging.DEBUG)
