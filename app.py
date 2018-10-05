'''
cloud computing assignment 
under prof. sudeepta mishra
'''
#Import required modules
from gevent import monkey; monkey.patch_all()
from flask import Flask, render_template, request, json
from gevent import queue
from gevent.pywsgi import WSGIServer

#Create an instance of the Flask class
app = Flask(__name__)
app.debug = True

#Defination of room class
class Room(object):

    #Constructor
    def __init__(self):
        self.users = set()
        self.messages = []

    def backlog(self, size=25):
        return self.messages[-size:]
    
    #add subscriber
    def subscribe(self, user):
        self.users.add(user)

    def add(self, message):
        for user in self.users:
            print user
            user.queue.put_nowait(message)
        self.messages.append(message)

#Defination of USER class
class User(object):

    def __init__(self):
        self.queue = queue.Queue()

rooms = {'room-1': Room(),'room-2': Room(),}

#Dictionary of simulataneous users
users = {}

#Bind function 'choose_name' to the URL
@app.route('/')
def choose_name():
    return render_template('choose.html')

#Bind function 'main()' to the URL
@app.route('/<uid>')
def main(uid):
    return render_template('main.html',uid=uid,rooms=rooms.keys())

#Bind funtion 'join' to the resource based URI /room/uid
@app.route('/<room>/<uid>')
def join(room, uid):
    user = users.get(uid, None)
    if not user:
        users[uid] = user = User()
    active_room = rooms[room]
    active_room.subscribe(user)
    print 'subscribe', active_room, user
    messages = active_room.backlog()
    return render_template('room.html',room=room, uid=uid, messages=messages)

#Bind funtion 'put' to the resource based URI put/room/uid and enable POST
@app.route("/put/<room>/<uid>", methods=["POST"])
def put(room, uid):
    user = users[uid]
    room = rooms[room]
    message = request.form['message']
    room.add(':'.join([uid, message]))
    return ''

#Bind funtion 'poll' to the resource based URI poll/uid and enable POST
@app.route("/poll/<uid>", methods=["POST"])
def poll(uid):
    try:
        msg = users[uid].queue.get(timeout=10)
    except queue.Empty:
        msg = []
    return json.dumps(msg)

#Server start point
if __name__ == "__main__":
    http = WSGIServer(('', 3000), app)
    http.serve_forever()
