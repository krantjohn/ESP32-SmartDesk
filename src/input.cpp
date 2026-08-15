#include <Arduino.h>

#include "input.h"
#include "page.h"
#include "config.h"

volatile int encoderValue = 0;

int lastA = HIGH;

int8_t table[16] =
{
0,-1,1,0,
1,0,0,-1,
-1,0,0,1,
0,1,-1,0
};

void encoderUpdate();

void inputInit()
{
    pinMode(KEY_UP_PIN, INPUT_PULLUP);
    pinMode(KEY_DOWN_PIN, INPUT_PULLUP);
    pinMode(KEY_OK_PIN, INPUT_PULLUP);
    pinMode(KEY_BACK_PIN, INPUT_PULLUP);
    pinMode(ENC_A_PIN, INPUT_PULLUP);
    pinMode(ENC_B_PIN, INPUT_PULLUP);

    lastA = digitalRead(ENC_A_PIN);
}


void inputUpdate()
{
    encoderUpdate();

    if(encoderValue > 0)
    {
        pageNext();

        encoderValue = 0;
    }
    
     if(encoderValue < 0)
    {
        pagePrev();

        encoderValue = 0;
    }

    static bool lastUp=HIGH;
    static bool lastDown=HIGH;
    static bool lastOK=HIGH;
    static bool lastBack=HIGH;

    bool up = digitalRead(KEY_UP_PIN);
    bool down = digitalRead(KEY_DOWN_PIN);
    bool ok = digitalRead(KEY_OK_PIN);
    bool back = digitalRead(KEY_BACK_PIN);



    if(lastUp == HIGH && up == LOW)
    {
        pagePrev();
    }

    if(lastDown == HIGH && down == LOW)
    {
        pageNext();
    }

    if(lastBack == HIGH && back ==LOW)
    {
        pageBack();
    }

    if(lastOK == HIGH && ok == LOW)
    {

        if(currentPage == HOME_PAGE)
        
        {
            currentPage = MENU_PAGE;
        }
        else
        {
            pageEnter();
        }
    }

    lastUp = up;
    lastDown = down;
    lastOK = ok;
    lastBack = back;
}

void encoderUpdate()
{

    static uint8_t oldState = 0;


    uint8_t state = 0;

    state |= digitalRead(ENC_A_PIN)<<1;
    state |= digitalRead(ENC_B_PIN);


    uint8_t index = (oldState << 2) | state;


    int8_t move = table[index];


    if(move == 1)
    {
        encoderValue++;
    }

    if(move == -1)
    {
        encoderValue--;
    }


    oldState = state;
}