import time

import RPi.GPIO as GPIO


LED_PIN = 11
BUZZER_PIN = 7
FREQUENCY = 523
UNIT_TIME = 0.2

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

buzzer = GPIO.PWM(BUZZER_PIN, FREQUENCY)


def signal(duration):
    """Turn on the LED and buzzer for one Morse-code signal."""
    GPIO.output(LED_PIN, GPIO.HIGH)
    buzzer.start(50)
    time.sleep(duration * UNIT_TIME)
    buzzer.stop()
    GPIO.output(LED_PIN, GPIO.LOW)


def pause(duration):
    """Wait between Morse-code signals."""
    time.sleep(duration * UNIT_TIME)


try:
    while True:
        # S: three short signals
        for _ in range(3):
            signal(1)
            pause(1)
        pause(2)

        # O: three long signals
        for _ in range(3):
            signal(3)
            pause(1)
        pause(2)

        # S: three short signals
        for _ in range(3):
            signal(1)
            pause(1)

        pause(7)

except KeyboardInterrupt:
    pass
finally:
    buzzer.stop()
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()