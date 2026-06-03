/*
* main.h
*
*  Created on: 27.12.2023
*      Author: Stefan Zott
*/

#ifndef MAIN_H_
#define MAIN_H_

#include "driver/gpio.h"
#include "cJSON.h"

#define MAX_CRED_LEN       32       // WLAN SSID and password: max. 31 chars + null terminator

#define PRO_CPU             0       // Explicit assignment to the first CPU core
#define APP_CPU             1       // Second CPU core; naming follows the ESP-IDF API

typedef enum ledModi {
   LED_EIN,
   LED_SCHWELLE,
   LED_AUS
} LED_MODE_T;

extern SemaphoreHandle_t xLedMutex;
extern SemaphoreHandle_t xLedSemaphore;
extern const char *FW_Version, *productName;
extern cJSON* config;

#endif /* MAIN_H_ */