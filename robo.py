import os
from time import sleep
from threading import Thread
from flask import Flask
from flask import render_template
from flask import Response
import cv2
import json
import NetworkManager


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


left = MotorThread(202)
left.start()
right = MotorThread(196)
right.start()

app = Flask(__name__ )

@app.route('/camera')
def index():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,320);
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,240);
    def camera():
        while True:
            rval, frame = cap.read()
            ret, jpeg = cv2.imencode('.jpg', frame, (cv2.IMWRITE_JPEG_QUALITY, 20))
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tostring() + b'\r\n\r\n' 
    return Response(camera(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route("/api/wireless")

def wireless():
    networks = []
	#Getting the information about the network
    for dev in NetworkManager.NetworkManager.GetDevices():
        if dev.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
            continue
    for ap in dev.SpecificDevice().GetAccessPoints():
        networks.append({"ssid":ap.Ssid, "freq":ap.Frequency, "strength":ord(ap.Strength)})
    return json.dumps(networks)

@app.route("/batterystatus")
def battery():
    stats = {}
	#open the file battery to get the information about the battery
    for filename in os.listdir("/sys/power/axp_pmu/battery/"):
        with open ("/sys/power/axp_pmu/battery/" + filename) as fh:
            stats[filename] = int(fh.read())
            #r means read the values 
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
    right.speed = -1
    return "left"

@app.route("/stop")
def stop():
    left.speed = 0
    right.speed = 0
    return "stop"

@app.route("/go")
def go():
    left.speed = 1
    right.speed = 1
    return "go"

@app.route("/right")
def right1():
    left.speed = -1
    right.speed = 1
    return "right"

@app.route("/back")
def back():
    left.speed = -1
    right.speed = -1
    return "back"
    
#if any error happened use (debug = True)

if __name__ == '__main__':
    app.run(host = "0.0.0.0", threaded = True)
