/*
* WebServer.h
*
*  Created on: 30.12.2023
*      Author: Stefan Zott
*/

#ifndef WEBSERVER_H_
#define WEBSERVER_H_

#include "esp_http_server.h"

#define HTTP_200_HDR "200 OK"
#define HTTP_204_HDR "204 No Content"
#define HTTP_302_HDR "302 Temporary Redirect"
#define HTTP_LOCATION_HDR "Location"
#define RESP_REDIRECT "HTTP/1.1 302 Found\r\nLocation: "
#define HTTP_CONTENT_TYPE_HTML "text/html"
#define HTTP_CONTENT_TYPE_JS "text/javascript"
#define HTTP_CONTENT_TYPE_CSS "text/css"
#define HTTP_CONTENT_TYPE_PDF "application/pdf"
#define HTTP_CONTENT_TYPE_JPG "image/jpeg"
#define HTTP_CONTENT_TYPE_ICO "image/x-icon"
#define HTTP_CONTENT_TYPE_SVG "image/svg+xml"
#define HTTP_CONTENT_TYPE_JSON "application/json"
#define HTTP_CONTENT_TYPE_PNG "image/png"

httpd_handle_t startWebServer(const char *base_path);

#endif // WEBSERVER_H_