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
		init_lines = 0
		while (output != "Ready!" and init_lines < 5):
			output = self.readline()
			init_lines += 1
		if (output != "Ready!"):
			raise Exception("Cannot connect to Arduino at " + port)
		# sleep 5 seconds to let sensors stabilize
		sleep(5)

	def readline(self):
		return str(self._con.readline().decode().replace('\r\n',''))
	
	def get_moisture(self):
		self._con.write(b'M')
		return self.readline()

	def get_light(self):
		self._con.write(b'L')
		return self.readline()

	def get_temperature(self):
		self._con.write(b'T')
		return self.readline()

	def close(self):
		self._con.close()

	
if __name__ == '__main__':
	print("Arduino test")
	print("Connecting... ")
	a = Arduino()
	print("Connected.")

	print("Light: " + a.get_light())
	print("Temp/Press/Humid: " + a.get_temperature())
	print("Moisture: " + a.get_moisture())
	a.close()
