#include <stdlib.h>
#include "HX711.h"
#define EVENING_LIGHT 180 //the maximum lamp brightness in the evening
#define MORNING_LIGHT 255 //the maximum brightness of the lamp in the morning
#define FOTOREZ_LOWER_BOUND 180 //the output of the photoresistor under which the lamp must be fully open
#define FOTOREZ_UPPER_BOUND 500 //the output of the photoresistor over which the lamp should be turned off

HX711 scale;

uint8_t dataPin = A1, clockPin = A0;
uint8_t photoresPin = A2, PWMPin = 3, ledPin = 13;
uint8_t state = 0; //0 - closed, 1 - ongoing evening story; 2 - ongoing morning alarm
uint8_t story_has_begun = 0;
int story_length, counts = 0;
unsigned long tstamp = 0;
uint8_t flag = 0;
float max_value;

void setup() {
  scale.begin(dataPin, clockPin);
  pinMode(photoresPin, INPUT);
  pinMode(PWMPin, OUTPUT);
  pinMode(ledPin, OUTPUT);

  Serial.begin(9600);
  //send a signal on built-in led 13 that they should empty the scale
  for(int i = 0; i < 3; i++) {
    digitalWrite(ledPin, HIGH);
    delay(100);
    digitalWrite(ledPin, LOW);
    delay(100);
  }
  delay(2000);
  scale.tare();

  
  //send a signal on built-in led 13 that they should put the maximum allowed weight on the scale
  digitalWrite(ledPin, HIGH);
  delay(2000);
  scale.calibrate_scale(1000, 10);
  max_value = scale.get_units(10);
  digitalWrite(ledPin, LOW);
  //now the scale is calibrated and the process may begin
  
  delay(2000);
  /*
  //send the calibrated value to python
  while(Serial.available() <= 0);
  if (Serial.available() > 0) {
    String received = Serial.readStringUntil('\n'); // Read command
    received.trim(); // Remove extra spaces or newlines
    // Check for commands with "CMD:" prefix
    if (received.startsWith("CMD:")) {
      received.remove(0, 4); // Remove "CMD:" prefix

      if (received.equals("READ_PIN")) {
        Serial.print("MAX=");
        Serial.println(scale.get_units(10)); // Send the sensor value back to Python
      }
    }
  }
  */
}

int evening_map(unsigned long current_time) { //the function maps the values according to the time passed and the story length
  return (int)EVENING_LIGHT * (((float)(story_length - current_time)) / story_length);
}

int morning_map(int ambientalLight) {
  if(ambientalLight < FOTOREZ_LOWER_BOUND)
    return MORNING_LIGHT;
  if(ambientalLight > FOTOREZ_UPPER_BOUND)
    return 0;
  return (int)((float)MORNING_LIGHT / (FOTOREZ_UPPER_BOUND - FOTOREZ_LOWER_BOUND) * (FOTOREZ_UPPER_BOUND - ambientalLight));
}

void loop() {
  //read incoming data from python
  if (Serial.available() > 0) {
    String received = Serial.readStringUntil('\n'); // Read command
    received.trim(); // Remove extra spaces or newlines
    // Check for commands with "CMD:" prefix
    if (received.startsWith("CMD:")) {
      received.remove(0, 4); // Remove "CMD:" prefix

      if (received.equals("READ_PIN")) {
        if(!flag)
          Serial.println(max_value), flag = 1;
        else
          Serial.println(scale.get_units(10)); // Send the sensor value back to Python
      }
    } else if(received.startsWith("STATE")) {
      received.remove(0, 5);
      if(received.equals("0"))
        state = 0;
      else if(received.equals("1"))
        state = 1, story_has_begun = 0;
      else if(received.equals("2"))
        state = 2;
      else if(received.equals("3"))
        state = 3;
      else if(received.equals("4"))
        state = 4;
    } else if(received.startsWith("SL")) {
      received.remove(0, 2);
      story_has_begun = 1;
      tstamp = millis() / 1000;
      story_length = received.toInt();
    }
  }

  if(state == 4) {
    int photorez_value = analogRead(photoresPin);
    analogWrite(PWMPin, morning_map(photorez_value));
  }
  if(state == 1 || state == 2) {
    if(story_has_begun) {
      analogWrite(PWMPin, evening_map((millis()/1000 - tstamp)));
    }
    else {
      analogWrite(PWMPin, EVENING_LIGHT);
    }
  }
  if(state == 3) {
    analogWrite(PWMPin, 0);
  }
  if(state == 0) {
    analogWrite(PWMPin, 0);
  }
  
}