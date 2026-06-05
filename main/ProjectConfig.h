/**
 *
 * ProjectConfig.h
 *
 * Created on: 31.12.2023
 * Author: Stefan Zott
 *
 * Description:
 * Project-wide configuration switches and compile-time options.
 */

#ifndef PROJECTCONFIG_H_
#define PROJECTCONFIG_H_

// --------------------------------PROJECT---------------------------------


// ---------------------------------OUTPUT---------------------------------
// TaskControl — set to 1 to print FreeRTOS task list (requires CONFIG_FREERTOS_USE_TRACE_FACILITY in sdkconfig)
#define TaskListOutput  0

#endif // PROJECTCONFIG_H_
