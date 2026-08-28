#include <Arduino.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include "uploader.h"
#include "system_state.h"
#include "config.h"

static unsigned long lastUploadTime = 0;

void uploaderInit() {
    lastUploadTime = 0;
    Serial.println("[Uploader] Initialized. Target URL: " SERVER_UPLOAD_URL);
}

bool uploadDataNow() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[Uploader] WiFi not connected, skipping upload.");
        return false;
    }

    HTTPClient http;
    http.begin(SERVER_UPLOAD_URL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Connection", "close"); // 显式短连接，避免连接丢失
    http.setTimeout(5000); // 5秒超时保护

    // 构建 JSON 报文
    StaticJsonDocument<512> doc;
    doc["device_id"] = "ESP32S3_SmartDesk";
    doc["indoor_temp"] = isnan(systemState.sensor_temp) ? 0.0 : systemState.sensor_temp;
    doc["indoor_hum"] = isnan(systemState.sensor_hum) ? 0.0 : systemState.sensor_hum;
    doc["city"] = systemState.city.isEmpty() ? "衡水" : systemState.city;
    doc["outdoor_temp"] = systemState.weather_temp;
    doc["outdoor_hum"] = systemState.weather_hum;
    doc["weather"] = systemState.weather.isEmpty() ? "晴" : systemState.weather;
    doc["timestamp"] = systemState.time;

    String jsonString;
    serializeJson(doc, jsonString);

    Serial.print("[Uploader] Uploading to " SERVER_UPLOAD_URL " ... Payload: ");
    Serial.println(jsonString);

    int httpResponseCode = http.POST(jsonString);

    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.printf("[Uploader] SUCCESS! HTTP Code: %d, Server Reply: %s\n", httpResponseCode, response.c_str());
        http.end();
        return true;
    } else {
        Serial.printf("[Uploader] Error sending POST: %s (Error code: %d)\n", http.errorToString(httpResponseCode).c_str(), httpResponseCode);
        http.end();
        return false;
    }
}

void uploaderUpdate() {
    unsigned long now = millis();
    if (now - lastUploadTime >= SERVER_UPLOAD_INTERVAL_MS) {
        lastUploadTime = now;
        uploadDataNow();
    }
}
