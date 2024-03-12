/*
 * main.h
 *
 *  Created on: 27.12.2023
 *      Author: Stefan Zott
 */
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_mac.h"
#include "aes/esp_aes.h"

#include "WLAN.h"
#include "cJSON.h"
#include "FileManagment.h"
#include "LED.h"

/* The event group allows multiple bits for each event, but we only care about two events:
 * - we are connected to the AP with an IP
 * - we failed to connect after the maximum amount of retries */
#define WIFI_CONNECTED_BIT                  BIT0
#define WIFI_FAIL_BIT                       BIT1
/* AP Configuration */
#define EXAMPLE_ESP_WIFI_AP_SSID            CONFIG_ESP_WIFI_AP_SSID
#define EXAMPLE_ESP_WIFI_AP_PASSWD          CONFIG_ESP_WIFI_AP_PASSWORD
#define EXAMPLE_ESP_WIFI_CHANNEL            CONFIG_ESP_WIFI_AP_CHANNEL
#define EXAMPLE_MAX_STA_CONN                CONFIG_ESP_MAX_STA_CONN_AP
#define AP_ESP_WIFI_PASS                    "telegaertner"
#define AP_ESP_WIFI_CHANNEL                 1
#define AP_MAX_STA_CONN                     2     // Ganz bewusste Beschränkung, damit nicht mehrere gleichzeitig auf Konfigurationsseite zugreifen

/* STA Configuration */
#define EXAMPLE_ESP_WIFI_STA_SSID           CONFIG_ESP_WIFI_REMOTE_AP_SSID
#define EXAMPLE_ESP_WIFI_STA_PASSWD         CONFIG_ESP_WIFI_REMOTE_AP_PASSWORD
#define EXAMPLE_ESP_MAXIMUM_RETRY           CONFIG_ESP_MAXIMUM_STA_RETRY

#if CONFIG_ESP_WIFI_AUTH_OPEN
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD   WIFI_AUTH_OPEN
#elif CONFIG_ESP_WIFI_AUTH_WEP
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD   WIFI_AUTH_WEP
#elif CONFIG_ESP_WIFI_AUTH_WPA_PSK
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD   WIFI_AUTH_WPA_PSK
#elif CONFIG_ESP_WIFI_AUTH_WPA2_PSK
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD   WIFI_AUTH_WPA2_PSK
#elif CONFIG_ESP_WIFI_AUTH_WPA_WPA2_PSK
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD   WIFI_AUTH_WPA_WPA2_PSK
#elif CONFIG_ESP_WIFI_AUTH_WPA3_PSK
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD   WIFI_AUTH_WPA3_PSK
#elif CONFIG_ESP_WIFI_AUTH_WPA2_WPA3_PSK
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD   WIFI_AUTH_WPA2_WPA3_PSK
#elif CONFIG_ESP_WIFI_AUTH_WAPI_PSK
#define ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD   WIFI_AUTH_WAPI_PSK
#endif

#define AES_BLOCKLEN                        16

static const wifi_scan_time_t wifiScanTime = {
      { 0, 0 },            // wifi_active_scan_time_t active { min, max }, default 0 = 120 ms
      320                  // uint32_t passive
};                         // Zeiten in ms
/*
 * Strukturen für AP mit eigener IP-Adresse. Es soll das Nuller-Netz statt dem Vierer-Netz sein.
 * Entnahme aus esp_netif/include/esp_netif_types.h
 * Verzicht auf const bei esp_netif_inherent_ap_config wegen Warnung bei Verwendung als Funktionsparameter.
 * Dann opfere ich halt die 34 Byte im RAM, so knapp ist es nicht.
 */
static const esp_netif_ip_info_t esp_netif_soft_ap_ip = {
   .ip = { .addr = ESP_IP4TOADDR( 192, 168, 0, 1) },
   .gw = { .addr = ESP_IP4TOADDR( 192, 168, 0, 1) },
   .netmask = { .addr = ESP_IP4TOADDR( 255, 255, 255, 0) },
};

static esp_netif_inherent_config_t esp_netif_inherent_ap_config = {
   .flags = (esp_netif_flags_t)(ESP_NETIF_DHCP_SERVER | ESP_NETIF_FLAG_AUTOUP),
   ESP_COMPILER_DESIGNATED_INIT_AGGREGATE_TYPE_EMPTY(mac)
   .ip_info = &esp_netif_soft_ap_ip,
   .get_ip_event = 0,
   .lost_ip_event = 0,
   .if_key = "WIFI_AP_DEF",
   .if_desc = "ap",
   .route_prio = 10
};

wifi_config_t wifi_ap_config = {
    .ap = {
        .channel = AP_ESP_WIFI_CHANNEL,
        .password = AP_ESP_WIFI_PASS,
        .max_connection = AP_MAX_STA_CONN,
        .authmode = WIFI_AUTH_WPA2_PSK,
    },
};

wifi_config_t wifi_sta_config = {
    .sta = {
        // Array Initialisierung mit Nullen, Zuweisung erfolgt nach Eingabe auf Web-Seite oder Einlesen aus Datei
        // .ssid = EXAMPLE_ESP_WIFI_STA_SSID,
        // .password = EXAMPLE_ESP_WIFI_STA_PASSWD,
        .scan_method = WIFI_ALL_CHANNEL_SCAN,
        .failure_retry_cnt = EXAMPLE_ESP_MAXIMUM_RETRY,
        /* Authmode threshold resets to WPA2 as default if password matches WPA2 standards (pasword len => 8).
            * If you want to connect the device to deprecated WEP/WPA networks, Please set the threshold value
            * to WIFI_AUTH_WEP/WIFI_AUTH_WPA_PSK and set the password with length and format matching to
        * WIFI_AUTH_WEP/WIFI_AUTH_WPA_PSK standards.
            */
        .threshold.authmode = ESP_WIFI_SCAN_AUTH_MODE_THRESHOLD,
        .sae_pwe_h2e = WPA3_SAE_PWE_BOTH,
    },
};

static int s_retry_num = 0;
static const char* TAG = "WIFI";
static const char *errFileWrite = "Error on file writing";
static const char *failCloseFile = "Failed to close file";
static const char *failOpenFileForWrite = "Failed to open file for writing";
static const char *errFileRead = "Error on file reading";
static const char *errFileDelete = "Error on file deleting";
static const char *okFileDelete = "File deleted";
static bool writeToConfigFileFlag;

esp_aes_context aesContext;
const unsigned char aesInitVector[] = { 0x1e, 0x2c, 0x82, 0xd0, 0x22, 0x4c, 0x2e, 0x8f, 0x60, 0x72, 0xcc, 0xf4, 0x5b, 0xc2, 0xa1, 0xf8 };

/* FreeRTOS event group to signal when we are connected/disconnected */
static EventGroupHandle_t s_wifi_event_group;
static wifi_scan_config_t wifiScanConfig;
WIFI_STATE_TYPE wifiState;
char macString[18];
QueueHandle_t xWifiConfigQueue;
SemaphoreHandle_t xWifiStateMutex;
SemaphoreHandle_t xSsidMutex;
char ssidList[SCAN_LIST_SIZE][MAX_CRED_LEN]; 
const char *wifiConfigFile = "/spiffs/configuration.json";
char buffer[3000];
cJSON* tempObject;

static void scan() {
    uint16_t number = SCAN_LIST_SIZE;
    wifi_ap_record_t ap_info[SCAN_LIST_SIZE];
    uint16_t ap_count = 0;
    memset(ap_info, 0, sizeof(ap_info));

    // esp_wifi_scan_start(NULL, true);
    ESP_LOGI(TAG,"Max AP number ap_info can hold = %u", number);
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_scan_get_ap_records(&number, ap_info));
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_scan_get_ap_num(&ap_count));
    ESP_LOGI(TAG,"Total APs scanned = %u, actual AP number ap_info holds = %u \n", ap_count, number);
    for (int i = 0; i < number; i++) {
        strcpy(ssidList[i], (char*)ap_info[i].ssid);
        ESP_LOGI(TAG,"SSID\t\t%s", ap_info[i].ssid);
        ESP_LOGI(TAG,"RSSI\t\t%d", ap_info[i].rssi);
        ESP_LOGI(TAG,"CHANNEL\t\t%d", ap_info[i].primary);
        printf("\n");
    }
}

static int readLineFromConfigFile( char *buf, char *str ) {
   // Maximalauslegung 63 Nutzzeichen Passwort + '\n' + '\0'
   char *pos;

   pos = strchr( buf, '\n' );
   if( pos != NULL )
   {
      *pos = '\0';
      strcpy( str, buf );
      // puts( str );
      return ( pos - buf );
   }
   else
   {
      ESP_LOGE(TAG, "%s", errFileRead);
      return -1;
   }
}

static void event_handler(void *arg, esp_event_base_t event_base, int32_t event_id, void *event_data) {
    FILE *file;
    int len, padding;
    unsigned char aesBuf[128], iv[16];
    wifiConfigMessage message;
    ledStateMessage ledMessage;

    if (event_id == WIFI_EVENT_AP_START) {
        ESP_LOGI(TAG,"AP started.");
    } else if (event_id == WIFI_EVENT_AP_STACONNECTED) {                      // 4.1 Event wifi station connected
        wifi_event_ap_staconnected_t *event = (wifi_event_ap_staconnected_t*) event_data;
        ESP_LOGI(TAG,"Device "MACSTR" join, AID=%d", MAC2STR(event->mac), event->aid);
    } else if (event_id == WIFI_EVENT_AP_STADISCONNECTED) {              // 5.1 Event wifi station disconnected
        wifi_event_ap_stadisconnected_t *event = (wifi_event_ap_stadisconnected_t*) event_data;
        ESP_LOGI(TAG,"Device "MACSTR" leave, AID=%d", MAC2STR(event->mac), event->aid);
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_STACONNECTED) {
        wifi_event_ap_staconnected_t *event = (wifi_event_ap_staconnected_t *) event_data;
        ESP_LOGI(TAG,"Station "MACSTR" joined, AID=%d", MAC2STR(event->mac), event->aid);
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_STADISCONNECTED) {
        wifi_event_ap_stadisconnected_t *event = (wifi_event_ap_stadisconnected_t *) event_data;
        ESP_LOGI(TAG,"Station "MACSTR" left, AID=%d", MAC2STR(event->mac), event->aid);
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        if( wifiState == STATION_CONNECTING ) {
            ESP_LOGI(TAG,"Station connecting");
            ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_connect());                   // 4.1 Connect WiFi
         } else if( wifiState == STATION_SCANNING ) {
            ESP_LOGI(TAG,"Station scanning");
            ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_scan_start( &wifiScanConfig, false ));
         }
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *networkInfo = (ip_event_got_ip_t *) event_data;
        char temp[20] = {'\0'};

        sprintf(temp, IPSTR, IP2STR(&networkInfo->ip_info.ip));
        cJSON_SetValuestring(cJSON_GetObjectItem(config, "IP"), temp);
        memset(&temp, 0x00, sizeof(temp));

        sprintf(temp, IPSTR, IP2STR(&networkInfo->ip_info.netmask));
        cJSON_SetValuestring(cJSON_GetObjectItem(config, "Netmask"), temp);
        memset(&temp, 0x00, sizeof(temp));

        sprintf(temp, IPSTR, IP2STR(&networkInfo->ip_info.gw));
        cJSON_SetValuestring(cJSON_GetObjectItem(config, "Gateway"), temp);
        memset(&temp, 0x00, sizeof(temp));

        ESP_LOGI(TAG,"Got IP: %s", cJSON_GetObjectItem(config, "IP")->valuestring);
        file_writeContentInFile(wifiConfigFile, config);
        s_retry_num = 0;
        xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
    } else if( event_id == WIFI_EVENT_SCAN_DONE ) {
        ESP_LOGI(TAG,"Scan done");
        scan();
        message.state = START_AP;
        xQueueSend(xWifiConfigQueue, (void*) &message, 100 / portTICK_PERIOD_MS);
    } else if( event_id == WIFI_EVENT_STA_CONNECTED ) {
        wifi_ap_record_t ap_info = {'\0'};
        wifiState = STATION_CONNECTED;
        if( writeToConfigFileFlag == true ) {          // In diesem Fall keine Semaphore notwendig
            writeToConfigFileFlag = false;
            cJSON_SetValuestring(cJSON_GetObjectItem(config, "SSID"), (char*) wifi_sta_config.sta.ssid);
            cJSON_SetValuestring(cJSON_GetObjectItem(config, "Password"), (char*) wifi_sta_config.sta.password);

            esp_wifi_sta_get_ap_info(&ap_info);
            // cJSON_SetValuestring(cJSON_GetObjectItem(config, "Channel"), (char*)ap_info.primary);
            // cJSON_SetNumberValue(cJSON_GetObjectItem(config, "Authenticate Mode"), ap_info.authmode);

            file_writeContentInFile(wifiConfigFile, config);
        }

        ledMessage.mode = NORMAL;
        ledMessage.led = LED_BLUE;
        ledMessage.state = ON;
        xQueueSend(xLedStateQueue, (void *) &ledMessage, 500 / portTICK_PERIOD_MS);
    }
}

static void copyWifiCredentials( wifiConfigMessage *message ) {
   strcpy( (char *)wifi_sta_config.sta.ssid, message->ssid );
   // puts( message->ssid );
   strcpy( (char *)wifi_sta_config.sta.password, message->password );
   // puts( message->password );
   writeToConfigFileFlag = true;
}

void wifi_init_sta_and_softap(void) {
    FILE *file;
   uint8_t mac[6];
   struct stat entry_stat;
   int len, res;
   unsigned char aesBuf[128], iv[16];

   s_wifi_event_group = xEventGroupCreate();

   esp_netif_create_default_wifi_sta();                                   // 1.3 Create / init WiFi  (default WiFi station)

   // esp_netif_create_default_wifi_ap();
   esp_netif_create_wifi( WIFI_IF_AP, &esp_netif_inherent_ap_config );  // 1.3 Create / init WiFi  (default WiFi access point) TR: Modifizierte IP-Adresse
   esp_wifi_set_default_wifi_ap_handlers();                             // Dieser Aufruf zusätzlich notwendig, ist dagegen in esp_netif_create_default_wifi_ap() integriert

   wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
   ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_init(&cfg));

   /*
    * Bei UXGA crop 800 x 800 px trat somit kein Übertragungsfehler mehr auf.
    * Bei UXGA 1600 x 1200 px überwiegend OK, aber nicht vollständig.
    * Der Ansatz ist richtig, dass der Wifi-Task der Störenfried ist.
    */
    // ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_set_ps( WIFI_PS_NONE ));

    esp_event_handler_instance_t instance_any_id;
    esp_event_handler_instance_t instance_got_ip;
    // TR: &-Operator für server notwendig, da Zuweisung ansonsten nach außen nicht sichtbar!
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL, &instance_any_id));
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler, NULL, &instance_got_ip));

    strcpy((char *)wifi_ap_config.ap.ssid, productName );
    wifi_ap_config.ap.ssid_len = strlen( productName );
    if (strlen(AP_ESP_WIFI_PASS) == 0) {
        wifi_ap_config.ap.authmode = WIFI_AUTH_OPEN;
    }
    wifiScanConfig.scan_time = wifiScanTime;              // Die restlichen Elemente der Struktur sind NULL bzw. 0

    if (strlen(cJSON_GetObjectItem(config, "SSID")->valuestring) == 0) {
        wifiState = STATION_SCANNING;
    } else {
        wifiState = STATION_CONNECTING;

        strcpy((char *)wifi_sta_config.sta.ssid, cJSON_GetObjectItem(config, "SSID")->valuestring);
        strcpy((char *)wifi_sta_config.sta.password, cJSON_GetObjectItem(config, "SSID_PW")->valuestring);
    }
    

    // if(( file = fopen( wifiConfigFile, "r" )) == NULL ) {
    //     wifiState = STATION_SCANNING;
    // } else {
    //     wifiState = STATION_CONNECTING;
    //     stat( wifiConfigFile, &entry_stat );
    //     len = entry_stat.st_size;
    //     res = fread( aesBuf, 1, len, file );
    //     if( res != len || len % 16 )
    //         ESP_LOGE(TAG, "%s", errFileRead);
    //     else
    //     {
    //         memcpy( iv, aesInitVector, AES_BLOCKLEN );
    //         esp_aes_crypt_cbc( &aesContext, ESP_AES_DECRYPT, len, iv, aesBuf, aesBuf );
    //         aesBuf[len] = '\0';
    //         res = readLineFromConfigFile( (char *) aesBuf, (char *)wifi_sta_config.sta.ssid );
    //         if( res != -1 )
    //             readLineFromConfigFile( (char *) &aesBuf[res + 1], (char *)wifi_sta_config.sta.password );
    //     }
    //     if( fclose( file ) == EOF )
    //         ESP_LOGE(TAG, "%s", failCloseFile);
    // }

    ESP_LOGI(TAG,"SSID = %s, PW = %s.", (char*)wifi_sta_config.sta.ssid, (char*)wifi_sta_config.sta.password);

    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_set_mode(WIFI_MODE_STA));                          // 2. Configure WiFi: station mode
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_set_config(ESP_IF_WIFI_STA, &wifi_sta_config));
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_get_mac( ESP_IF_WIFI_STA, mac ));
    sprintf( macString, "%02x:%02x:%02x:%02x:%02x:%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5] );
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_start());                          // 3.1 Start WiFi, der Rest läuft event-gesteuert, siehe weiter Funktion event_handler()
    ESP_LOGI(TAG,"wifi_init_sta_and_softap finished.");

    /* Waiting until either the connection is established (WIFI_CONNECTED_BIT) or connection failed for the maximum
        * number of re-tries (WIFI_FAIL_BIT). The bits are set by event_handler() (see above) */
    EventBits_t bits = xEventGroupWaitBits(s_wifi_event_group, WIFI_CONNECTED_BIT | WIFI_FAIL_BIT, pdFALSE, pdFALSE, portMAX_DELAY);

    /* xEventGroupWaitBits() returns the bits before the call returned, hence we can test which event actually
        * happened. */
    if (bits & WIFI_CONNECTED_BIT){
        ESP_LOGI(TAG,"connected to ap SSID:%s", wifi_sta_config.sta.ssid);
    } else if (bits & WIFI_FAIL_BIT) {
        ESP_LOGI(TAG,"Failed to connect to SSID:%s", wifi_sta_config.sta.ssid);
    } else {
        ESP_LOGI(TAG,"UNEXPECTED EVENT");
    }

   /* TR: Die unregister-Funktionen waren aus dem ursprünglichen Beispiel noch drin.
    * Dann funktioniert aber kein disconnect-handling.
    * Ich lasse sie nur zu Demostrationszwecken noch stehen.
    *
    * The event will not be processed after unregister
    * ESP_ERROR_CHECK(esp_event_handler_instance_unregister(IP_EVENT, IP_EVENT_STA_GOT_IP, instance_got_ip));
    * ESP_ERROR_CHECK(esp_event_handler_instance_unregister(WIFI_EVENT, ESP_EVENT_ANY_ID, instance_any_id));
    * vEventGroupDelete(s_wifi_event_group);
    */
}

void wifiControlTask( void *pvParameters ) {
    wifiConfigMessage message;
    xWifiConfigQueue = xQueueCreate( 10, sizeof( wifiConfigMessage ) );
    xWifiStateMutex = xSemaphoreCreateMutex();
    xSsidMutex = xSemaphoreCreateMutex();

    while( 1 ) {
        if( xQueueReceive( xWifiConfigQueue, (void *) &message, portMAX_DELAY ) == pdTRUE ){

            if( message.state == START_STATION ) {
                vTaskDelay(1000 / portTICK_PERIOD_MS);       // Ansonsten manchmal Anzeige im Browser "Fehler: Verbindung unterbrochen"

                if( wifiState == ACCESS_POINT ) {
                    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_stop());                // stop soft-AP
                    ESP_LOGI(TAG, "SSID = %s, Passwort = %s", message.ssid, message.password);

                    wifiState = STATION_CONNECTING;        // Ganz wichtig jetzt Zuweisung hier, da Abfrage beim WIFI_EVENT_STA_START
                    copyWifiCredentials( &message );

                    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_set_mode(WIFI_MODE_STA));
                    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_set_config(ESP_IF_WIFI_STA, &wifi_sta_config) );
                    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_start());               // start station
                }
                else if( message.flag == true && ( strcmp( (char *)wifi_sta_config.sta.ssid, message.ssid ) || strcmp( (char *)wifi_sta_config.sta.password, message.password ) ))
                {                                   // station-mode, nur wenn sich Zugangsdaten geändert haben, aber nicht bei Einstellungen wiederherstellen
                    esp_wifi_disconnect();        // weiter im DISCONNECT-event, dann mit anderem WLAN verbinden
                    copyWifiCredentials( &message );
                }
            } else if( message.state == START_AP ) {
                ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_stop());                // stop station
                wifiState = ACCESS_POINT;
                ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_set_mode(WIFI_MODE_AP));
                ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_set_config(ESP_IF_WIFI_AP, &wifi_ap_config));
                ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_start());               // start AP
            }
        } else {
            ESP_LOGI(TAG,"Fehler beim Empfangen der Daten");
        }
    }
    vTaskDelete(NULL);
}

int getWifiState() {
    WIFI_STATE_TYPE tempWifiState = ACCESS_POINT;

    if (xSemaphoreTake(xWifiStateMutex, ( TickType_t ) 0 ) == pdTRUE) {
        tempWifiState = wifiState;

        xSemaphoreGive(xWifiStateMutex);
    }
    

    return tempWifiState;
}

char* getSSID() {
    if (xSemaphoreTake(xSsidMutex, ( TickType_t ) 0 ) == pdTRUE) {
        ESP_LOGI(TAG, "getSSID -> Send SSID: %s", (char *)wifi_sta_config.sta.ssid);
        xSemaphoreGive(xSsidMutex);
    }

    return (char *)wifi_sta_config.sta.ssid;
}