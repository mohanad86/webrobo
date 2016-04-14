import os
from time import sleep
from threading import Thread
from flask import Flask, render_template

for pin  in range(192,196):
    try:
        with open("/sys/class/gpio/export", "w") as fh:
            fh.write(str(pin))
    except IOError:
        pass
    with open("/sys/class/gpio/gpio%d/direction" % pin, "w") as fh:
        fh.write("in")

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

def distance(self):
    self.path = "/sys/class/gpio/gpio%d" % pin
    value = os.path.join(198)
    distance = 6762 / (value -9) -5
    textedit.append("{:06.2f}".format(distance))
    print (distance)
    print("distance", os.path.join(198))
left = MotorThread(202)
left.start()

import json

r2 = MotorThread(196)
r2.start()
app = Flask(__name__ )
 
@app.route("/batterycharge")
def battery():
    stats = {}
    for filename in os.listdir("/sys/power/axp_pmu/battery/"):
        with open ("/sys/power/axp_pmu/battery/" + filename) as fh:
            stats[filename] = int(fh.read())
            
    with open("/sys/class/gpio/gpio192/value", "r") as fh:
        stats["enemy_left"] = int(fh.read())
    with open("/sys/class/gpio/gpio193/value", "r") as fh:
        stats["line_left"] = int(fh.read())
    with open("/sys/class/gpio/gpio194/value", "r") as fh:
        stats["line_right"] = int(fh.read())
    with open("/sys/class/gpio/gpio195/value", "r") as fh:
        stats["enemy_right"] = int(fh.read())


    return json.dumps(stats)
    
@app.route("/css.css")
def css():
    return app.send_static_file('css.css')
@app.route("/app.js")
def java():
    return app.send_static_file('app.js')
@app.route("/")
def robot():
    return app.send_static_file('robot.html')

@app.route("/left")
def command():
    left.speed = 1
    r2.speed = -1
    return "ok"
@app.route("/stop")
def stop():
    left.speed = 0
    r2.speed = 0
    return "ok"
    
@app.route("/go")
def go():
    left.speed = 1
    r2.speed = 1
    return "ok"
    
@app.route("/right")
def right():
    left.speed = -1
    r2.speed = 1
    return "ok"
@app.route("/back")
def back():
    left.speed = -1
    r2.speed = -1        

 
if __name__ == '__main__':
    app.run(host = "0.0.0.0", debug = True, threaded = True)