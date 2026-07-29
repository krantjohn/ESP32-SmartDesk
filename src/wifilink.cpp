#include <WiFi.h>
#include <Arduino.h>
#include "wifilink.h"
#include "system_state.h"


const char* ssid = "CMCC-PEQ4";
const char* password = "12345678";



void wifiInit(){

    WiFi.begin(ssid, password);

    Serial.println("Start Connecting WiFi");
}

void wifiUpdate(){

    if(WiFi.status()==WL_CONNECTED)
    {

        systemState.wifiOK=true;

        Serial.print("WIFI TRUE");

    }
    else
    {

        systemState.wifiOK=false;

        Serial.print("WIFI FALSE");

        WiFi.reconnect();



    }


}
