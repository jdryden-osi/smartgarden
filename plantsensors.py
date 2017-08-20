import time
import sys
import threading
from arduino import Arduino
from repeatedtimer import RepeatedTimer

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")


class PlantSensors(object):
    def __init__(self, moisture_scan=3600, temp_scan=5, light_scan=5, port='/dev/ttyACM0'):
        self.arduino = Arduino(port)
        self.moisture = None
        self.temperature = None
        self.pressure = None
        self.humidity = None
        self.light = None
        
        self.light_scan = light_scan
        self.temp_scan = temp_scan
        self.moisture_scan = moisture_scan
        self.temp_last_scan = None
        self.light_last_scan = None
        self.moisture_last_scan = None
        self.serial_busy = False

        self.update_temperature()
        self.update_light()
        self.update_moisture()

        self.updateTimer = RepeatedTimer(1, self.on_scan)

    def stop(self):
        self.updateTimer.stop()

    def on_scan(self):
        if not self.serial_busy:
            self.serial_busy = True
            now = time.time()
            try:
                if (now - self.temp_last_scan > self.temp_scan):
                    self.update_temperature(now)
                if (now - self.light_last_scan > self.light_scan):
                    self.update_light(now)
                if (now - self.moisture_last_scan > self.moisture_scan):
                    self.update_moisture(now)
            finally:
                self.serial_busy = False

    def update_temperature(self, scanTime=None):
        if scanTime:
            self.temp_last_scan = scanTime
        else:
            self.temp_last_scan = time.time()
        rawVal = self.arduino.get_temperature().split(',')
        if rawVal == ['Unavailable']:
            self.temperature = 'Unavailable'
            self.pressure = 'Unavailable'
            self.humidity = 'Unavailable'
        elif len(rawVal) == 3:
            self.temperature = PlantSensors.try_parse_float(rawVal[0])
            self.pressure = PlantSensors.try_parse_float(rawVal[1])
            self.humidity = PlantSensors.try_parse_float(rawVal[2])
        else:
            self.temperature = 'ReadFailed'
            self.pressure = 'ReadFailed'
            self.humidity = 'ReadFailed'

    def update_light(self, scanTime=None):
        if scanTime:
            self.light_last_scan = scanTime
        else:
            self.light_last_scan = time.time()
        rawVal = self.arduino.get_light()
        if rawVal == 'Unavailable':
            self.light = 'Unavailable'
        else:
            self.light = PlantSensors.try_parse_float(rawVal)

    def update_moisture(self, scanTime=None):
        if scanTime:
            self.moisture_last_scan = scanTime
        else:
            self.moisture_last_scan = time.time()
        rawVal = self.arduino.get_moisture().split(',')
        vals = [0] * len(rawVal)
        for idx, val in enumerate(rawVal):
            vals[idx] = PlantSensors.try_parse_int(val)
        self.moisture = vals

    def print_all(self):
        for idx, val in enumerate(self.moisture):
            print("Moisture ", idx, ":  ", val, sep='')
        print("Temperature:", self.temperature)
        print("Pressure:   ", self.pressure)
        print("Humidity:   ", self.humidity)
        print("Light:      ", self.light)

    @staticmethod
    def try_parse_float(val):
        try:
            return float(val)
        except:
            return 'ReadFailed'

    @staticmethod
    def try_parse_int(val):
        try:
            return int(val)
        except:
            return 'ReadFailed'
    


if __name__ == '__main__':
    p = PlantSensors()
    try:
        while True:
            p.print_all()
            time.sleep(5)
    finally:
        p.stop()
        p.arduino.close()
