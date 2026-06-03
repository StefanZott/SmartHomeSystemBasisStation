/*
*   TaskControl.h
*
*   Created on: 27.12.2023
*   Author: Stefan Zott
*   
*   Description:
*   Task used to print the state of the other FreeRTOS tasks.*
*   Notes:
*   - Enable TaskListOutput in ProjectConfig.h for periodic task dumps.*/

#ifndef TASKCONTROL_H_
#define TASKCONTROL_H_

void executeTaskControl( void *pvParameters );

#endif /* TASKCONTROL_H_ */