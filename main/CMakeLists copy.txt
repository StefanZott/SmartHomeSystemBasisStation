idf_component_register(SRCS "FileManagment.c" "cJSON.c" "TaskControl.c" "LED.c" "main.c" "WLAN.c" "WebServer.c" "cJSON.c"
                    INCLUDE_DIRS "."
                    EMBED_FILES "../spiffs/html/index.html" "../spiffs/img/favicon.ico" "../spiffs/img/tgeSymbol.svg" "../spiffs/img/logOut.svg" "../spiffs/js/bootstrap.js.map" "../spiffs/js/common.js" "../spiffs/img/Logo.png"
                    "../spiffs/html/info.html" "../spiffs/html/led.html" "../spiffs/css/bootstrap.css.map" "../spiffs/css/bootstrap.css" "../spiffs/js/bootstrap.js" "../spiffs/css/service.css" "../spiffs/html/wlan.html")
