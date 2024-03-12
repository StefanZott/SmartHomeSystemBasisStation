/*
 * wifi.h
 *
 *  Created on: 22.09.2022
 *      Author: Stefan Zott
 */

#ifndef MAIN_WIFI_H_
#define MAIN_WIFI_H_

#include "main.h"
#include "esp_netif.h"
#include "esp_wifi.h"

#define SCAN_LIST_SIZE              10
#define AP_ESP_WIFI_PASS            "telegaertner"
#define AP_ESP_WIFI_CHANNEL         1
#define AP_MAX_STA_CONN             2     // Ganz bewusste Beschränkung, damit nicht mehrere gleichzeitig auf Konfigurationsseite zugreifen

typedef enum
{
   ACCESS_POINT,
   STATION_CONNECTING,
   STATION_CONNECTED,
   STATION_INDICATE_SCAN,
   STATION_SCANNING,
   STATION_STOP
} WIFI_STATE_TYPE;

typedef enum {
   START_STATION,
   START_AP
} WIFI_QUEUE_TYPE;

typedef struct wifiConfigMessage_t {
   unsigned char state;
   unsigned char flag;
   char ssid[MAX_CRED_LEN];
   char password[2 * MAX_CRED_LEN];
} wifiConfigMessage;

extern WIFI_STATE_TYPE wifiState;
extern QueueHandle_t xWifiConfigQueue;
extern SemaphoreHandle_t xWifiStateMutex;
extern char ssidList[SCAN_LIST_SIZE][MAX_CRED_LEN];
extern const char *wifiConfigFile;

void wifiControlTask( void *pvParameters );
void wifi_init_sta_and_softap(void);
int getWifiState();
char* getSSID();

#endif /* MAIN_WIFI_H_ */