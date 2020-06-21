#include <math.h>

#define LOW_PRESSURE_1 A0
#define LOW_PRESSURE_2 A1
#define LOW_PRESSURE_3 A2
#define LOW_PRESSURE_4 A3

#define HIGH_PRESSURE_1 A4
#define HIGH_PRESSURE_2 A5

int input = 0;
bool shouldPrint = false;

long currTime = millis();

int numLowPressure = 0;
int numHighPressure = 0;

void setup() {
  Serial.begin(9600);

  while(!Serial.available());
  
  Serial.println("How many low pressure sensors are connected?");
  while (!Serial.available());
  
  numLowPressure = Serial.read() - 48;
  
  Serial.println("How many high pressure sensors are connected?");
  while (!Serial.available());

  numHighPressure = Serial.read() - 48;

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

  Serial.print("There are ");
  Serial.print(numLowPressure);
  Serial.print(" low PTs and ");
  Serial.print(numHighPressure);
  Serial.println(" high PTs");
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
      if(readByte == 't'){
        shouldPrint = true;
      } else if(readByte == 'f'){
        shouldPrint = false;
      } else if(readByte == '0'){
        shouldPrint = !shouldPrint;
      }
    }
  
    readData();
  
    convertData();
    
    //need some check on magnitude of reading to see if we should print data.
    if(shouldPrint){
      if(numLowPressure >= 1){
        Serial.print(convertedLow1);
        //Serial.println("Added first low PT reading; 
      }
      if(numLowPressure >= 2){
        //sprintf(toWriteBuffer + bufferIndex, "%d,", convertedLow2);
        //bufferIndex += String(convertedLow2).length();
        Serial.print(", ");
        Serial.print(convertedLow2);
      }
      if(numLowPressure >= 3){
        //sprintf(toWriteBuffer + bufferIndex, "%d,", convertedLow3);
        //bufferIndex += String(convertedLow3).length();
        Serial.print(", ");
        Serial.print(convertedLow3);
      }
      if(numLowPressure >= 4){
        //sprintf(toWriteBuffer + bufferIndex, "%d,", convertedLow4);
        //bufferIndex += String(convertedLow4).length();
        Serial.print(", ");
        Serial.print(convertedLow4);
      }

      if(numHighPressure >= 1){
        //sprintf(toWriteBuffer + bufferIndex, "%d,", convertedHigh1);
        //bufferIndex += String(convertedHigh1).length();
        Serial.print(", ");
        Serial.print(convertedHigh1);
      }
      if(numHighPressure >= 2){
        //sprintf(toWriteBuffer + bufferIndex, "%d,", convertedHigh2);
        //bufferIndex += String(convertedHigh2).length();
        Serial.print(", ");
        Serial.print(convertedHigh2);
      }
      Serial.print("\n");
      
      //String toWrite = String(converted_inject_low)+','+String(converted_prop_low); // +','+String(converted_prop_high); //+','+String(converted_high_prop);
      //Serial.println(toWriteBuffer);
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
  return (6.612739309669555*(raw - 0.88 / 4.4 * 1024)); //- 1237.7612969223858);
}
