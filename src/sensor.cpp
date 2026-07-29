#include <Adafruit_SHT31.h>
#include "sensor.h"
#include "system_state.h"

Adafruit_SHT31 sht30;
void sensorInit(){

    sht30.begin(0x44);
}

void updateSensor()
{

systemState.sensor_temp =
sht30.readTemperature();


systemState.sensor_hum =
sht30.readHumidity();

}