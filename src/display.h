#ifndef DISPLAY_H
#define DISPLAY_H

#include "U8g2lib.h"




void displayInit ();

void showHome();

void showWeather();

void showSystem();

void showSensor();


extern U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled;

#endif