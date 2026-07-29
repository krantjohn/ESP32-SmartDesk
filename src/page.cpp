#include "page.h"
#include "display.h"
#include "menu.h"

Page currentPage = HOME_PAGE;

int menuIndex = 0;


void pageNext()
{
    if(currentPage == MENU_PAGE)
    {

        menuIndex++;

        if(menuIndex > 2)
        {
            menuIndex = 0;
        }
    }
}

void pagePrev()
{
    if(currentPage == MENU_PAGE)
    {
        menuIndex--;

        if(menuIndex < 0)
        {
            menuIndex = 2;
        }
    }
}

void pageEnter()
{
    if(currentPage == MENU_PAGE)
    {
        switch(menuIndex)
        {
            case 0:

                currentPage = SENSOR_PAGE;

                break;

            case 1:

                currentPage = WEATHER_PAGE;

                break;

            case 2:

                currentPage = SYSTEM_PAGE;

                break;
        }
    }
}

void pageBack()
{
    switch(currentPage)
    {
        case MENU_PAGE:

            currentPage = HOME_PAGE;

            break;

        case WEATHER_PAGE:
        case SENSOR_PAGE:
        case SYSTEM_PAGE:

            currentPage = MENU_PAGE;

            break;
    }
}

void pageUpdate()
{

    switch(currentPage)
    {
        case HOME_PAGE:

            showHome();

            break;

        case WEATHER_PAGE:

            showWeather();

            break;

        case MENU_PAGE:

            showMenu();

            break;

        case SYSTEM_PAGE:

            showSystem();

            break;

        case SENSOR_PAGE:

            showSensor();

            break;
    }
}