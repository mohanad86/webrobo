import os
from time import sleep
from threading import Thread
from flask import Flask, render_template
class MotorThread(Thread):
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
@app.route("/app.js")
def java():
    return 
@app.route("/")
def robot():
    return app.send_static_file('robot.html')

@app.route("/left")
def command():
    left.speed = 1
    right.speed = -1
    return "ok"
@app.route("/stop")
def stop():
    left.speed = 0
    right.speed = 0
    return "ok"
    
@app.route("/go")
def go():
    left.speed = 1
    right.speed = 1
    return "ok"
    
@app.route("/right")
def right():
    left.speed = -1
    right.speed = 1
    return "ok"
        
 
if __name__ == '__main__':
    app.run(host = "0.0.0.0")


