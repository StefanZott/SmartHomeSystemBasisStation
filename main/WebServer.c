#include <stdio.h>
#include <string.h>
#include "esp_vfs.h"
#include <sys/param.h>
#include <esp_app_desc.h>
#include "esp_ota_ops.h"
#include <esp_log.h>
#include "esp_wifi.h"
#include "lwip/inet.h"
#include "esp_netif.h"

#include "main.h"
#include "WebServer.h"
#include "WLAN.h"
#include "LED.h"
#include "cJSON.h"

/* Max length a file path can have on storage */
#define FILE_PATH_MAX (ESP_VFS_PATH_MAX + CONFIG_SPIFFS_OBJ_NAME_LEN)
#define IS_FILE_EXT(filename, ext) \
    (strcasecmp(&filename[strlen(filename) - sizeof(ext) + 1], ext) == 0)

/* Max size of an individual file. Make sure this
 * value is same as that set in upload_script.html */
#define MAX_FILE_SIZE   (200*1024) // 200 KB
#define MAX_FILE_SIZE_STR "200KB"

/* Scratch buffer size */
#define SCRATCH_BUFSIZE  8192

struct file_server_data {
    /* Base path of file storage */
    char base_path[ESP_VFS_PATH_MAX + 1];

    /* Scratch buffer for temporary storage during file transfer */
    char scratch[SCRATCH_BUFSIZE];
};

static esp_app_desc_t *app_desc;
static char responseStr[500];
static httpd_handle_t server = NULL;
static const char* TAG = "Webserver";
static cJSON* tempObject;

const char *getPathFromUri(char *dest, const char *base_path, const char *uri, size_t destsize) {

    /*
    char* new_uri = malloc(strlen(uri) + 1);
    strcpy(new_uri, uri);
    */

    const size_t base_pathlen = strlen(base_path);
    size_t pathlen = strlen(uri);

    const char *quest = strchr(uri, '?');
    if (quest) {
        pathlen = MIN(pathlen, quest - uri);
    }

    const char *hash = strchr(uri, '#');
    if (hash) {
        pathlen = MIN(pathlen, hash - uri);
    }

    if (base_pathlen + pathlen + 1 > destsize) {
        /* Full path string won't fit into destination buffer */
        return NULL;
    }

    /* Construct full path (base + path) */
    strcpy(dest, base_path);
    strlcpy(dest + base_pathlen, uri, pathlen + 1);
    /* Return pointer to path, skipping the base */
    return dest + base_pathlen;
}

esp_err_t setContentTypeFromFile(httpd_req_t *req, const char *filename) {
    if (IS_FILE_EXT(filename, ".pdf")) {
        return httpd_resp_set_type(req, HTTP_CONTENT_TYPE_PDF);
    } else if (IS_FILE_EXT(filename, ".html")) {
        return httpd_resp_set_type(req, HTTP_CONTENT_TYPE_HTML);
    } else if (IS_FILE_EXT(filename, ".jpeg")) {
        return httpd_resp_set_type(req, HTTP_CONTENT_TYPE_JPG);
    } else if (IS_FILE_EXT(filename, ".jpg")) {
        return httpd_resp_set_type(req, HTTP_CONTENT_TYPE_JPG);
    }else if (IS_FILE_EXT(filename, ".ico")) {
        return httpd_resp_set_type(req, HTTP_CONTENT_TYPE_ICO);
    } else if (IS_FILE_EXT(filename, ".svg")) {
        return httpd_resp_set_type(req, HTTP_CONTENT_TYPE_SVG);
    } else if (IS_FILE_EXT(filename, ".css")) {
        return httpd_resp_set_type(req, HTTP_CONTENT_TYPE_CSS);
    } else if (IS_FILE_EXT(filename, ".js")) {
        return httpd_resp_set_type(req, HTTP_CONTENT_TYPE_JS);
    } else if (IS_FILE_EXT(filename, ".json")) {
        return httpd_resp_set_type(req, HTTP_CONTENT_TYPE_JSON);
    } else if (IS_FILE_EXT(filename, ".png")) {
        return httpd_resp_set_type(req, HTTP_CONTENT_TYPE_PNG);
    }
    /* This is a limited set only */
    /* For any other type always set as plain text */
    return httpd_resp_set_type(req, "text/plain");
}

static esp_err_t fwVersionHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    strcpy(responseStr, "v");
    strcat(responseStr, app_desc->version);
    httpd_resp_send(req, (const char *)responseStr, strlen(responseStr));

    memset(&responseStr, 0x00, sizeof(responseStr));

    return ESP_OK;
}

static esp_err_t zottItLogoHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);
    extern const unsigned char logo_png_start[] asm("_binary_Logo_png_start");
    extern const unsigned char logo_png_end[] asm("_binary_Logo_png_end");
    const size_t logo_png_size = (logo_png_end - logo_png_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_ICO);
    httpd_resp_send(req, (const char *)logo_png_start, logo_png_size);
    return ESP_OK;
}

static esp_err_t getHandler(httpd_req_t *req) {
    char filepath[FILE_PATH_MAX];
	size_t req_hdr_host_len = httpd_req_get_hdr_value_len(req, "Host");
  	char req_hdr_host_val[req_hdr_host_len + 1];
	struct stat file_stat;

	esp_err_t res = httpd_req_get_hdr_value_str(req, "Host", (char *)&req_hdr_host_val, sizeof(char) * req_hdr_host_len + 1);
	if (res != ESP_OK) {
		printf("EVENT: WebServer -> failed getting HOST header value: %d\n", res);

		switch (res) {
			case ESP_ERR_NOT_FOUND:
			printf("EVENT: WebServer -> failed getting HOST header value: ESP_ERR_NOT_FOUND: Key not found: %d\n", res);
			break;

			case ESP_ERR_INVALID_ARG:
			printf("EVENT: WebServer -> failed getting HOST header value: ESP_ERR_INVALID_ARG: Null arguments: %d\n", res);
			break;

			case ESP_ERR_HTTPD_INVALID_REQ:
			printf("EVENT: WebServer -> failed getting HOST header value: ESP_ERR_HTTPD_INVALID_REQ: Invalid HTTP request pointer: %d\n", res);
			break;

			case ESP_ERR_HTTPD_RESULT_TRUNC:
			printf("EVENT: WebServer -> failed getting HOST header value: ESP_ERR_HTTPD_RESULT_TRUNC: Value string truncated: %d\n", res);
			break;

			default:
			break;
		}
	} else {
		// ESP_LOGI(TAG_WEB, "URI: %s", req->uri);
	}
	
    const char *filename = getPathFromUri(filepath, ((struct file_server_data *)req->user_ctx)->base_path, req->uri, sizeof(filepath));

    if (!filename) {
        printf("EVENT: WebServer -> Filename is too long\n");
        httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Filename too long");
        return ESP_FAIL;
    }

    if (stat(filepath, &file_stat) == -1) {
        if(strcmp(filename, "/") == 0) {
            printf("index\n");
            extern const unsigned char index_html_start[] asm("_binary_index_html_start");
            extern const unsigned char index_html_end[] asm("_binary_index_html_end");
            const size_t index_html_size = (index_html_end - index_html_start);
            httpd_resp_set_type(req, HTTP_CONTENT_TYPE_HTML);
            httpd_resp_send(req, (const char *)index_html_start, index_html_size);
            return ESP_OK;
        } else {
            printf("URI: %s not found\n", filename);
            httpd_resp_send_404(req);
            return ESP_FAIL;
        }
    }

    return ESP_OK;
}

static esp_err_t faviconIcoHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    extern const unsigned char favicon_html_start[] asm("_binary_favicon_ico_start");
    extern const unsigned char favicon_html_end[] asm("_binary_favicon_ico_end");
    const size_t favicon_html_size = (favicon_html_end - favicon_html_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_ICO);
    httpd_resp_send(req, (const char *)favicon_html_start, favicon_html_size);
    return ESP_OK;
}

static esp_err_t tgeSymbolSvgHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    extern const unsigned char tge_symbol_svg_start[] asm("_binary_tgeSymbol_svg_start");
    extern const unsigned char tge_symbol_svg_end[] asm("_binary_tgeSymbol_svg_end");
    const size_t tge_symbol_svg_size = (tge_symbol_svg_end - tge_symbol_svg_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_SVG);
    httpd_resp_send(req, (const char *)tge_symbol_svg_start, tge_symbol_svg_size);
    return ESP_OK;
}

static esp_err_t logOutSvgHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    extern const unsigned char log_out_svg_start[] asm("_binary_logOut_svg_start");
    extern const unsigned char log_out_svg_end[] asm("_binary_logOut_svg_end");
    const size_t log_out_svg_size = (log_out_svg_end - log_out_svg_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_SVG);
    httpd_resp_send(req, (const char *)log_out_svg_start, log_out_svg_size);
    return ESP_OK;
}

static esp_err_t bootstrapJsMapHandler(httpd_req_t *req) {
    extern const unsigned char bootstrap_js_map_start[] asm("_binary_bootstrap_js_map_start");
    extern const unsigned char bootstrap_js_map_end[] asm("_binary_bootstrap_js_map_end");
    const size_t bootstrap_js_map_size = (bootstrap_js_map_end - bootstrap_js_map_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_JS);
    httpd_resp_send(req, (const char *)bootstrap_js_map_start, bootstrap_js_map_size);
    return ESP_OK;
}

static esp_err_t bootstrapJsHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    extern const unsigned char bootstrap_js_start[] asm("_binary_bootstrap_js_start");
    extern const unsigned char bootstrap_js_end[] asm("_binary_bootstrap_js_end");
    const size_t bootstrap_js_size = (bootstrap_js_end - bootstrap_js_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_JS);
    httpd_resp_send(req, (const char *)bootstrap_js_start, bootstrap_js_size);
    return ESP_OK;
}

static esp_err_t bootstrapCssMapHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    extern const unsigned char bootstrap_css_map_start[] asm("_binary_bootstrap_css_map_start");
    extern const unsigned char bootstrap_css_map_end[] asm("_binary_bootstrap_css_map_end");
    const size_t bootstrap_css_map_size = (bootstrap_css_map_end - bootstrap_css_map_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_CSS);
    httpd_resp_send(req, (const char *)bootstrap_css_map_start, bootstrap_css_map_size);
    return ESP_OK;
}

static esp_err_t bootstrapCssHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    extern const unsigned char bootstrap_css_start[] asm("_binary_bootstrap_css_start");
    extern const unsigned char bootstrap_css_end[] asm("_binary_bootstrap_css_end");
    const size_t bootstrap_css_size = (bootstrap_css_end - bootstrap_css_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_CSS);
    httpd_resp_send(req, (const char *)bootstrap_css_start, bootstrap_css_size);
    return ESP_OK;
}

static esp_err_t commonJsHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    extern const unsigned char common_js_start[] asm("_binary_common_js_start");
    extern const unsigned char common_js_end[] asm("_binary_common_js_end");
    const size_t common_js_size = (common_js_end - common_js_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_JS);
    httpd_resp_send(req, (const char *)common_js_start, common_js_size);
    return ESP_OK;
}

static esp_err_t ssidListHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    memset(&responseStr,0x00,sizeof(responseStr));
    for (size_t i = 0; i < SCAN_LIST_SIZE; i++) {
        if (i == 0) {
            strcpy(responseStr,ssidList[i]);
            strcat(responseStr, ",");
        } else if(i == (SCAN_LIST_SIZE - 1)){
            strcat(responseStr,ssidList[i]);
        }else {
            strcat(responseStr,ssidList[i]);
            strcat(responseStr, ",");
        }
    }

    httpd_resp_send(req,responseStr,strlen(responseStr));
    
    return ESP_OK;
}

static esp_err_t newSsidHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    wifiConfigMessage message;
    char buf[100] = {0x00};
    int ret, remaining = req->content_len;
    bool nextAttribute = false;
    char delimiter[] = ",";
    char *ptr;

    httpd_req_recv( req, buf, sizeof(buf) - 1);
    ptr = strtok(buf, delimiter);

    while(ptr != NULL) {
        if (!nextAttribute) {
            nextAttribute = true;
            strcpy(message.ssid, ptr);
        } else {
            strcpy(message.password, ptr);
        }
        
        ptr = strtok(NULL, delimiter);
    }
    
    httpd_resp_send_chunk(req, NULL, 0);

    message.state = START_STATION;

    if (xQueueSend(xWifiConfigQueue, (void *) &message, 500 / portTICK_PERIOD_MS) == pdTRUE) {
        printf("EVENT: WebServer -> Erfolgreich gesendet an die Queue\n");
    } else {
        printf("EVENT: WebServer -> Fehler beim senden an die Queue\n");
    }

    return ESP_OK;
}

static esp_err_t ledHtmlHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    extern const unsigned char led_html_start[] asm("_binary_led_html_start");
    extern const unsigned char led_html_end[] asm("_binary_led_html_end");
    const size_t led_html_size = (led_html_end - led_html_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_SVG);
    httpd_resp_send(req, (const char *)led_html_start, led_html_size);
    return ESP_OK;
}

static esp_err_t infoHtmlHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    extern const unsigned char info_html_start[] asm("_binary_info_html_start");
    extern const unsigned char info_html_end[] asm("_binary_info_html_end");
    const size_t info_html_size = (info_html_end - info_html_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_SVG);
    httpd_resp_send(req, (const char *)info_html_start, info_html_size);
    return ESP_OK;
}

static esp_err_t ledTestHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    ledStateMessage message;

    message.mode = TEST;
    xQueueSend(xLedStateQueue, (void *) &message, 500 / portTICK_PERIOD_MS);

    httpd_resp_send_chunk(req, NULL, 0);
    return ESP_OK;
}

static esp_err_t serviceCssHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    extern const unsigned char service_css_start[] asm("_binary_service_css_start");
    extern const unsigned char service_css_end[] asm("_binary_service_css_end");
    const size_t service_css_size = (service_css_end - service_css_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_CSS);
    httpd_resp_send(req, (const char *)service_css_start, service_css_size);
    return ESP_OK;
}

static esp_err_t wlanHtmlHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    extern const unsigned char wlan_html_start[] asm("_binary_wlan_html_start");
    extern const unsigned char wlan_html_end[] asm("_binary_wlan_html_end");
    const size_t wlan_html_size = (wlan_html_end - wlan_html_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_SVG);
    httpd_resp_send(req, (const char *)wlan_html_start, wlan_html_size);
    return ESP_OK;
}

static esp_err_t ledSingleTestHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    ledStateMessage message = {'\0'};
    char buf[100] = {0x00};
    int count = 0;
    char delimiter[] = ",";
    char *ptr;

    httpd_req_recv( req, buf, sizeof(buf) - 1);
    ptr = strtok(buf, delimiter);

    while(ptr != NULL) {
        if(count == 0) {
            message.led = atoi(ptr);
        } else if (count == 1) {
            message.state = atoi(ptr);
        } else if(count == 2) {
            message.mode = atoi(ptr);
        }
        
        count++;
        ptr = strtok(NULL, delimiter);
    }
    
    httpd_resp_send_chunk(req, NULL, 0);

    if (xQueueSend(xLedStateQueue, (void *) &message, 500 / portTICK_PERIOD_MS) == pdTRUE) {
        printf("EVENT: WebServer -> Erfolgreich gesendet an die Queue\n");
    } else {
        printf("EVENT: WebServer -> Fehler beim senden an die Queue\n");
    }

    return ESP_OK;
}

static esp_err_t getInfosHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    cJSON* tempResponse = cJSON_CreateObject();
    cJSON_AddStringToObject(tempResponse, "Projekt-Name", app_desc->project_name);
    cJSON_AddStringToObject(tempResponse, "Projekt-Version", app_desc->version);
    cJSON_AddStringToObject(tempResponse, "IDF-Version", app_desc->idf_ver);
    cJSON_AddStringToObject(tempResponse, "Kompilierzeit", app_desc->time);
    cJSON_AddStringToObject(tempResponse, "Kompilierdatum", app_desc->date);
    
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_JSON);
    httpd_resp_send(req, cJSON_Print(tempResponse), strlen(cJSON_Print(tempResponse)));

    cJSON_Delete(tempResponse);

    return ESP_OK;
}

static esp_err_t disconnectWIFIHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    wifiConfigMessage message;

    message.state = START_AP;

    if (xQueueSend(xWifiConfigQueue, (void *) &message, 500 / portTICK_PERIOD_MS) == pdTRUE) {
        printf("EVENT: WebServer -> Erfolgreich gesendet an die Queue\n");
    } else {
        printf("EVENT: WebServer -> Fehler beim senden an die Queue\n");
    }
    
    httpd_resp_send(req, "disconnected", strlen("disconnected"));

    return ESP_OK;
}

static esp_err_t getWifiStateHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    itoa(getWifiState(), responseStr, 10);
    
    httpd_resp_send(req,  responseStr, strlen(responseStr));

    return ESP_OK;
}

static esp_err_t getConnectionInfoHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);
    tempObject = cJSON_CreateObject();

    for (size_t i = 0; i < SCAN_LIST_SIZE; i++) {
        if (strlen(cJSON_GetObjectItem(config, "SSID")->valuestring) == 0) {
            ESP_LOGI(TAG, "Keine SSID vorhanden!");
            cJSON_AddStringToObject(tempObject, "SSID", "Unbekannt");
            cJSON_AddStringToObject(tempObject, "Channel", "Unbekannt");
            cJSON_AddStringToObject(tempObject, "RSSI", "Unbekannt");
            cJSON_AddStringToObject(tempObject, "Authenticate Mode", "Unbekannt");
        } else {
            cJSON_AddStringToObject(tempObject, "SSID", cJSON_GetObjectItem(config, "SSID")->valuestring);

            if (strlen(cJSON_GetObjectItem(config, "Channel")->valuestring) == 0) {
                cJSON_AddStringToObject(tempObject, "Channel", "Unbekannt");
            } else {
                cJSON_AddStringToObject(tempObject, "Channel", cJSON_GetObjectItem(config, "Channel")->valuestring);
            }

            if (strlen(cJSON_GetObjectItem(config, "RSSI")->valuestring) == 0) {
                cJSON_AddStringToObject(tempObject, "RSSI", "Unbekannt");
            } else {
                cJSON_AddStringToObject(tempObject, "RSSI", cJSON_GetObjectItem(config, "RSSI")->valuestring);
            }

            // Information about coonection
            cJSON_AddStringToObject(tempObject, "IP", cJSON_GetObjectItem(config, "IP")->valuestring);
            cJSON_AddStringToObject(tempObject, "Netmask", cJSON_GetObjectItem(config, "Netmask")->valuestring);
            cJSON_AddStringToObject(tempObject, "Gateway", cJSON_GetObjectItem(config, "Gateway")->valuestring);

            // TODO: MAC-Adresse wäre noch schön
            break;
        }
    }
    
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_JSON);
    httpd_resp_send(req, cJSON_Print(tempObject), strlen(cJSON_Print(tempObject)));

    cJSON_Delete(tempObject);

    return ESP_OK;
}

static esp_err_t alexaTestHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    httpd_resp_send(req, "Hello World", strlen("Hello World"));

    return ESP_OK;
}

static esp_err_t deviceHtmlHandler(httpd_req_t *req) {
    ESP_LOGI(TAG, "Load %s", req->uri);

    extern const unsigned char device_html_start[] asm("_binary_device_html_start");
    extern const unsigned char device_html_end[] asm("_binary_device_html_end");
    const size_t device_html_size = (device_html_end - device_html_start);
    httpd_resp_set_type(req, HTTP_CONTENT_TYPE_HTML);
    httpd_resp_send(req, (const char *)device_html_start, device_html_size);
    return ESP_OK;
}

httpd_handle_t startWebServer(const char *base_path) {
    static struct file_server_data *server_data = NULL;
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.lru_purge_enable = true;
    config.uri_match_fn = httpd_uri_match_wildcard;
    config.max_uri_handlers = 51;

    app_desc = esp_ota_get_app_description();

    if (!base_path || strcmp(base_path, "/spiffs") != 0) {
		printf("EVENT: WebServer -> File server presently supports only '/spiffs' as base path\n");
		return ESP_ERR_INVALID_ARG;
	}

	if (server_data) {
		printf("EVENT: WebServer -> File server already started\n");
		return ESP_ERR_INVALID_STATE;
	}

	server_data = calloc(1, sizeof(struct file_server_data));
	if (!server_data) {
		printf("EVENT: WebServer -> Failed to allocate memory for server data\n");
		return ESP_ERR_NO_MEM;
	}
	strlcpy(server_data->base_path, base_path, sizeof(server_data->base_path));

    // Start the httpd server
    printf("EVENT: WebServer -> Starting server on port: '%d'\n", config.server_port);
    if (httpd_start(&server, &config) == ESP_OK) {
        // Set URI handlers
        printf("EVENT: WebServer -> Registering URI handlers\n");
        httpd_uri_t deviceHandler = {
			.uri       = "/html/device.html",
			.method    = HTTP_GET,
			.handler   = deviceHtmlHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &deviceHandler);
        
        httpd_uri_t alexaTest = {
			.uri       = "/alexaTest",
			.method    = HTTP_GET,
			.handler   = alexaTestHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &alexaTest);

        httpd_uri_t getConnectionInfo = {
			.uri       = "/getConnectionInfo",
			.method    = HTTP_GET,
			.handler   = getConnectionInfoHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &getConnectionInfo);

        httpd_uri_t getWifiState = {
			.uri       = "/getWifiState",
			.method    = HTTP_GET,
			.handler   = getWifiStateHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &getWifiState);

        printf("EVENT: WebServer -> Registering URI handlers\n");
        httpd_uri_t disconnectWIFI = {
			.uri       = "/disconnectWIFIHandler",
			.method    = HTTP_GET,
			.handler   = disconnectWIFIHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &disconnectWIFI);

        httpd_uri_t getInfos = {
			.uri       = "/getInfos",
			.method    = HTTP_GET,
			.handler   = getInfosHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &getInfos);

        printf("EVENT: WebServer -> Registering URI handlers\n");
        httpd_uri_t ledSingleTest = {
			.uri       = "/ledSingleTest",
			.method    = HTTP_POST,
			.handler   = ledSingleTestHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &ledSingleTest);

        printf("EVENT: WebServer -> Registering URI handlers\n");
        httpd_uri_t serviceCss = {
			.uri       = "/css/service.css",
			.method    = HTTP_GET,
			.handler   = serviceCssHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &serviceCss);

        httpd_uri_t bootstrapCssMap = {
			.uri       = "/css/bootstrap.css.map",
			.method    = HTTP_GET,
			.handler   = bootstrapCssMapHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &bootstrapCssMap);

        httpd_uri_t bootstrapCss = {
			.uri       = "/css/bootstrap.css",
			.method    = HTTP_GET,
			.handler   = bootstrapCssHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &bootstrapCss);

        httpd_uri_t ledTest = {
			.uri       = "/ledTest",
			.method    = HTTP_GET,
			.handler   = ledTestHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &ledTest);

        httpd_uri_t wlanHtml = {
			.uri       = "/html/wlan.html",
			.method    = HTTP_GET,
			.handler   = wlanHtmlHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &wlanHtml);

        httpd_uri_t infoHtml = {
			.uri       = "/html/info.html",
			.method    = HTTP_GET,
			.handler   = infoHtmlHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &infoHtml);

        httpd_uri_t ledHtml = {
			.uri       = "/html/led.html",
			.method    = HTTP_GET,
			.handler   = ledHtmlHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &ledHtml);

        httpd_uri_t fwVersion = {
			.uri       = "/FWversion",
			.method    = HTTP_GET,
			.handler   = fwVersionHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &fwVersion);

        httpd_uri_t zottItLogo = {
			.uri       = "/img/Logo.png",
			.method    = HTTP_GET,
			.handler   = zottItLogoHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &zottItLogo);

        httpd_uri_t newSsid = {
			.uri       = "/newSSID",
			.method    = HTTP_POST,
			.handler   = newSsidHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &newSsid);

        httpd_uri_t ssidList = {
			.uri       = "/getSsidList",
			.method    = HTTP_GET,
			.handler   = ssidListHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &ssidList);

        httpd_uri_t commonJs = {
			.uri       = "/js/common.js",
			.method    = HTTP_GET,
			.handler   = commonJsHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &commonJs);

        httpd_uri_t bootstrapJsMap = {
			.uri       = "/js/bootstrap.js.map",
			.method    = HTTP_GET,
			.handler   = bootstrapJsMapHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &bootstrapJsMap);

        httpd_uri_t bootstrapJs = {
			.uri       = "/js/bootstrap.js",
			.method    = HTTP_GET,
			.handler   = bootstrapJsHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &bootstrapJs);

        httpd_uri_t logOutSvg = {
			.uri       = "/img/logOut.svg",
			.method    = HTTP_GET,
			.handler   = logOutSvgHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &logOutSvg);

        httpd_uri_t tgeSymbolSvg = {
			.uri       = "/img/tge-symbol.svg",
			.method    = HTTP_GET,
			.handler   = tgeSymbolSvgHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &tgeSymbolSvg);

        httpd_uri_t faviconIco = {
			.uri       = "/favicon.ico",
			.method    = HTTP_GET,
			.handler   = faviconIcoHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &faviconIco);

        httpd_uri_t reqGet = {
			.uri       = "/*",
			.method    = HTTP_GET,
			.handler   = getHandler,
			.user_ctx  = server_data
		};
		httpd_register_uri_handler(server, &reqGet);
        return server;
    }

    printf("EVENT: WebServer -> Error starting server!\n");
    return NULL;
}