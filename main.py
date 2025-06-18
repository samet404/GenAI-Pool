from flask import Flask, render_template, request
from Logger import logger
from configuration import conf
from Pool import Pool
from routes.stream import stream_route
from flask_socketio import SocketIO, join_room
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    socketio = SocketIO(
        app,
        cors_allowed_origins=conf["cors_origins"],
        async_mode='eventlet',
        logger=True,
        engineio_logger=True
    )
    CORS(app, resources={r"/*": {"origins": conf["cors_origins"]}})

    gemini_pool = Pool(
        api_keys=conf["api_keys"],
        health_check=conf["health_check"]
    )

    @app.route('/client')
    def client():
        if (conf['allow_clients']):
            return render_template('index.html')
        else:
            return 404

    @socketio.on('connect', namespace='/')
    def handle_connect():
        # Get the client's session ID
        session_id = request.sid
        if session_id is None:
            raise Exception('No session ID found')
        join_room(session_id)
        stream_route(socketio, gemini_pool, session_id)

    return app, socketio


app, socketio = create_app()

if __name__ == '__main__':
    logger.info('Starting Flask server at http://localhost:' + str(conf["port"]))
    socketio.run(app=app,
                 host='0.0.0.0',  # Add this if you need external access
                 port=conf["port"],
                 debug=True)
