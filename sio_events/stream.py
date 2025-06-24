import json
from flask_socketio import SocketIO
from google import genai
from pydantic import BaseModel
from Logger import logger
from Pool import Pool

class Input(BaseModel):
    prompt: str
    sio_event: str
    metadata: str | None = None

def handle_req_stream_event(input, io: SocketIO, pool: Pool, session_id: str):
    try:
        input = json.loads(str(input))
        input = Input(**input)

        try_count = 0
        while True:
            try:
                pool.update_index()
                index = pool.current_index
                client: genai.Client = pool.clients[index]
                api_key = client._api_client.api_key
                model = pool.choose_model_to_use(api_key)

                for chunk in pool.getResponseStream(contents=input.prompt, client=client, api_key=api_key, model=model):
                    if hasattr(chunk, "text"):
                        emit_data = json.dumps({
                            "chunk": chunk.text,
                            "metadata": input.metadata,
                        })
                        io.emit(input.sio_event, emit_data, namespace='/', to=session_id)
                        io.sleep(0)

                io.emit(f"{input.sio_event}:success", json.dumps({
                    "metadata": input.metadata,
                    "model": model,
                }), namespace='/', to=session_id)
                break
            except Exception as e:
                io.sleep(2)
                try_count += 1
                error = f'Error in req-stream event in while loop | MODEL: {model} | API KEY: {pool.api_keys.index(api_key)} |  {str(e)}'
                logger.error(error)
                if try_count > 30:
                    raise Exception(error)

    except Exception as e:
        error_data = json.dumps({
            "error": str(e),
            "client_error": "Ops, something went wrong. Please try again later.",
            "metadata": input.metadata,
        })
        io.emit(f"{input.sio_event}:error", error_data, namespace='/', to=session_id)
        logger.error(f'Error in req-stream event - {error_data}')
