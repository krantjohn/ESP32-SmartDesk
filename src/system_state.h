#ifndef SYSTEM_STATE_H
#define SYSTEM_STATE_H

#include <Arduino.h>

struct SystemState
{
    
    float sensor_temp;

    float sensor_hum;

    float weather_temp;

    float weather_hum;

    String city;

    String weather;

    String time;

    bool wifiOK;

    bool weatherOK;
};

extern SystemState systemState;

#endif