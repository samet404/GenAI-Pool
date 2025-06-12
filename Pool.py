import logging
from datetime import time
from typing import Dict
import time
from google import genai


class Pool:
    def __init__(self,
         # List of API keys to use for the Gemini Pool
         api_keys: list[str],
         # Whether to check the API keys is working or not
         health_check=False,
         # Whether to lazy load the clients or not
         lazy_load=False
    ):
        self.health_check = health_check
        self.lazy_load = lazy_load
        self.api_keys = api_keys.copy()
        # Current index that represents the current ai client
        self.current_index = -1
        # List of clients that are used to generate responses
        self.clients = []
        # Timeouts are applied to clients that give an error to prevent overloading the API
        self.timeouts: Dict[int, float] = {}

        if lazy_load == False:
            for api_key in api_keys:
                self.add_client(api_key)

    def add_client(self, api_key: str):
        try:
            client = genai.Client(api_key=api_key)

            if self.health_check:
                result = client.models.generate_content(model="gemma-3-1b-it",
                                                        contents="""Answer with "OK" without quotes and spaces.""").text
                if result is not None and result == "OK":
                    self.clients.append(genai.Client(api_key=api_key))
            else:
                self.clients.append(genai.Client(api_key=api_key))
        except:
            logging.error(f"Invalid API key: {api_key}")

    def update_index(self):
        if self.lazy_load == True and self.clients[self.current_index] is None and self.api_keys[
            self.current_index] is not None:
            self.add_client(self.api_keys[self.current_index])
        elif len(self.clients) == self.current_index + 1:
            self.current_index = 0
        else:
            self.current_index += 1

    def getResponseStream(self, model: str, contents: str):
        self.update_index()

        try:
            client_timeout = self.timeouts.get(self.current_index)

            # Check if the client has tried to generate a response recently and has timed out
            if client_timeout is not None:
                if (time.time() - client_timeout) < 10000:
                    return self.getResponseStream(model, contents)
                else:
                    self.timeouts.pop(self.current_index)

            return self.clients[self.current_index].models.generate_content_stream(
                model=model,
                contents=contents
            )
        except:
            self.timeouts[self.current_index] = time.time()
            logging.error(f"Error in getResponseStream: {model}, {contents}")

    def getResponse(self, model: str, contents: str):
        try:
            client = self.clients[self.current_index]

            response = client.models.generate_content(
                model=model,
                contents=contents
            )
            self.current_index += 1
            return response
        except:
            self.current_index += 1
            logging.error(f"Error in getResponse: {model}, {contents}")
