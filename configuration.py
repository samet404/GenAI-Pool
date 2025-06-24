import os
from pydantic import BaseModel
from constants import GoogleModel

class PoolConfig(BaseModel):
    # Google's models to use.
    # First one is will be first used and the rest will be used in case of failure.
    models_to_use: list[GoogleModel]
    # Whether to check the API keys is working or not
    health_check: int
    # API keys to use for the Gemini Pool
    api_keys: list[str]
    # Whether to lazy load the clients or not. If set to True, the clients will be loaded only when needed.
    lazy_load: bool

class Configuration(BaseModel):
    cors_origins: str
    allow_clients: bool
    pool_config: PoolConfig
    redis_host: str
    redis_port: int
    redis_pass: str
    port: int
    # 0 = NOTSET, 10 = DEBUG, 20 = INFO, 30 = WARNING, 40 = ERROR, 50 = CRITICAL
    log_level: int

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'conf.json')

with open(config_path, 'r') as file:
    jsonfile = file.read()  # Use json.load() for files, not json.loads()

if jsonfile is None:
    raise ValueError("Missing 'conf.json' file. You can create new one by copying 'conf.example.json' to 'conf.json'")

conf: Configuration = Configuration.model_validate_json(jsonfile)