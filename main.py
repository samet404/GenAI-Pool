from typing import Literal, Set
from flask import Flask, render_template, request
from pydantic import BaseModel
from Logger import logger
from configuration import conf
from Pool import Pool
from sio_events.on_connect import sio_on_connect
from sio_events.stream import stream_route
from flask_socketio import SocketIO, join_room
from flask_cors import CORS

def create_app():
    logger.info('Creating app...')
    app = Flask(__name__)
    socketio = SocketIO(
        app,
        cors_allowed_origins=conf.cors_origins,
        async_mode='eventlet',
        logger=True,
        engineio_logger=True
    )
    pool = Pool(conf.pool_config)
    CORS(app, resources={r"/*": {"origins": conf.cors_origins}})

    @app.route('/client')
    def client():
        if conf.allow_clients:
            return render_template('index.html')
        else:
            return 404

    sio_on_connect(socketio, pool)
    logger.info('App created successfully.')

    return app, socketio

app, socketio = create_app()

if __name__ == '__main__':
    logger.info('Starting Flask server at http://localhost:' + str(conf.port))
    socketio.run(
        app=app,
        host='0.0.0.0',  # Add this if you need external access
        port=conf.port,
        debug=True  # Set to False in production
    )
