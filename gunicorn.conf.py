# Gunicorn configuration file
import multiprocessing

max_requests = 1000
max_requests_jitter = 50

log_file = "-"

bind = "0.0.0.0:3100"

timeout = 90

graceful_timeout = 30

preload_app = True

proxy_protocol = True

forwarded_allow_ips = "*"

worker_class = "uvicorn.workers.UvicornWorker"
# workers = int(round((multiprocessing.cpu_count() * 2) + 1))
workers = 4
