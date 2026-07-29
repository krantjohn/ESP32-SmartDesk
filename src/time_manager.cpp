#include "time_manager.h"
#include <Arduino.h>
#include "time.h"
#include "system_state.h"


const char* ntpSever = "pool.ntp.org";
const long gmtOffset = 8 * 3600;
const int daylighhtOffset_sec = 0;

void timeInit(){
    //设置时区偏移和NTP服务器
    configTime (gmtOffset ,daylighhtOffset_sec ,ntpSever);
}

void updateTime(){

    struct  tm timeinfo;
  
    if(!getLocalTime(&timeinfo)){
        systemState.time = "Time ERROR";
        return;
    }

    char buffer[30];
    sprintf (
        buffer,
        "%04d-%02d-%02d %02d:%02d:%02d",
        timeinfo.tm_year+1900,
        timeinfo.tm_mon+1,
        timeinfo.tm_mday,
        timeinfo.tm_hour,
        timeinfo.tm_min,
        timeinfo.tm_sec
    );

    systemState.time = String(buffer);

}