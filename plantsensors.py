import time
import sys
import threading
from arduino import Arduino
from repeatedtimer import RepeatedTimer

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")


class PlantSensors(object):
    def __init__(self, port='/dev/ttyACM0'):
        self.arduino = Arduino(port)
        self.moisture = None
        self.temperature = None
        self.pressure = None
        self.humidity = None
        self.light = None
        
        self.lightInterval = 5
        self.tempInterval = 5
        self.moistureInterval = 30
        self.lastTempScan = None
        self.lastLightScan = None
        self.lastMoistureScan = None
        self.serialBusy = False

        self.updateTemperature()
        self.updateLight()
        self.updateMoisture()

        self.updateTimer = RepeatedTimer(1, self.onScan)

    def stop(self):
        self.updateTimer.stop()

    def onScan(self):
        if not self.serialBusy:
            self.serialBusy = True
            now = time.time()
            try:
                if (now - self.lastTempScan > self.tempInterval):
                    self.updateTemperature(now)
                if (now - self.lastLightScan > self.lightInterval):
                    self.updateLight(now)
                if (now - self.lastMoistureScan > self.moistureInterval):
                    self.updateMoisture(now)
            finally:
                self.serialBusy = False

    def updateTemperature(self, scanTime=None):
        if scanTime:
            self.lastTempScan = scanTime
        else:
            self.lastTempScan = time.time()
        rawVal = self.arduino.getTemp().split(',')
        if rawVal == ['Unavailable']:
            self.temperature = 'Unavailable'
            self.pressure = 'Unavailable'
            self.humidity = 'Unavailable'
        elif len(rawVal) == 3:
            self.temperature = PlantSensors.tryParseFloat(rawVal[0])
            self.pressure = PlantSensors.tryParseFloat(rawVal[1])
            self.humidity = PlantSensors.tryParseFloat(rawVal[2])
        else:
            self.temperature = 'ReadFailed'
            self.pressure = 'ReadFailed'
            self.humidity = 'ReadFailed'

    def updateLight(self, scanTime=None):
        if scanTime:
            self.lastLightScan = scanTime
        else:
            self.lastLightScan = time.time()
        rawVal = self.arduino.getLight()
        if rawVal == 'Unavailable':
            self.light = 'Unavailable'
        else:
            self.light = PlantSensors.tryParseFloat(rawVal)

    def updateMoisture(self, scanTime=None):
        if scanTime:
            self.lastMoistureScan = scanTime
        else:
            self.lastMoistureScan = time.time()
        rawVal = self.arduino.getMoisture().split(',')
        vals = [0] * len(rawVal)
        for idx, val in enumerate(rawVal):
            vals[idx] = PlantSensors.tryParseFloat(val)
        self.moisture = vals

    def printAll(self):
        for idx, val in enumerate(self.moisture):
            print("Moisture ", idx, ":  ", val, sep='')
        print("Temperature:", self.temperature)
        print("Pressure:   ", self.pressure)
        print("Humidity:   ", self.humidity)
        print("Light:      ", self.light)

    @staticmethod
    def tryParseFloat(strVal):
        try:
            return float(strVal)
        except:
            return 'ReadFailed'
    


if __name__ == '__main__':
    p = PlantSensors()
    try:
        while True:
            p.printAll()
            time.sleep(5)
    finally:
        p.stop()
        p.arduino.close()
