from flask import Flask, request, render_template, session, Response
from flask_cors import CORS, cross_origin
import queue, threading, secrets, time, logging
from uuid import uuid4
from quer import stream_query_agent
from config import LOGS_DIR
import os
from waitress import serve

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(LOGS_DIR, 'app.log'),
    filemode='w'
)
CORS(app, resources={r"/stream": {"origins": "*"}}, supports_credentials=False)

@app.before_request
def assign_session():
    if 'session_id' not in session:
        session['session_id'] = str(uuid4())
    logging.info(f"[SESSION] ID: {session['session_id']}")

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/stream', methods=['GET', 'OPTIONS'])
@cross_origin(origins="*", methods=["GET", "OPTIONS"], send_wildcard=True)
def stream():
    if request.method == 'OPTIONS':
        return Response(status=200)

    message = request.args.get('message', '').strip()
    if not message:
        return Response("Message required", status=400)

    session_id = session.get('session_id')
    logging.info(f"[STREAM] Session {session_id}, Received: {message}")

    token_queue = queue.Queue()
    threading.Thread(
        target=stream_query_agent,
        args=(message, token_queue, session_id),
        daemon=True
    ).start()

    def generate():
        try:
            while True:
                token = token_queue.get()
                if token is None:
                    break
                yield f"data: {token.replace('\\n','\\\\n')}\n\n"
                time.sleep(0.005)
        except GeneratorExit:
            token_queue.put(None)

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)