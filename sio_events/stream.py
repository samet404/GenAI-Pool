import json
import logging
import eventlet
from flask_socketio import SocketIO
from google import genai
from pydantic import BaseModel
from Logger import logger
from Pool import Pool

class Input(BaseModel):
    prompt: str
    sio_event: str
    metadata: str | None = None

def handle_event(input, io: SocketIO, pool: Pool, session_id: str):
    try:
        for i in range(10):
            logging.info(f"req-stream requested from {session_id} |  {input} ")
        input = json.loads(str(input))
        input = Input(**input)

        pool.update_index()
        index = pool.current_index
        client: genai.Client = pool.clients[index]
        api_key = client._api_client.api_key
        model = pool.choose_model_to_use(api_key)
        logging.info("2")

        def generate_response():
            for chunk in pool.getResponseStream(contents=input.prompt, client=client, api_key=api_key,
                                                model=model):
                if hasattr(chunk, "text"):
                    emit_data = json.dumps({
                        "chunk": chunk.text,
                        "metadata": input.metadata,
                        "model": model,
                    })
                    for i in range(10):
                        logging.info(f"stream sending to {session_id} | {input} ")

                    io.emit(input.sio_event, emit_data, namespace='/', to=session_id)
                    io.sleep(0)

        try_count = 0
        while True:
            try:
                generate_response()
                break
            except Exception as e:
                io.sleep(2)
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
    for i in range(10):
        logging.info(f"Stream route registered for session {session_id}")
    @io.on('req-stream', namespace='/')
    def stream(input):
        eventlet.spawn(handle_event, input, io, pool, session_id)