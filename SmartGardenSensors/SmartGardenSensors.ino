#include <Wire.h>
#include <Adafruit_BME280.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2561_U.h>

#define BME280_I2C_ADDR 0x76 

Adafruit_BME280 bme;
Adafruit_TSL2561_Unified tsl = Adafruit_TSL2561_Unified(TSL2561_ADDR_FLOAT, 12345);
bool bmeAvailable = 1;
bool tslAvailable = 1;

int moistureNumPins = 3;
int moisturePins[] = {A0, A1, A2};
int moisturePowerNumPins = 1;
int moisturePowerPins[] = {2};

// Use pin 13 so the onboard LED mirrors the lampControlPin state
int lampControlPin = 13;

// *********************************************
// Initialize the temperature, humidity, and pressure sensor.
// Sensor board: BME280
// https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout/overview
//
void initBME280()
{
  bool bmeStatus = bme.begin(BME280_I2C_ADDR);
  if (!bmeStatus) {
        Serial.println("# Could not find a valid BME280 sensor, check wiring!");
        bmeAvailable = 0;
  }
}

// *********************************************
// Initialize the light sensor.
// Sensor board: TSL2561
// https://learn.adafruit.com/tsl2561/use?view=all#overview
//
void initTSL2561()
{
  tsl.enableAutoRange(true); //Auto-gain ... switches automatically between 1x and 16x
  tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_101MS);  // medium resolution and speed 
  
  // TSL library does not report status if sensor not connected, have to do it manually
  Wire.beginTransmission(TSL2561_ADDR_FLOAT);
  bool tslStatus = Wire.endTransmission();
  if (tslStatus != 0) {
    Serial.println("# Could not find a valid TSL2561 sensor, check wiring!");
    tslAvailable = 0;
    delay(1000);
  }
  tsl.begin();
}

// *********************************************
// Initialize pins for moisture sensors
//
void initMoisture()
{
  for(byte i=0; i<moisturePowerNumPins; ++i)
  {
    pinMode(moisturePowerPins[i], OUTPUT);
    digitalWrite(moisturePowerPins[i], LOW);
  }
}

// *********************************************
// Print a light reading in lux.
// 
void printLux()
{
  if(!tslAvailable)
  {
    Serial.println("Unavailable");
  }
  else
  {
    sensors_event_t tslEvent;
    tsl.getEvent(&tslEvent);
    Serial.println(tslEvent.light);
  }
}

// *********************************************
// Print the temperature, humidity, and pressure
//
void printTemp()
{
  if(!bmeAvailable)
  {
    Serial.println("Unavailable");
  }
  else
  {
    Serial.print(bme.readTemperature()); Serial.print(",");
    Serial.print(bme.readPressure() / 100.0F); Serial.print(",");
    Serial.println(bme.readHumidity());
  }
}

// *********************************************
// Print all moisture readings
// 
void printMoisture()
{
  for(byte i=0; i<moisturePowerNumPins; ++i)
  {
    digitalWrite(moisturePowerPins[i], HIGH);
  }

  // wait 5 seconds to allow sensors to stabilize
  delay(5000);
  
  for(byte i=0; i<moistureNumPins; ++i)
  {
    long sum = 0;
    for(byte j=0; j<8; ++j) 
    {
      sum += analogRead(moisturePins[i]);
      delay(5);
    }
    if(i != 0) Serial.print(",");
    Serial.print(sum >> 3);
  }
  Serial.println();

  for(byte i=0; i<moisturePowerNumPins; ++i)
  {
    digitalWrite(moisturePowerPins[i], LOW);
  }
}

void setup() {
  Serial.begin(9600);
  Serial.println("# SmartGardenSensors.ino");

  initBME280();
  initTSL2561();
  initMoisture();
  pinMode(lampControlPin, OUTPUT);
  digitalWrite(lampControlPin, LOW);

  Serial.println("Ready!");
}

void loop() {
  
  while(Serial.available())
  {
    int incomingByte = Serial.read();
    switch(incomingByte)
    {
      case 'M':
        //Serial.println("Moisture");
        printMoisture();
        break;
      case 'L':
        //Serial.println("Light");
        printLux();
        break;
      case 'T':
        //Serial.println("Temp");
        printTemp();
        break;
      case '1':
        //Serial.println("Lamp On");
        digitalWrite(lampControlPin, HIGH);
        break;
      case '0':
        //Serial.println("Lamp Off");
        digitalWrite(lampControlPin, LOW);
        break;
    }
  }
}
