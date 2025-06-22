import json
import logging
from datetime import time
import time as real_time

from flask_socketio import SocketIO
from google import genai
from pydantic import BaseModel
from Logger import logger
from Pool import Pool
from data_representation import ModelInfo


class Input(BaseModel):
    prompt: str
    sio_event: str
    metadata: str | None = None

def stream(input, io: SocketIO, pool: Pool, session_id: str):
    try:
        logging.info(f"req-stream requested: {input} from {session_id}")
        input = json.loads(str(input))
        input = Input(**input)
        logging.info("1")

        pool.update_index()
        index = pool.current_index
        client: genai.Client = pool.clients[index]
        api_key = client._api_client.api_key
        model = pool.choose_model_to_use(api_key)
        logging.info("2")

        async def generate_response():
            logging.info("3")

            for chunk in pool.getResponseStream(contents=input.prompt, client=client, api_key=api_key,
                                                model=model):
                if hasattr(chunk, "text"):
                    logging.info("4")

                    emit_data = json.dumps({
                        "chunk": chunk.text,
                        "metadata": input.metadata,
                        "model": model,
                    })

                    io.emit(input.sio_event, emit_data, namespace='/', to=session_id)
                    io.sleep(1)

        logging.info("5")

        try_count = 0
        while True:
            try:
                logging.info("5")
                generate_response()
                break
            except Exception as e:
                try_count += 1
                logger.error(f'Error in req-stream route in while loop - {str(e)}')
                if try_count > 30:
                    raise Exception("Too many tries")

        io.emit(f"{input.sio_event}:success", json.dumps({
            "metadata": input.metadata,
        }), namespace='/', to=session_id)
    except Exception as e:
        io.emit(f"{input.sio_event}:error", json.dumps({
            "error": str(e),
            "metadata": input.metadata,
        }), namespace='/', to=session_id)
        logger.error(f'Error in req-stream route - {str(e)}')


def stream_route(
        io: SocketIO,
        pool: Pool,
        session_id: str
):
    @io.on('req-stream', namespace='/')
    def stream(input):
        io.start_background_task(stream, input, io, pool, session_id)
