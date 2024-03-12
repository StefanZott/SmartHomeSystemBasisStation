#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/FreeRTOSConfig.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

#include "esp_log.h"

#include"LED.h"
#include "main.h"
#include "WLAN.h"

static const char* TAG = "LED";
static int count;

QueueHandle_t xLedStateQueue;
ledStateMessage message;
ledStateMessage tempMessage;

ledProfil redLedProfil;
ledProfil greenLedProfil;
ledProfil yellowLedProfil;
ledProfil blueLedProfil;

ledProfil tempRedLedProfil;
ledProfil tempGreenLedProfil;
ledProfil tempYellowLedProfil;
ledProfil tempblueLedProfil;

static void ledInit(void) {
    // Prepare and then apply the LEDC PWM timer configuration
    ledc_timer_config_t ledRedTimer = {
        .speed_mode       = LEDC_MODE,
        .duty_resolution  = LEDC_DUTY_RES,
        .timer_num        = LEDC_TIMER,
        .freq_hz          = LEDC_FREQUENCY,  // Set output frequency at 4 kHz
        .clk_cfg          = LEDC_AUTO_CLK
    };
    ESP_ERROR_CHECK(ledc_timer_config(&ledRedTimer));

    // Prepare and then apply the LEDC PWM channel configuration
    ledc_channel_config_t ledRedChannel = {
        .speed_mode     = LEDC_MODE,
        .channel        = LED_RED,
        .timer_sel      = LEDC_TIMER,
        .intr_type      = LEDC_INTR_DISABLE,
        .gpio_num       = LED_GPIO_RED,
        .duty           = 0, // Set duty to 0%
        .hpoint         = 0
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ledRedChannel));
    redLedProfil.state = OFF;
    redLedProfil.mode = NORMAL;
    tempRedLedProfil.state = OFF;
    tempRedLedProfil.mode = NORMAL;


    // Prepare and then apply the LEDC PWM timer configuration
    ledc_timer_config_t ledGreenTimer = {
        .speed_mode       = LEDC_MODE,
        .duty_resolution  = LEDC_DUTY_RES,
        .timer_num        = LEDC_TIMER,
        .freq_hz          = LEDC_FREQUENCY,  // Set output frequency at 4 kHz
        .clk_cfg          = LEDC_AUTO_CLK
    };
    ESP_ERROR_CHECK(ledc_timer_config(&ledGreenTimer));

    // Prepare and then apply the LEDC PWM channel configuration
    ledc_channel_config_t ledGreenChannel = {
        .speed_mode     = LEDC_MODE,
        .channel        = LED_GREEN,
        .timer_sel      = LEDC_TIMER,
        .intr_type      = LEDC_INTR_DISABLE,
        .gpio_num       = LED_GPIO_GREEN,
        .duty           = 0, // Set duty to 0%
        .hpoint         = 0
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ledGreenChannel));
    greenLedProfil.state = OFF;
    greenLedProfil.mode = NORMAL;
    tempGreenLedProfil.state = OFF;
    tempGreenLedProfil.mode = NORMAL;


    // Prepare and then apply the LEDC PWM timer configuration
    ledc_timer_config_t ledYellowTimer = {
        .speed_mode       = LEDC_MODE,
        .duty_resolution  = LEDC_DUTY_RES,
        .timer_num        = LEDC_TIMER,
        .freq_hz          = LEDC_FREQUENCY,  // Set output frequency at 4 kHz
        .clk_cfg          = LEDC_AUTO_CLK
    };
    ESP_ERROR_CHECK(ledc_timer_config(&ledYellowTimer));

    // Prepare and then apply the LEDC PWM channel configuration
    ledc_channel_config_t ledYellowChannel = {
        .speed_mode     = LEDC_MODE,
        .channel        = LED_YELLOW,
        .timer_sel      = LEDC_TIMER,
        .intr_type      = LEDC_INTR_DISABLE,
        .gpio_num       = LED_GPIO_YELLOW,
        .duty           = 0, // Set duty to 0%
        .hpoint         = 0
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ledYellowChannel));
    yellowLedProfil.state = OFF;
    yellowLedProfil.mode = NORMAL;
    tempYellowLedProfil.state = OFF;
    tempYellowLedProfil.mode = NORMAL;


    // Prepare and then apply the LEDC PWM timer configuration
    ledc_timer_config_t ledBlueTimer = {
        .speed_mode       = LEDC_MODE,
        .duty_resolution  = LEDC_DUTY_RES,
        .timer_num        = LEDC_TIMER,
        .freq_hz          = LEDC_FREQUENCY,  // Set output frequency at 4 kHz
        .clk_cfg          = LEDC_AUTO_CLK
    };
    ESP_ERROR_CHECK(ledc_timer_config(&ledBlueTimer));

    // Prepare and then apply the LEDC PWM channel configuration
    ledc_channel_config_t ledBlueChannel = {
        .speed_mode     = LEDC_MODE,
        .channel        = LED_BLUE,
        .timer_sel      = LEDC_TIMER,
        .intr_type      = LEDC_INTR_DISABLE,
        .gpio_num       = LED_GPIO_BLUE,
        .duty           = 0, // Set duty to 0%
        .hpoint         = 0
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ledBlueChannel));
    blueLedProfil.state = OFF;
    blueLedProfil.mode = NORMAL;
    tempblueLedProfil.state = OFF;
    tempblueLedProfil.mode = NORMAL;
}

static void saveSettings() {
    // ESP_LOGI(TAG, "Save Settings tempMessage -> LED = %s, State = %s, Mode = %s", tempMessage.led, tempMessage.state, tempMessage.mode);
    // ESP_LOGI(TAG, "Save Settings message -> LED = %s, State = %s, Mode = %s", message.led, message.state, message.mode);
    if (tempMessage.mode != TEST && tempMessage.mode != SINGLETEST) {
        // ESP_LOGI(TAG, "Save Settings message and LEDs");

        message.led = tempMessage.led;
        message.state = tempMessage.state;
        message.mode = tempMessage.mode;

        redLedProfil.state = tempRedLedProfil.state;
        redLedProfil.mode = tempRedLedProfil.mode;

        greenLedProfil.state = tempGreenLedProfil.state;
        greenLedProfil.mode = tempGreenLedProfil.mode;

        yellowLedProfil.state = tempYellowLedProfil.state;
        yellowLedProfil.mode = tempYellowLedProfil.mode;

        blueLedProfil.state = tempblueLedProfil.state;
        blueLedProfil.mode = tempblueLedProfil.mode;
    }
}

static void loadSettings() { 
    tempMessage.led = message.led;
    tempMessage.state = message.state;
    tempMessage.mode = message.mode;

    tempRedLedProfil.state = redLedProfil.state;
    tempRedLedProfil.mode = redLedProfil.mode;

    tempGreenLedProfil.state = greenLedProfil.state;
    tempGreenLedProfil.mode = greenLedProfil.mode;

    tempYellowLedProfil.state = yellowLedProfil.state;
    tempYellowLedProfil.mode = yellowLedProfil.mode;

    tempblueLedProfil.state = blueLedProfil.state;
    tempblueLedProfil.mode = blueLedProfil.mode;
}

static void blink() {
    if(ledc_get_duty(LEDC_MODE, LED_BLUE) > 0) {
        ESP_LOGI(TAG, "Blue LED OFF");
        // Set duty to 50%
        ESP_ERROR_CHECK(ledc_set_duty(LEDC_MODE, LED_BLUE, OFF));
        // Update duty to apply the new value
        ESP_ERROR_CHECK(ledc_update_duty(LEDC_MODE, LED_BLUE));
    } else {
        ESP_LOGI(TAG, "Blue LED ON");
        ESP_ERROR_CHECK(ledc_set_duty(LEDC_MODE, LED_BLUE, ON));
        ESP_ERROR_CHECK(ledc_update_duty(LEDC_MODE, LED_BLUE));
    }
}

void ledControlTask( void *pvParameters ) {
    ESP_LOGI(TAG, "Start LedControlTask");
    
    tempMessage.mode = BLINK;
    xLedStateQueue = xQueueCreate( 10, sizeof( ledStateMessage ) );

    // Set the LEDC peripheral configuration
    ledInit();

    // TODO: Viel redudanter Code. Sehr oft rufe ich die Funktionen ledc_set_duty() und ledc_update_duty() auf. Gibt es nicht eine bessere Lösung?
    while (1) {
        saveSettings();
        
        if(xQueueReceive( xLedStateQueue, (void *) &tempMessage, BLINK_FREQ / portTICK_PERIOD_MS ) == pdTRUE ) {
            ESP_LOGI(TAG, "New tempMessage info. LED = %d, State = %d, Mode = %d", tempMessage.led, tempMessage.state, tempMessage.mode);
        } else {
            if (tempMessage.mode == NORMAL) { // Ändert die ausgewählte LED dauerhaft, bis sie erneut geändert wird.
                ESP_ERROR_CHECK(ledc_set_duty(LEDC_MODE, tempMessage.led, tempMessage.state));
                ESP_ERROR_CHECK(ledc_update_duty(LEDC_MODE, tempMessage.led));
            } else if (tempMessage.mode == TEST) { // Führt einen Test aller LEDs durch. Aber es muss sicher gestellt werden, dass nach dem TEST die LEDs wieder auf den Ausgangspunkt zurück gesetzt werden
                for (size_t i = 0; i < LED_MAX; i++) {
                    ESP_ERROR_CHECK(ledc_set_duty(LEDC_MODE, i, ON));
                    ESP_ERROR_CHECK(ledc_update_duty(LEDC_MODE, i));

                    vTaskDelay(1000 / portTICK_PERIOD_MS);
                }

                for (size_t i = 0; i < LED_MAX; i++) {
                    ESP_ERROR_CHECK(ledc_set_duty(LEDC_MODE, i, OFF));
                    ESP_ERROR_CHECK(ledc_update_duty(LEDC_MODE, i));
                }

                vTaskDelay(1000 / portTICK_PERIOD_MS);

                while (count < 4) {
                    if(count % 2 == 0) {
                        for (size_t i = 0; i < LED_MAX; i++) {
                            ESP_ERROR_CHECK(ledc_set_duty(LEDC_MODE, i, ON));
                            ESP_ERROR_CHECK(ledc_update_duty(LEDC_MODE, i));
                        }
                    } else {
                        for (size_t i = 0; i < LED_MAX; i++) {
                            ESP_ERROR_CHECK(ledc_set_duty(LEDC_MODE, i, OFF));
                            ESP_ERROR_CHECK(ledc_update_duty(LEDC_MODE, i));
                        }
                    }
                    count++;
                    vTaskDelay(1000 / portTICK_PERIOD_MS);
                }
                
                count = 0;
                loadSettings();
            } else if(tempMessage.mode == BLINK) {
                ESP_LOGI(TAG, "Blink-Mode");
                blink();
                vTaskDelay((BLINK_INTERVALL - BLINK_FREQ) / portTICK_PERIOD_MS);
            } else if(tempMessage.mode == SINGLETEST) {
                ESP_ERROR_CHECK(ledc_set_duty(LEDC_MODE, tempMessage.led, tempMessage.state));
                ESP_ERROR_CHECK(ledc_update_duty(LEDC_MODE, tempMessage.led));

                loadSettings();
            } else {
                ESP_LOGI(TAG, "Mode is undefined. Set MODE to normal");
                tempMessage.mode = NORMAL;
            }
        }
    }

    vTaskDelete(NULL);
}