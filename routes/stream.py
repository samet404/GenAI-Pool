import json
from typing import Literal

from flask_socketio import SocketIO
from pydantic import BaseModel

from Logger import logger

class Input(BaseModel):
    prompt: str
    model: Literal['gemma-3-1b-it', 'gemma-3-27b-it', 'gemma-3-4b-it', 'gemma-3-12b-it', 'gemma-3n-e4b-it' ,'gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-2.5-pro-preview-06-05', 'gemini-1.5-pro']

def stream_route(
        io: SocketIO,
        gemini_pool,
        session_id: str
):
    @io.on('/req-stream', namespace='/')
    def stream(input):
        try:
            input = json.loads(str(input))
            input = Input(**input)

            for chunk in gemini_pool.getResponseStream(model=input.model, contents=input.prompt):
                if chunk.text:
                    io.emit('stream', chunk.text, namespace='/')
                    io.sleep(0.1)

            io.emit('stream-success', namespace='/', to=session_id)
        except Exception as e:
            io.emit('stream-error', namespace='/', to=session_id)
            logger.error(f'Route Error: /stream - {str(e)}')
