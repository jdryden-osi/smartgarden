import http.server
import time
import glob
import sys
import threading
from smartgarden import SmartGarden

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

address = ('', 80)
smartgarden = SmartGarden(port='/dev/ttyACM0', moisture_scan=1800, temp_scan=1, light_scan=1)

def make_line():
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    moistures = ""
    for idx, val in enumerate(smartgarden.moisture):
        moistures += "Moisture" + str(idx) + "=" + str(val) + " "
    return '{0} {1}Temp={2} Press={3} Humid={4} Light={5}'.format(
        date,
        moistures,
        smartgarden.temperature,
        smartgarden.pressure,
        smartgarden.humidity,
        smartgarden.light
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
        self.wfile.write(bytes(make_line(),'utf-8'))
        self.wfile.write(bytes("</p></body></html>",'utf-8'))


if __name__ == '__main__':
    webserver = http.server.HTTPServer(address, WebHandler)
    try:
        webserver.serve_forever()
    except KeyboardInterrupt:
        print('Closing Socket.')
        webserver.socket.close()
        smartgarden.stop()
        exit()

