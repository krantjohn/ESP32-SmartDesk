#pragma once

// ==========================================
// 1. I2C 引脚定义 (OLED & SHT30)
// ==========================================
#define I2C_SDA_PIN 5
#define I2C_SCL_PIN 4

// ==========================================
// 2. 按键引脚定义 (输入上拉，低电平有效)
// ==========================================
#define KEY_UP_PIN 9
#define KEY_DOWN_PIN 10
#define KEY_OK_PIN 11
#define KEY_BACK_PIN 12

// ==========================================
// 3. 旋转编码器引脚定义 (EC11)
// ==========================================
#define ENC_A_PIN 35
#define ENC_B_PIN 36
#define ENC_SW_PIN 37

// ==========================================
// 4. WiFi 连接配置
// ==========================================
#define DEFAULT_WIFI_SSID "CMCC-PEQ4"
#define DEFAULT_WIFI_PASS "12345678"

// ==========================================
// 5. 天气 API 配置 (聚合数据 simpleWeather)
// ==========================================
#define WEATHER_CITY "枣强"
#define WEATHER_API_KEY "3960a914d88cf4838b1f5baecfa3c6b9"
#define WEATHER_API_URL "https://apis.juhe.cn/simpleWeather/query?city=" WEATHER_CITY "&key=" WEATHER_API_KEY

// ==========================================
// 6. NTP 网络授时配置
// ==========================================
#define NTP_SERVER "pool.ntp.org"
#define GMT_OFFSET_SEC (8 * 3600)  // 东八区北京时间 (UTC+8)
#define DAYLIGHT_OFFSET_SEC 0
