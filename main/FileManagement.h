/*
 * FileManagement.h
 *
 *  Created on: 22.09.2022
 *      Author: Stefan Zott
 */

#ifndef FILEMANAGEMENT_H_
#define FILEMANAGEMENT_H_

#include <string.h>
#include <stdbool.h>
#include "cJSON.h"

bool file_isExisting(char* path);
char* file_getContent(char* path);
void file_writeContentInFile(char* path, cJSON* tcfg);

#endif /* FILEMANAGEMENT_H_ */