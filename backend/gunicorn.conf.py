import multiprocessing
from app.core.config import settings

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
bind = f"0.0.0.0:{settings.PORT}"
timeout = 120
keepalive = 5
preload_app = True

loglevel = "info"
accesslog = "-"
errorlog = "-"

capture_output = True
enable_stdio_inheritance = False
