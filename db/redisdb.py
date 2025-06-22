import logging

from redis import Redis
from configuration import conf

logging.info('\nConnecting to Redis...')
redis_db = Redis(
    host=conf.redis_host,
    port=conf.redis_port,
    password=conf.redis_pass,
)