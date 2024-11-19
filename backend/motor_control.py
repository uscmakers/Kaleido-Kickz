# motor_control.py

import RPi.GPIO as GPIO
import time

# Configure GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define GPIO pins
STEP_PIN = 17   # GPIO17
DIR_PIN = 27    # GPIO27
ENABLE_PIN = 22 # GPIO22 (optional)

# Setup GPIO pins
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(ENABLE_PIN, GPIO.OUT)

# Enable the motor driver (set to LOW if using ENABLE)
GPIO.output(ENABLE_PIN, GPIO.LOW)  # Adjust based on your driver

def set_direction(direction):
    """
    Set the direction of the motor.
    :param direction: 'CW' for clockwise, 'CCW' for counter-clockwise
    """
    if direction == 'CW':
        GPIO.output(DIR_PIN, GPIO.HIGH)
    elif direction == 'CCW':
        GPIO.output(DIR_PIN, GPIO.LOW)

def step_motor(steps, delay=0.001):
    """
    Step the motor a specific number of steps.
    :param steps: Number of steps to move
    :param delay: Delay between steps in seconds
    """
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(delay)

def cleanup():
    """
    Clean up GPIO settings.
    """
    GPIO.cleanup()
