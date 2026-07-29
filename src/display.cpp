#include "U8g2lib.h"
#include "display.h"
#include "system_state.h"
#include "page.h"
#include <Arduino.h>


extern U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled;

void displayInit(){

    oled.begin();
}

void showHome(){

    oled.clearBuffer();

    oled.setFont(u8g2_font_wqy12_t_gb2312);

    oled.drawUTF8(0 ,12 ,"智能桌面");

    if(systemState.wifiOK)
    {
        oled.drawUTF8(80 ,12 ,"WIFI OK");
    }
    else
    {
        oled.drawUTF8(80 ,12 ,"WIFI 不OK");
    }

  
    oled.drawUTF8(0 ,30 ,systemState.time.c_str());

    oled.sendBuffer();

}

void showWeather()

{

    oled.clearBuffer();

    oled.setFont(u8g2_font_wqy12_t_gb2312);

    oled.drawUTF8(
        0,
        15,
        systemState.city.c_str()
    );

    char buf[30];

    sprintf(
        buf,
        "%s %.1fC",
        systemState.weather.c_str(),
        systemState.weather_temp
    );

    oled.drawUTF8(
        0,
        35,
        buf
    );


    sprintf(
        buf,
        "湿度 %.1f%%",
        systemState.weather_hum
    );


    oled.drawUTF8(
        0,
        55,
        buf
    );

    oled.sendBuffer();

}


void showSystem()
{
    oled.clearBuffer();


    oled.setFont(u8g2_font_wqy12_t_gb2312);


    oled.drawUTF8(
        0,
        12,
        "SmartDesk 系统"
    );

    char buf[30];

    sprintf(
        buf,
        "芯片：%s",
        ESP.getChipModel()
    );

    oled.drawUTF8(
        0,
        27,
        buf
    );

    sprintf(
        buf,
        "RAM:%dkB",
        ESP.getFreeHeap()
    );

    oled.drawUTF8(
        0,
        42,
        buf
    );

    unsigned long sec = millis()/1000;

    int h = sec/3600;
    int m = (sec%3600)/60;
    int s = sec%60;

    sprintf(
        buf,
        "运行:%02d:%02d:%02d",
        h,m,s
    );

    oled.drawUTF8(
        0,
        57,
        buf
    );


    oled.sendBuffer();
}




void showSensor()
{

    oled.clearBuffer();


    oled.setFont(u8g2_font_wqy12_t_gb2312);

    oled.drawUTF8(
        0,
        15,
        "环境监测"
    );


    char buf[20];


    sprintf(
        buf,
        "温度 %.1f C",
        systemState.sensor_temp
    );


    oled.drawUTF8(
        0,
        35,
        buf
    );


    sprintf(
        buf,
        "湿度 %.1f %% ",
        systemState.sensor_hum
    );


    oled.drawUTF8(
        0,
        55,
        buf
    );


    oled.sendBuffer();

}