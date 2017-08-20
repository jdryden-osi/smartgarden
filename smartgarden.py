import time
import sys
from arduino import Arduino
from repeatedtimer import RepeatedTimer

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")


class SmartGarden(object):
    def __init__(self, port='/dev/ttyACM0', moisture_scan=3600, temp_scan=5, light_scan=5, autostart=True):
        # Scan intervals in seconds
        self.light_scan = light_scan
        self.temp_scan = temp_scan
        self.moisture_scan = moisture_scan
        
        # Sensor reading variables
        self.moisture = None
        self.temperature = None
        self.pressure = None
        self.humidity = None
        self.light = None
        
        # Last scan times for each sensor type
        self.temp_last_scan = None
        self.light_last_scan = None
        self.moisture_last_scan = None
        
        # Connect to Arduino and get initial sensor readings
        self.arduino = Arduino(port)
        self.update_temperature()
        self.update_light()
        self.update_moisture()
        
        # Create/start timer to update readings in the background
        self.serial_busy = False
        self.update_timer = RepeatedTimer(1, self.on_scan, autostart)

    def start(self):
        self.update_timer.start()

    def stop(self):
        self.update_timer.stop()

    def on_scan(self):
        # Only run if another thread is not currently using serial comms
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
            self.temperature = SmartGarden.try_parse_float(rawVal[0])
            self.pressure = SmartGarden.try_parse_float(rawVal[1])
            self.humidity = SmartGarden.try_parse_float(rawVal[2])
        else:
            # Should only get here if response is malformed
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
            self.light = SmartGarden.try_parse_float(rawVal)

    def update_moisture(self, scanTime=None):
        # Number of moisture readings is determined by Arduino sketch
        # Parse all that arrive into array in self.moisture
        if scanTime:
            self.moisture_last_scan = scanTime
        else:
            self.moisture_last_scan = time.time()
        rawVal = self.arduino.get_moisture().split(',')
        vals = [0] * len(rawVal)
        for idx, val in enumerate(rawVal):
            vals[idx] = SmartGarden.try_parse_int(val)
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
    p = SmartGarden()
    try:
        while True:
            p.print_all()
            time.sleep(5)
    finally:
        p.stop()
        p.arduino.close()
