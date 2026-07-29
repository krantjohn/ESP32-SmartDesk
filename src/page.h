#ifndef PAGE_H
#define PAGE_H

enum Page
{
    HOME_PAGE,
    WEATHER_PAGE,
    SENSOR_PAGE,
    MENU_PAGE,
    SYSTEM_PAGE

};


extern Page currentPage;

extern int menuIndex;

void pageNext();

void pagePrev();

void pageEnter();

void pageUpdate();

void pageBack();


#endif