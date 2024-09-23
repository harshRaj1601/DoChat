from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send
import time
import random
import string

app = Flask(__name__)
socketio = SocketIO(app)

# Store users in chatrooms
users = {}

# Function to generate random room key
def generate_room_key(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route('/')
def index():
    return render_template('index.html')

# Route to create a new room with a randomly generated room key
@app.route('/create', methods=['POST'])
def create_room():
    username = request.form['username']
    room = generate_room_key()  # Generate random room key
    return render_template('chat.html', username=username, room=room)

# Route to join an existing room with a provided room key
@app.route('/join', methods=['POST'])
def join_room_route():
    username = request.form['username']
    room = request.form['room']
    return render_template('chat.html', username=username, room=room)

# Handle when a user joins a room
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    if username and room:
        join_room(room)
        users[username] = room
        send({'msg': f"{username} has entered the chatroom."}, to=room)
    else:
        send({'msg': "User or room data is missing."}, to=room)
# Handle when a user leaves a room
@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    if username in users:
        leave_room(room)
        send({'msg': f"{username} has left the chatroom."}, to=room)
        users.pop(username, None)

# Handle incoming chat messages and broadcast them to the room
@socketio.on('message')
def handle_message(data):
    room = data['room']
    username = data['username']
    msg = data['message']
    timestamp = time.strftime('%I:%M %p', time.localtime())
    send({'username': username, 'msg': msg, 'time': timestamp}, to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
