/*
 * FILEMANAGMENT.h
 *
 *  Created on: 22.09.2022
 *      Author: Stefan Zott
 */

#ifndef FILEMANAGMENT_H_
#define FILEMANAGMENT_H_

#include <string.h>
#include <stdbool.h>
#include "cJSON.h"

bool file_isExisting(char* path);
char* file_getContent(char* path);
void file_writeContentInFile(char* path, cJSON* tcfg);

#endif /* FILEMANAGMENT_H_ */