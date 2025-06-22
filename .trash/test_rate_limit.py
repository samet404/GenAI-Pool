import time
from sys import stdout

from google import genai

from configuration import conf

if __name__ == '__main__':
    client = genai.Client(api_key=conf.pool_config.api_keys[2])

    first = next(iter(conf.pool_config.models_to_use))

    while True:
        try:
            for chunk in client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents="Tell me a joke about cats"
            ):
                stdout.write(chunk.text)
            time.sleep(1)
            print("\n --- \n")
        except Exception as e:
            print(f"Error: {e}")