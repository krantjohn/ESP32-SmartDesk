#include <Arduino.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "weather.h"
#include "system_state.h"
#include "config.h"
#include <WiFi.h>

const char* url = WEATHER_API_URL;


void weatherInit(){

    systemState.city = "unknow";

    systemState.weather= "unknow";

    systemState.weather_hum = 0;

    systemState.weather_temp = 0;
}

void updateWeather(){

    HTTPClient http;

    if(WiFi.status()!=WL_CONNECTED)
    {

    return;

    }

    http.begin(url);

    int code = http.GET();

    if(code == 200){

        String payload = http.getString();

        Serial.println(payload);

        DynamicJsonDocument doc(2048);

        DeserializationError error = deserializeJson(doc ,payload);

        if(error)
        {
            Serial.println("JSON error");
            return;
        }
        JsonObject result = doc["result"];
        JsonObject realtime = result["realtime"];

        systemState.city = result["city"].as<String>();
        systemState.weather_temp = realtime["temperature"].as<float>();
        systemState.weather_hum = realtime["humidity"].as<float>();
        systemState.weather = realtime["info"].as<String>();

        systemState.weatherOK = true;

    }
    else
    {

    Serial.print("HTTP error:");
    Serial.println(code);

    systemState.weatherOK = false;

    }

    http.end();

}

