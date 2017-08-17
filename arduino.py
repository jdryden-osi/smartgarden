import sys
import serial
from time import sleep

if sys.version_info[0] < 3:
	raise Exception("Must be using Python 3")

class Arduino:
	def __init__(self, port = '/dev/ttyACM0'):
		self._con = serial.Serial(port, 9600)
		self._con.setTimeout(10)
		output = ""
		initLines = 0
		while (output != "Ready!" and initLines < 5):
			output = self.readline()
			initLines += 1
		if (output != "Ready!"):
			raise Exception("Cannot connect to Arduino at " + port)
		# sleep 5 seconds to let sensors stabilize
		sleep(5)

	def readline(self):
		return str(self._con.readline().decode().replace('\r\n',''))
	
	def getMoisture(self):
		self._con.write(b'M')
		return self.readline()

	def getLight(self):
		self._con.write(b'L')
		return self.readline()

	def getTemp(self):
		self._con.write(b'T')
		return self.readline()

	def close(self):
		self._con.close()

	
if __name__ == '__main__':
	print("Arduino test")
	print("Connecting... ")
	a = Arduino()
	print("Connected.")

	print("Light: " + a.getLight())
	print("Temp/Press/Humid: " + a.getTemp())
	print("Moisture: " + a.getMoisture())
	a.close()
