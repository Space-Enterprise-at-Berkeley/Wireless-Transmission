#include <math.h>
#include <solenoids.h>

Solenoids valves;

#define LOW_PRESSURE_1 A0
#define LOW_PRESSURE_2 A1
#define LOW_PRESSURE_3 A2
#define LOW_PRESSURE_4 A3

#define HIGH_PRESSURE_1 A4
#define HIGH_PRESSURE_2 A5

//#define RFSerial Serial1

void readData();
void convertData();

int input = 0;
bool shouldPrint = true;

long currTime = millis();
long currTime2 = millis();

int numLowPressure = 0;
int numHighPressure = 0;

void setup() {
  //If connected to RF, change baud rate from 9600 to 57600
  Serial.begin(57600);

  // Setup solenoids
  valves.init();
  
  
  Serial.println("How many low pressure sensors are connected?");
  while (Serial.available() == 0) {
    
      delay(50);
      if (millis() - currTime > 2000) {
        Serial.println("waiting for low pt #...");
        currTime = millis();
      }
    }
  numLowPressure = Serial.parseInt();
  
//  numLowPressure = Serial.read() - 48;
  
Serial.println("How many high pressure sensors are connected?");
  while (Serial.available() == 0) {
      delay(50);
      if (millis() - currTime > 2000) {
        Serial.println("waiting for high pt #...");
        currTime = millis();
      }
    }

  numHighPressure = Serial.parseInt();

  Serial.print("There are ");
  Serial.print(numLowPressure);
  Serial.print(" low PTs and ");
  Serial.print(numHighPressure);
  Serial.println(" high PTs");

  if(numLowPressure >= 1){
    pinMode(LOW_PRESSURE_1, INPUT);
  }
  if(numLowPressure >= 2){
    pinMode(LOW_PRESSURE_2, INPUT);
  }
  if(numLowPressure >= 3){
    pinMode(LOW_PRESSURE_3, INPUT);
  }
  if(numLowPressure >= 4){
    pinMode(LOW_PRESSURE_4, INPUT);
  }
  if(numHighPressure >= 1){
    pinMode(HIGH_PRESSURE_1, INPUT);
  }
  if(numHighPressure >= 2){
    pinMode(HIGH_PRESSURE_2, INPUT);
  }
  
  Serial.print("high, lox tank, propane tank, lox injector, propane injector\n");

  currTime = millis();
  currTime2 = millis();
}

// 0.88V - 4.4V : ?? - 5000 PSI

int lowPressure1, lowPressure2, lowPressure3, lowPressure4, highPressure1, highPressure2;
int convertedLow1, convertedLow2, convertedLow3, convertedLow4, convertedHigh1, convertedHigh2;

int periodic = 100; // take data 10 times a second.
void loop() {
  currTime = millis();
  if((currTime%int(periodic)) == 0) {
    if (Serial.available() > 0) {
      int readByte = Serial.read();
      if(readByte == 'a') {
        Serial.print("Toggled LOX 2: ");
        Serial.println(valves.toggleLOX2Way());
      } else if(readByte == 'b') {
        Serial.print("Toggled LOX 5: ");
        Serial.println(valves.toggleLOX5Way());
      } else if (readByte == 'c') {
        Serial.print("Toggled LOX Gems: ");
        Serial.println(valves.toggleLOXGems());
      } else if(readByte == 'x') {
        Serial.print("Toggled PROP 2: ");
        Serial.println(valves.toggleProp2Way());
      } else if (readByte == 'y') {
        Serial.print("Toggled PROP 5: ");
        Serial.println(valves.toggleProp5Way());
      } else if (readByte == 'z') {
        Serial.print("Toggled PROP Gems: ");
        Serial.println(valves.togglePropGems());
      } else if (readByte == 'e') {
        Serial.print("Toggled High Pressure: ");
        Serial.println(valves.toggleHighPressureSolenoid());
      }
    }

    readData();
  
    convertData();
    
    //need some check on magnitude of reading to see if we should print data.
    if(shouldPrint){

      if(numHighPressure >= 1){
        //sprintf(toWriteBuffer + bufferIndex, "%d,", convertedHigh1);
        //bufferIndex += String(convertedHigh1).length();
        Serial.print(convertedHigh1);
      } else {
        Serial.print("-1");
      }
//      if(numHighPressure >= 2){
//        //sprintf(toWriteBuffer + bufferIndex, "%d,", convertedHigh2);
//        //bufferIndex += String(convertedHigh2).length();
//        Serial.print(", ");
//        Serial.print(convertedHigh2);
//      }

      Serial.print(", ");
      if(numLowPressure >= 1){
        Serial.print(convertedLow1);
        //Serial.println("Added first low PT reading; 
      } else {
        Serial.print("-1");
      }

      Serial.print(", ");
      if(numLowPressure >= 2){
        //sprintf(toWriteBuffer + bufferIndex, "%d,", convertedLow2);
        //bufferIndex += String(convertedLow2).length();
        Serial.print(convertedLow2);
      } else {
        Serial.print("-1");
      }

      Serial.print(", ");
      if(numLowPressure >= 3){
        //sprintf(toWriteBuffer + bufferIndex, "%d,", convertedLow3);
        //bufferIndex += String(convertedLow3).length();
        Serial.print(convertedLow3);
      } else {
        Serial.print("-1");
      }

      Serial.print(", ");
      if(numLowPressure >= 4){
        //sprintf(toWriteBuffer + bufferIndex, "%d,", convertedLow4);
        //bufferIndex += String(convertedLow4).length();
        Serial.print(convertedLow4);
      } else {
        Serial.print("-1");
      }
      Serial.print("\n");
    }
  }
}

void convertData(){
    switch(numLowPressure){
    case 1:
      convertedLow1 = lowPressureConversion(lowPressure1);
      break;
    case 2:
      convertedLow1 = lowPressureConversion(lowPressure1);
      convertedLow2 = lowPressureConversion(lowPressure2);
      break;
    case 3:
      convertedLow1 = lowPressureConversion(lowPressure1);
      convertedLow2 = lowPressureConversion(lowPressure2);
      convertedLow3 = lowPressureConversion(lowPressure3);
      break;
    case 4:
      convertedLow1 = lowPressureConversion(lowPressure1);
      convertedLow2 = lowPressureConversion(lowPressure2);
      convertedLow3 = lowPressureConversion(lowPressure3);
      convertedLow4 = lowPressureConversion(lowPressure4);
      break;
  }

  switch(numHighPressure){
    case 1:
      convertedHigh1 = highPressureConversion(highPressure1);
      break;
    case 2:
      convertedHigh1 = highPressureConversion(highPressure1);
      convertedHigh2 = highPressureConversion(highPressure2);
      break;
  }
}

void readData(){
  switch(numLowPressure){
    case 1:
      lowPressure1 = analogRead(LOW_PRESSURE_1);
      break;
    case 2:
      lowPressure1 = analogRead(LOW_PRESSURE_1);
      lowPressure2 = analogRead(LOW_PRESSURE_2);
      break;
    case 3:
      lowPressure1 = analogRead(LOW_PRESSURE_1);
      lowPressure2 = analogRead(LOW_PRESSURE_2);
      lowPressure3 = analogRead(LOW_PRESSURE_3);
      break;
    case 4:
      lowPressure1 = analogRead(LOW_PRESSURE_1);
      lowPressure2 = analogRead(LOW_PRESSURE_2);
      lowPressure3 = analogRead(LOW_PRESSURE_3);
      lowPressure4 = analogRead(LOW_PRESSURE_4);
      break;
  }

  switch(numHighPressure){
    case 1:
      highPressure1 = analogRead(HIGH_PRESSURE_1);
      break;
    case 2:
      highPressure1 = analogRead(HIGH_PRESSURE_1);
      highPressure2 = analogRead(HIGH_PRESSURE_2);
      break;
  }
}


float lowPressureConversion(int raw){
  return int(1.2258857538273733*raw - 123.89876445934394);
}

float highPressureConversion(int raw){
    float 
//    return -9083 + (1.239 * pow(10,2) * raw) - 7.17 * pow(10,-1) * pow(raw, 2) + 2.29 * pow(10,-3) * pow(raw, 3);
    float converted = (((float)raw / 1024) - 0.2) * 5000;
    return converted;
//    return -11.3 + 1.53 * converted - 1.0327 * pow(10, -3) * pow(converted, 2) + 1.246 * pow(10, -6) * pow(converted,3);
    
}
