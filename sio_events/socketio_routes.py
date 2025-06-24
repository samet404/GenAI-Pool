import logging
import eventlet
from flask import request
from flask_socketio import SocketIO, join_room

from Pool import Pool
from sio_events.stream import handle_req_stream_event

def socketio_routes(socketio: SocketIO, pool: Pool):
    @socketio.on('connect', namespace='/')
    def handle_connect():
        try:
            # TODO: maybe you can do some checks here later...
            logging.info(f"Client connected: {request.sid}")
            join_room(room=request.sid, namespace='/')
        except Exception as e:
            socketio.emit('connect-error', str(e), namespace='/', to=request.sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        logging.info(f"Client disconnected: {request.sid}")

    @socketio.on('req-stream', namespace='/')
    def stream(input):
        eventlet.spawn(handle_req_stream_event, input, socketio, pool, request.sid)
