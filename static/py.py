from flask import Flask, render_template
from flask_sockets import Sockets
 
import os
from time import sleep
from threading import Thread
class MotorThread(Thread): # This class generated PWM signal necessary for servo motors
    def __init__(self, pin=192):
        Thread.__init__(self)
        self.path = "/sys/class/gpio/gpio%d" % pin
        if not os.path.exists(self.path):
            with open("/sys/class/gpio/export", "w") as fh:
                fh.write(str(pin))
        with open(os.path.join(self.path, "direction"), "w") as fh:
            fh.write("out")
        self.speed = 0
        self.daemon = True
           
    def run(self):
        with open(os.path.join(self.path, "value"), "w") as fh:
          while True:
            if self.speed:                
                fh.write("1")
                fh.flush()
                sleep(0.002 if self.speed > 0 else 0.001)
                fh.write("0")
                fh.flush()
                sleep(0.018 if self.speed > 0 else 0.019)
            else:
                sleep(0.020)
 
left = MotorThread(192)
left.start()
 
right = MotorThread(195)
right.start()
 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
sockets = Sockets(app)
 
@app.route('/')
def index():
    print "bla"
    return render_template('index.html');
 
@sockets.route('/')
def command(ws):
    while not ws.closed:
        command = ws.receive();
        if command == '0':
            print("Seisma")
            left.speed = 0
            right.speed = 0
        elif command == '1':
            left.speed = 1
            right.speed = 1
            print("Edasi")
        elif command == '2':
            print("Tagasi")
            left.speed = -1
            right.speed = -1
        elif command == '3':
            print("Paremale")
            left.speed = -1
            right.speed = 1
        elif command == '4':
            print("Vasakule")
            left.speed = 1
            right.speed = -1
        else:
            print(command)
            exec command
 
if __name__ == '__main__':
    print("Started server")
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
