"""Gunicorn configuration for production deployment."""

bind = "127.0.0.1:8000"
workers = 4
accesslog = "logs/gunicorn-access.log"
errorlog = "logs/gunicorn-error.log"
loglevel = "info"
timeout = 120
