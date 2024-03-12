#include <stdio.h>
#include "nvs_flash.h"
#include "freertos/FreeRTOS.h"
#include "freertos/FreeRTOSConfig.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "esp_event.h"
#include "esp_spiffs.h"

#include "main.h"
#include "TaskControl.h"
#include "LED.h"
#include "WLAN.h"
#include "WebServer.h"
#include "FileManagment.h"

SemaphoreHandle_t xLedMutex;
SemaphoreHandle_t xLedSemaphore;

const char *productName = "DoorLine Skill";
const char *FW_Version = "V0.0.1";
cJSON* config;

static int ret;

static esp_err_t initSpiffs(void) {
    printf("EVENT: Main -> Initializing SPIFFS\n");

    esp_vfs_spiffs_conf_t conf = {
      .base_path = "/spiffs",
      .partition_label = NULL,
      .max_files = 20,   // This decides the maximum number of files that can be created on the storage
      .format_if_mount_failed = true
    };

    ret = esp_vfs_spiffs_register(&conf);

    if (ret != ESP_OK) {
        if (ret == ESP_FAIL) {
             printf("EVENT: Main -> Failed to mount or format filesystem\n");
        } else if (ret == ESP_ERR_NOT_FOUND) {
             printf("EVENT: Main -> Failed to find SPIFFS partition\n");
        } else {
             printf("EVENT: Main -> Failed to initialize SPIFFS (%s)\n", esp_err_to_name(ret));
        }
        return ESP_FAIL;
    }

    size_t total = 0, used = 0;

    ret = esp_spiffs_info(conf.partition_label, &total, &used);

    if (ret != ESP_OK) {
         printf("EVENT: Main -> Failed to get SPIFFS partition information (%s)\n", esp_err_to_name(ret));
        return ESP_FAIL;
    }

     printf("EVENT: Main -> Partition size: total: %d, used: %d\n", total, used);
    return ESP_OK;
}

void app_main(void) {
    //Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK_WITHOUT_ABORT(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK_WITHOUT_ABORT(ret);

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    xLedMutex = xSemaphoreCreateMutex();
    xLedSemaphore = xSemaphoreCreateBinary();

    initSpiffs();
    startWebServer("/spiffs");

    xTaskCreatePinnedToCore( ledControlTask, "ledControlTask", 4096, NULL, 1, NULL, PRO_CPU );
    xTaskCreatePinnedToCore( executeTaskCotrol, "TaskControl", 2048, NULL, 1, NULL, PRO_CPU );
    xTaskCreatePinnedToCore( wifiControlTask, "wifiControlTask", 8192, NULL, 1, NULL, APP_CPU );

    if(file_isExisting(wifiConfigFile)) {
        if(cJSON_IsNull(config)) {
            config = cJSON_Parse(file_getContent(wifiConfigFile));
        } else {
            config = cJSON_CreateObject();
            cJSON_AddStringToObject(config, "SSID", "");
            cJSON_AddStringToObject(config, "Password", "");
            cJSON_AddStringToObject(config, "Channel", "");
            cJSON_AddStringToObject(config, "RSSI", "");
            cJSON_AddStringToObject(config, "Authenticate Mode", "");

            cJSON_AddStringToObject(config, "IP", "");
            cJSON_AddStringToObject(config, "Netmask", "");
            cJSON_AddStringToObject(config, "Gateway", "");
            file_writeContentInFile(wifiConfigFile, config);
        }
    } else {
        config = cJSON_CreateObject();
        cJSON_AddStringToObject(config, "SSID", "");
        cJSON_AddStringToObject(config, "Password", "");
        cJSON_AddStringToObject(config, "Channel", "");
        cJSON_AddStringToObject(config, "RSSI", "");
        cJSON_AddNumberToObject(config, "Authenticate Mode", -1);

        cJSON_AddStringToObject(config, "IP", "");
        cJSON_AddStringToObject(config, "Netmask", "");
        cJSON_AddStringToObject(config, "Gateway", "");
        file_writeContentInFile(wifiConfigFile, config);
    }

    wifi_init_sta_and_softap();
}
