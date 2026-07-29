#include <Arduino.h>
#include "menu.h"
#include "display.h"
#include "U8g2lib.h"
#include "page.h"



String menuList[] = 
{
    "室内环境",
    "天气信息",
    "系统状态"
};

void menuInit(){

    menuIndex = 0;

}


void menuUpdate()
{

}

void showMenu()
{
    oled.clearBuffer();

    oled.setFont(u8g2_font_wqy12_t_gb2312);

    oled.drawUTF8(
        0,
        15,
        "智能桌面"
    );

    for(int i=0; i<3; i++)
    {
        if(i == menuIndex)
        {
            oled.drawUTF8(
                0,
                32+i*12,
                ">"
            );
            

            
        }

        oled.drawUTF8(
            15,
            32+i*12,
            menuList[i].c_str()
        );
    }

    oled.sendBuffer();

   
}


