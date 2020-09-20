from flask import Flask, request, render_template, redirect, url_for, abort
from flask import make_response
from flask_socketio import SocketIO, join_room, leave_room
from flask_socketio import emit, send


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

users = {
    'user1': '1234',
    'user2': '2234',
    'user3': '3234',
    'user4': '4234',
}


@app.route('/login', methods=['GET', 'POST'])
def login():
    if (request.method == 'GET'):
        return render_template('login.html')
    elif (request.method == 'POST'):
        form = request.form
        username = form['username']
        password = form['password']

        try:
            if (username in users):
                if (users[username] == password):
                    resp = make_response(redirect('home'))
                    resp.set_cookie('username', username)
                    return resp
                else:
                    raise Exception('Password was wrong!')
            else:
                raise Exception('Username was wrong!')

        except Exception as e:
            return render_template('login.html', error=str(e))

    else:
        abort(401)


@app.route('/home')
def home():
    username = request.cookies.get('username')

    if username is None:
        return redirect(url_for('login'))
    return render_template('index.html')


@socketio.on('message')
def message(data):
    if (data['room'] is not None):
        emit('message', data['message'], room=data['room'])
    else:
        emit('message', data['message'], broadcast=True)


@socketio.on('online')
def connect(data):
    username = data['username']
    print('username', username)
    emit('new_online', username, broadcast=True)


@socketio.on('offline')
def disconnect(data):
    username = data['username']
    emit('disconnect', username + 'was left!', broadcast=True)


@socketio.on('join_room')
def join_room_event(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('message', f'{username}: Hi :)', room=room)


@socketio.on('leave_room')
def leave_room_event(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('message', f'{username}: Bye :(', room=room)


if __name__ == "__main__":
    socketio.run(app)
