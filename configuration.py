import json
from typing import Dict, Any

# Replace 'file_path.json' with your actual JSON file path
with open('conf.json', 'r') as file:
    jsonfile = json.load(file)  # Use json.load() for files, not json.loads()

if (not 'api_keys' in jsonfile):
    raise ValueError("Missing 'api_keys' key in JSON file")

conf: Dict[str, Any] = {
    "api_keys": jsonfile['api_keys'],
    "port": jsonfile['port'] if 'port' in jsonfile else 4000,
    "health_check": jsonfile['health_check'] if 'health_check' in jsonfile else True,
    "cors_origins": jsonfile['cors_origins'],
    "lazy_load": jsonfile['lazy_load'] if 'lazy_load' in jsonfile else False,
    "allow_clients": jsonfile['allow_clients'] if 'allow_clients' in jsonfile else True
}