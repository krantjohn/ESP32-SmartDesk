#include <WiFi.h>
#include <Arduino.h>
#include "wifilink.h"
#include "system_state.h"
#include "config.h"

const char* ssid = DEFAULT_WIFI_SSID;
const char* password = DEFAULT_WIFI_PASS;



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
