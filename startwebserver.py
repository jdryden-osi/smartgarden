import http.server
import time
import glob
import sys
import threading
from plantsensors import PlantSensors

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

address = ('', 80)
plantSensors = PlantSensors(30, 1, 1, '/dev/ttyACM0')

def makeLine():
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    moistures = ""
    for idx, val in enumerate(plantSensors.moisture):
        moistures += "Moisture" + str(idx) + "=" + str(val) + " "
    return '{0} {1}Temp={2} Press={3} Humid={4} Light={5}'.format(
        date,
        moistures,
        plantSensors.temperature,
        plantSensors.pressure,
        plantSensors.humidity,
        plantSensors.light
    )

class WebHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type","text/html")
        self.end_headers()
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>PlantPi01</title></head>",'utf-8'))
        self.wfile.write(bytes("<body><p>",'utf-8'))
        self.wfile.write(bytes(makeLine(),'utf-8'))
        self.wfile.write(bytes("</p></body></html>",'utf-8'))


if __name__ == '__main__':
    webserver = http.server.HTTPServer(address, WebHandler)
    try:
        webserver.serve_forever()
    except KeyboardInterrupt:
        print('Closing Socket.')
        webserver.socket.close()
        exit()

