import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8000"
timeout = 120
keepalive = 5
preload_app = True

loglevel = "info"
accesslog = "/opt/app/logs/gunicorn_access.log"
errorlog = "/opt/app/logs/gunicorn_error.log"

capture_output = True
enable_stdio_inheritance = False
