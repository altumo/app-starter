import multiprocessing

# Bind to all interfaces
bind = "0.0.0.0:8000"

# Workers: 2-4 x CPU cores
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 2

# Timeout
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Security
limit_request_line = 8190
limit_request_fields = 100

# Restart workers after this many requests (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Use /dev/shm for worker heartbeat (Docker doesn't mount /tmp on tmpfs)
worker_tmp_dir = "/dev/shm"
