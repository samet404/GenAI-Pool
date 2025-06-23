import logging

from flask import request
from flask_socketio import SocketIO, join_room

from Pool import Pool
from sio_events.stream import stream_route

connected_clients = set()

def sio_on_connect(socketio: SocketIO, pool: Pool):
    @socketio.on('connect', namespace='/')
    def handle_connect():
        try:
            # ==============================================================================
            # INITIALIZE STATES
            # ==============================================================================
            session_id = request.sid

            logging.info(f"Client connected: {session_id}")
            join_room(session_id)

            # ==============================================================================
            # EVENTS
            # ==============================================================================

            @socketio.on('disconnect')
            def handle_disconnect():
                logging.info(f"Client disconnected: {session_id}")

            stream_route(socketio, pool, session_id)

            socketio.emit('connect-success', namespace='/', to=session_id)
        except Exception as e:
            socketio.emit('connect-error', str(e), namespace='/', to=session_id)