import ConfigParser
import cv2
from flask import Flask
from flask import render_template
from flask import Response
from flask import request
import json
import NetworkManager
import os
import optparse
from time import sleep
from threading import Thread
config = ConfigParser.ConfigParser()
config.readfp(open('/etc/sumochip/sumochip.conf'))

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

class SensorThread(Thread):
    
    def __init__(self):
        """
        Setup all the sensor pins and open filehandlers
        """
        Thread.__init__(self)
        self.daemon = True
        self.sensor_pins = {#'line_left':193,
                            #'line_right':194,
                            'enemy_left':200,
                            'enemy_right':203}
        self.sensor_fhs = {}
        self.sensor_values = {}
        for pin_name, pin in self.sensor_pins.items(): 
            try:
                with open("/sys/class/gpio/export", "w") as fh:
                    fh.write(str(pin))
            except IOError:
                pass
            with open("/sys/class/gpio/gpio%d/direction" % pin, "w") as fh:
                fh.write("in")
                
            self.sensor_fhs[pin_name] = open("/sys/class/gpio/gpio%d/value" % pin, "r")
            
    def run(self):
        """ Update sensor values """
        while True:
            for name, fh in self.sensor_fhs.items():
                fh.seek(0)
                self.sensor_values[name] = bool(int(fh.read()))
            sleep(0.1)
                
    def __getattr__(self, name):
        """ Make this sensors class easier to use, for example
        >>> sensors = SensorThread()
        >>> sensors.start()  # start reading the sensors
        >>> print(sensors.enemy_left)  # get a sensor value
        True
        """
        try:
            return self.sensor_values[name]
        except KeyError as err:
            raise AttributeError('No sensor named '+name)

class LightStrip():
    def __init__(self):                                
        for pin  in range(192,200): 
            try:
                with open("/sys/class/gpio/export", "w") as fh:
                    fh.write(str(pin))
            except IOError:
                 pass
            with open("/sys/class/gpio/gpio%d/direction" % pin, "w") as fh:
                fh.write("out")
    def on(self, pin):
        with open("/sys/class/gpio/gpio%d/value" % pin, "w") as fh:
            fh.write("0")

    def off(self, pin):
        with open("/sys/class/gpio/gpio%d/value" % pin, "w") as fh:
            fh.write("1") 
            
class AI(Thread):

    def __init__(self, left_motor, right_motor, sensors, lights):
        Thread.__init__(self)
        self.daemon = True
        self.left = left_motor
        self.right = right_motor
        self.sensors = sensors
        self.lights = lights

    def run(self):
        while True:
            if self.sensors.enemy_left:
                self.blues_on()
                self.left.speed = 1
            else:
                self.blues_off()
                self.left.speed = 0    
            
            if self.sensors.enemy_right:
                self.reds_on()
                self.right.speed = 1
            else:
                self.reds_off()
                self.right.speed = 0
                sleep(0.1) 
                
    def reds_on(self):
        self.lights.on(198)
        self.lights.on(195)
        self.lights.on(194)
        self.lights.on(196)
    def reds_off(self):
        self.lights.off(198)
        self.lights.off(195)
        self.lights.off(194)
        self.lights.off(196)

    def blues_on(self):
        self.lights.on(197)
        self.lights.on(199)
        self.lights.on(193)
        self.lights.on(192)
    def blues_off(self):
        self.lights.off(197)
        self.lights.off(199)
        self.lights.off(193)
        self.lights.off(192)                                              
          
strip = LightStrip()

sensors = SensorThread()

sensors.start()
            
left = MotorThread(config.getint('pins', 'motor left'))
left.start()

right = MotorThread(config.getint('pins', 'motor right'))
right.start()

ai = AI(left, right, sensors, strip)
#left = MotorThread(202)
#left.start()
#right = MotorThread(196)
#right.start()

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

@app.route("/api/wireless", methods=['GET', 'POST'])
def wireless():
    if request.method == 'POST':
        networks = request.form['networks'];
        password = request.form['password'];
        print (request.form)
        return json.dumps({'status':'OK','networks':networks,'pass':password});
    else:
        networks = set()
        for dev in NetworkManager.NetworkManager.GetDevices():
            if dev.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
                 continue
            for ap in dev.SpecificDevice().GetAccessPoints():
                networks.add(ap.Ssid)
        return json.dumps({"networks":tuple(networks), "current":None})

@app.route("/batterystatus")
def battery():
    stats = {}
    axp = AXP209()
    stats['capacity'] = axp.battery_gauge 
    stats['voltage'] = axp.battery_voltage
    #open the file battery to get the information about the battery
    #for filename in os.listdir("/sys/power/axp_pmu/battery/"):
        #with open ("/sys/power/axp_pmu/battery/" + filename) as fh:
            #stats[filename] = int(fh.read())
            #r means read the values which is coming from the files 
    with open("/sys/class/gpio/gpio200/value", "r") as fh:
        stats["enemy_left"] = int(fh.read())
    with open("/sys/class/gpio/gpio193/value", "r") as fh:
        stats["line_left"] = int(fh.read())
    with open("/sys/class/gpio/gpio194/value", "r") as fh:
        stats["line_right"] = int(fh.read())
    with open("/sys/class/gpio/gpio203/value", "r") as fh:
        stats["enemy_right"] = int(fh.read())
    return json.dumps(stats)
    
@app.route("/lightall")
def lightall():
    strip.on(197)
    strip.on(199)
    strip.on(193)
    strip.on(192)
    strip.on(198)
    strip.on(195)
    strip.on(194)
    strip.on(196)
    sleep(10)
    strip.off(197)
    strip.off(199)
    strip.off(193)
    strip.off(192)
    strip.off(198)
    strip.off(195)
    strip.off(194)
    strip.off(196)
    return "light"

@app.route("/light1")
def light1():
    strip.on(197)
    sleep(1)
    strip.off(197)
    return "light"
    
@app.route("/light2")
def light2():
    strip.on(199)
    sleep(1)
    strip.off(199)
    return "light"

@app.route("/light3")
def light3():
    strip.on(193)
    sleep(1)
    strip.off(193)
    return "light"

@app.route("/light4")
def light4():
    strip.on(192)
    sleep(1)
    strip.off(192)
    return "light"
    
@app.route("/light5")
def light5():
    strip.on(198)
    sleep(1)
    strip.off(198)
    return "light"
    
@app.route("/light6")
def light6():
    strip.on(195)
    sleep(1)
    strip.off(195)
    return "light"
    
@app.route("/light7")
def light7():
    strip.on(194)
    sleep(1)
    strip.off(194)
    return "light"
    
@app.route("/light8")
def light8():
    strip.on(196)
    sleep(1)
    strip.off(196)
    return "light"  

@app.route("/reds")
def lightred():
    strip.on(198)
    strip.on(195)
    strip.on(194)
    strip.on(196)
    sleep(5)
    strip.off(198)
    strip.off(195)
    strip.off(194)
    strip.off(196)
    return "light"

@app.route("/blues")
def lightblue():
    strip.on(197)
    strip.on(199)
    strip.on(193)
    strip.on(192)
    sleep(5)
    strip.off(197)
    strip.off(199)
    strip.off(193)
    strip.off(192)
    return "light"

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

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-H", "--host",
        help="Bind to address, default to all interfaces",
        default="0.0.0.0")
    parser.add_option("-P", "--port",
        type=int,
        help="Listen on this port, default to 5000",
        default=5000)
    parser.add_option("-d", "--debug",
        action="store_true", dest="debug",
        help=optparse.SUPPRESS_HELP)
    parser.add_option("-a", "--A", action = "store_true" , dest ="ai", help="Enable AI")    
    options, _ = parser.parse_args()

    if options.ai:
        ai.start()

    app.run(
        debug=options.debug,
        host=options.host,
        port=options.port,
    )
