#include <Arduino.h>
#include "Wire.h"
#include "U8g2lib.h"
#include "display.h"
#include "sensor.h"
#include "wifilink.h"
#include "time_manager.h"
#include "weather.h"
#include "system_state.h"
#include "menu.h"
#include "page.h"
#include "input.h"

#define SCL 4
#define SDA 5

unsigned long sensorTimer = 0;
unsigned long timeTimer = 0;
unsigned long displayTimer = 0;
unsigned long wifiTimer = 0;
unsigned long weatherTimer=0;
unsigned long inputTimer=0;

bool timeReady = false;
bool weatherReady = false;

U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0 ,U8X8_PIN_NONE);

void setup(){

  Serial.begin(115200);

  Wire.begin(SDA ,SCL);
  
  displayInit();

  wifiInit();

  sensorInit();

  menuInit();

  inputInit();
}


void loop(){

  
  unsigned long now = millis();

  if(now - wifiTimer > 10000){

    wifiTimer = now;
    
    wifiUpdate();
  }

  if(systemState.wifiOK && !timeReady)
  {
    timeInit();
  
    timeReady = true;

  }

  if(systemState.wifiOK && !weatherReady)
  {
    updateWeather();

    weatherReady=true;

  }

  if(now - sensorTimer >= 2000){

    sensorTimer = now;

    updateSensor();
  }

  if(systemState.wifiOK){

    if(now - timeTimer >= 1000){

    timeTimer = now;

    updateTime();
  }
  }

  if(now - weatherTimer >= 1800000){

    weatherTimer = now;

    updateWeather();
  }

  if(now-inputTimer>=20)
  {

    inputTimer=now;

    inputUpdate();

  }


  if(now - displayTimer >= 100){

    displayTimer = now;

    pageUpdate();
  }
  
}
