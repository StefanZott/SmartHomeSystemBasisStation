#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include <freertos/task.h>

#include "ProjectConfig.h"

TaskHandle_t currentTask;
TaskStatus_t *pxTaskStatusArray;
volatile UBaseType_t uxArraySize, x;
unsigned long ulTotalRunTime;
char taskName[25];


void executeTaskCotrol( void *pvParameters ) {

    while (1) {
        uxArraySize = uxTaskGetNumberOfTasks(); // Die aktuelle Anzahl von Task 

        pxTaskStatusArray = pvPortMalloc( uxArraySize * sizeof( TaskStatus_t ) ); // Für die ganen Tasks im Heap ein Speicherbereich festlegen

        if( pxTaskStatusArray != NULL )
        {
            /* Generate raw status information about each task. */
            uxArraySize = uxTaskGetSystemState( pxTaskStatusArray, uxArraySize, &ulTotalRunTime );

            /* For each populated position in the pxTaskStatusArray array,
            format the raw data as human readable ASCII data. */
#if TaskListOutput
            printf("****************************************************\n");
            printf("%-7s%-20s%-10s%-5s%-10s%-5s\n", "Task", "Name", "State", "Prio", "Stack", "Core"); 
            printf("****************************************************\n");
            for( x = 1; x < (uxArraySize + 1); x++ ) {
                sprintf( taskName, "%s",pxTaskStatusArray[ x - 1 ].pcTaskName);

                currentTask = xTaskGetHandle(taskName);

                printf("  %-5d", pxTaskStatusArray[ x - 1 ].xTaskNumber);
                printf("%-20s", taskName);
                
                eTaskState taskState = eTaskGetState(currentTask);
                switch (taskState) {
                    case eRunning:
                        printf("%-10s", "RUNNING");
                        break;
                    case eReady:
                        printf("%-10s", "READY");
                        break;
                    case eBlocked:
                        printf("%-10s", "BLOCKED");
                        break;
                    case eSuspended:
                        printf("%-10s", "SUSPENDED");
                        break;
                    case eDeleted:
                        printf("%-10s", "DELETED");
                        break;
                    case eInvalid:
                        printf("%-10s", "INVALID");
                        break;
                    default:
                        printf("%-10s", "UNKOWN");
                        break;
                }

                printf("%-5d", uxTaskPriorityGet(currentTask));
                printf("%-10d", uxTaskGetStackHighWaterMark(currentTask));
                printf("%-5d\n", pxTaskStatusArray[ x - 1 ].xCoreID);
                
                memset(&taskName, 0x00, sizeof(taskName)); // Um sicher zu gehen, dass in dem Speicherbereich keine Bytes übrig sind vom letzten speichern.
            }
            printf("\n");

#endif // TaskListOutput

            /* The array is no longer needed, free the memory it consumes. */
            vPortFree( pxTaskStatusArray );
        }
        vTaskDelay(1500 / portTICK_PERIOD_MS);
    }
}