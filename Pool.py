import json
import logging
import traceback
from datetime import datetime
from typing import List, Dict

from engineio.async_drivers import eventlet
from google import genai
from configuration import PoolConfig
from constants import GENAI_QUOTAS, GoogleModel
from db.redisdb import redis_db

class Pool:
    def __init__(self, pool_config: PoolConfig):
        self.models_to_use: List[GoogleModel] = pool_config.models_to_use.copy()
        logging.info(f"Models to use: {self.models_to_use}")
        self.health_check = pool_config.health_check
        self.lazy_load = pool_config.lazy_load
        self.api_keys = pool_config.api_keys.copy()
        # Current index that represents the current ai client
        self.current_index = -1
        # List of clients that are used to generate responses
        self.clients: List[genai.Client] = []

        self.last_used_models: Dict[str, str] = {}
        self.last_used_model_cache_count: Dict[str, int] = {}

        if not pool_config.lazy_load:
            for api_key in pool_config.api_keys:
                self.add_client(api_key)

    def add_client(self, api_key: str):
        try:
            client = genai.Client(api_key=api_key)

            if self.health_check:
                try:
                    model = self.choose_model_to_use(api_key)
                    if model is None:
                        raise Exception(f"API key is rate-limited")

                    result = client.models.generate_content(model=model,
                                                            contents="""Answer with "OK" without quotes, spaces and special characters.""").text
                    if result is not None and result == "OK":
                        self.clients.append(client)
                except Exception as e:
                    logging.error(f"Health check failed for API key {api_key} | {str(e)}")
            else:
                self.clients.append(client)
        except Exception as e:
            error_info = {
                'error': str(e),
                'traceback': traceback.format_exc(),
                'api_key': api_key,
                'current_index': self.current_index,
                'clients_length': len(self.clients)
            }
            logging.error(f"Couldn't add client to pool: {json.dumps(error_info)}")

    # This function updates the current index of the current client
    def update_index(self):
        self.current_index += 1

        if self.lazy_load == True  and len(self.api_keys) > self.current_index :
            self.add_client(self.api_keys[self.current_index])
        elif len(self.clients) == self.current_index:
            self.current_index = 0


    # This function chooses the model to use based on the usage of the models
    # First it checks RPD, RPM and then TPM
    # Function always tries to choose the first available models that preferred by the user
    # If none of the models are not available, it returns none to indicate that api key is rate-limited and cannot be used at the moment
    def choose_model_to_use(self, api_key: str):
        # We are using a cache to avoid checking the same model multiple times
        if api_key in self.last_used_model_cache_count:
            if self.last_used_model_cache_count[api_key] <= 10:
                self.last_used_model_cache_count[api_key] += 1
                return self.last_used_models[api_key]

        model_to_use = None

        for model in self.models_to_use:
            # Skip if model not in quotas
            if model not in GENAI_QUOTAS:
                logging.error(f"Model {model} not found in GENAI_QUOTAS")
                continue

            current_date = datetime.now()

            # ==============================================================================
            # CHECK IF MODEL IS RATE LIMITED
            # ==============================================================================

            req_per_day =  redis_db.get(
                f"aipool:api_key:{api_key}:client_usage:model:{model}:requests_per_day:date:{current_date.year}-{current_date.month}-{current_date.day}")
            if req_per_day is not None:
                req_per_day = int(req_per_day.decode('utf-8'))
                logging.debug(f"RPD for model {model} and API key {self.api_keys.index(api_key)} is {req_per_day}")
                if req_per_day >= GENAI_QUOTAS[model]["RPD"]:
                    logging.debug(f"Client {api_key} has reached RPD limit for model {model}")
                    continue
            else:
                logging.debug(f"RPD not found for model {model} and API key {self.api_keys.index(api_key)}")

            req_per_min =  redis_db.get(
                f"aipool:api_key:{api_key}:client_usage:model:{model}:requests_per_minute:date:{current_date.year}-{current_date.month}-{current_date.day}-{current_date.hour}-{current_date.minute}")
            if req_per_min is not None:
                req_per_min = int(req_per_min.decode('utf-8'))
                logging.debug(f"RPM for model {model} and API key {self.api_keys.index(api_key)} is {req_per_min}")
                if req_per_min >= GENAI_QUOTAS[model]["RPM"]:
                    logging.debug(f"Client {api_key} has reached RPM limit for model {model}")
                    continue
            else:
                logging.debug(f"RPM not found for model {model} and API key {self.api_keys.index(api_key)}")

            tokens_per_min =  redis_db.get(
                f"aipool:api_key:{api_key}:client_usage:model:{model}:tokens_per_minute:date:{current_date.year}-{current_date.month}-{current_date.day}-{current_date.hour}-{current_date.minute}")
            if tokens_per_min is not None:
                logging.debug(f"TPM for model {model} and API key {self.api_keys.index(api_key)} is {tokens_per_min}")
                tokens_per_min = int(tokens_per_min.decode('utf-8'))
                if tokens_per_min >= GENAI_QUOTAS[model]["TPM"]:
                    logging.debug(f"Client {api_key} has reached TPM limit for model {model}")
                    continue
            else:
                logging.debug(f"TPM not found for model {model} and API key {self.api_keys.index(api_key)}")

            self.last_used_model_cache_count[api_key] = 1
            self.last_used_models[api_key] = model
            model_to_use = model
            break

        redis_db.set(
            f"aipool:api_key:{api_key}:current_model",
            model_to_use if model_to_use else "RATE_LIMITED"
        )

        if model_to_use is None:
            logging.info(f"Client {api_key} has reached rate limit")

        logging.info(f"Client {api_key} has selected model {model_to_use}")
        return model_to_use

    def getResponseStream(self, client: genai.Client, api_key: str, model: str,contents: str):
        stream = client.models.generate_content_stream(
            model=model,
            contents=contents
        )

        current_date = datetime.now()

        def add_usage_to_redis():
            redis_db.incr(
                f"aipool:api_key:{api_key}:client_usage:model:{model}:requests_per_day:date:{current_date.year}-{current_date.month}-{current_date.day}")
            updated_value = redis_db.get(
                f"aipool:api_key:{api_key}:client_usage:model:{model}:requests_per_day:date:{current_date.year}-{current_date.month}-{current_date.day}")
            logging.debug(f"THIS SHOULDN'T BE NONE OR SMTH: {updated_value}")
            redis_db.incr(
                f"aipool:api_key:{api_key}:client_usage:model:{model}:requests_per_minute:date:{current_date.year}-{current_date.month}-{current_date.day}-{current_date.hour}-{current_date.minute}")


        eventlet.spawn(add_usage_to_redis)

        for chunk in stream:
            def add_usage_to_redis():
                current_date = datetime.now()
                redis_db.incr(
                    f"aipool:api_key:{api_key}:client_usage:model:{model}:tokens_per_minute:date:{current_date.year}-{current_date.month}-{current_date.day}-{current_date.hour}-{current_date.minute}",
                    chunk.usage_metadata.prompt_token_count
                )

            eventlet.spawn(add_usage_to_redis)

            yield chunk
