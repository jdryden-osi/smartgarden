import serial
from time import sleep

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
			print "Cannot connect to Arduino. Exiting."
			exit()
		sleep(5)

	def readline(self):
		return str(self._con.readline().decode().replace('\r\n',''))
	
	def getMoisture(self):
		self._con.write('M')
		return self.readline()

	def getLight(self):
		self._con.write('L')
		return self.readline()

	def getTemp(self):
		self._con.write('T')
		return self.readline()

	def close(self):
		self._con.close()


if __name__ == '__main__':
	print "Arduino test"
	print "Connecting... "
	a = Arduino()
	print "Connected."

	print "Light: " + a.getLight()
	print "Temp/Humid/Press: " + a.getTemp()
	print "Moisture: " + a.getMoisture()
	a.close()
