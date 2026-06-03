/*
 * PrkHandler.c
 *
 *  Created on:         23.08.2023
 *      Author:         zott
 *
 *      Project:        S2207
 *
 *      Description:
 *          -
 */
/***************************includes **********************************/
#include "FileManagment.h"

#include <stdio.h>
#include <esp_log.h>

/**************************** private Variable ********************************/
static FILE *file;
static const char* TAG = "FileManagment";
char fileBuffer[25000];

/**************************** public Functions ********************************/
bool file_isExisting(char* path) {
    file = fopen(path, "r");
    if (file == NULL) {
        ESP_LOGE(TAG,"File is not existing. Create a new File!");
        fopen(path, "w+"); // Die Datei wird unter /build/app/ angelegt
        fclose(file);
        return false;
    }

    rewind(file);

    if(fgetc(file) == EOF) {
        ESP_LOGE(TAG,"File is empty!\n");
        fclose(file);
        return false;
    }

    ESP_LOGI(TAG,"File has been created!\n");
    fclose(file);
    return true;
}

char* file_getContent(char* path) {
    memset(&fileBuffer, 0x00, sizeof(fileBuffer));

    // Loading and reading from the file
    file = fopen(path, "r");
    if (file == NULL) {
        ESP_LOGE(TAG,"Can not opening the file for reading.\n");
        return "";
    }

    fread(fileBuffer, 1, sizeof(fileBuffer), file);

    fclose(file);

    return fileBuffer;
}

void file_writeContentInFile(char* path, cJSON* tcfg) {
    // Loading and reading from the file
    file = fopen(path, "w");
    if (file == NULL) {
        ESP_LOGE(TAG,"Can not opening the file for reading.\n");
    }

    memset(&fileBuffer, 0x00, sizeof(fileBuffer));
    strcpy(fileBuffer, cJSON_Print(tcfg));

    ESP_LOGI(TAG,"Content save in file: \n %s", fileBuffer);

    fprintf(file, fileBuffer);

    fclose(file);
}
