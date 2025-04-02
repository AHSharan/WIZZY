import RPi.GPIO as GPIO
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define GPIO pins for motor control
LEFT_MOTOR_IN1 = 5
LEFT_MOTOR_IN2 = 6
RIGHT_MOTOR_IN3 = 13
RIGHT_MOTOR_IN4 = 19
PWM_FREQ = 50

# Set up GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_MOTOR_IN1, GPIO.OUT)
GPIO.setup(LEFT_MOTOR_IN2, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR_IN3, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR_IN4, GPIO.OUT)

# Initialize PWM for motor control
left_pwm1 = GPIO.PWM(LEFT_MOTOR_IN1, PWM_FREQ)
left_pwm2 = GPIO.PWM(LEFT_MOTOR_IN2, PWM_FREQ)
right_pwm3 = GPIO.PWM(RIGHT_MOTOR_IN3, PWM_FREQ)
right_pwm4 = GPIO.PWM(RIGHT_MOTOR_IN4, PWM_FREQ)

# Start PWM with 0 duty cycle
left_pwm1.start(0)
left_pwm2.start(0)
right_pwm3.start(0)
right_pwm4.start(0)

# Function to move forward
def forward(speed=50, duration=None):
    logging.info(f"Moving forward at speed {speed} for duration {duration}.")
    left_pwm1.ChangeDutyCycle(speed)
    left_pwm2.ChangeDutyCycle(0)
    right_pwm3.ChangeDutyCycle(speed)
    right_pwm4.ChangeDutyCycle(0)
    if duration:
        time.sleep(duration)
        stop()

# Function to move backward
def backward(speed=50, duration=None):
    logging.info(f"Moving backward at speed {speed} for duration {duration}.")
    left_pwm1.ChangeDutyCycle(0)
    left_pwm2.ChangeDutyCycle(speed)
    right_pwm3.ChangeDutyCycle(0)
    right_pwm4.ChangeDutyCycle(speed)
    if duration:
        time.sleep(duration)
        stop()

# Function to turn left
def turn_left(speed=50, duration=None):
    logging.info(f"Turning left at speed {speed} for duration {duration}.")
    left_pwm1.ChangeDutyCycle(0)
    left_pwm2.ChangeDutyCycle(speed)
    right_pwm3.ChangeDutyCycle(speed)
    right_pwm4.ChangeDutyCycle(0)
    if duration:
        time.sleep(duration)
        stop()

# Function to turn right
def turn_right(speed=50, duration=None):
    logging.info(f"Turning right at speed {speed} for duration {duration}.")
    left_pwm1.ChangeDutyCycle(speed)
    left_pwm2.ChangeDutyCycle(0)
    right_pwm3.ChangeDutyCycle(0)
    right_pwm4.ChangeDutyCycle(speed)
    if duration:
        time.sleep(duration)
        stop()

# Function to stop the motors
def stop():
    left_pwm1.ChangeDutyCycle(0)
    left_pwm2.ChangeDutyCycle(0)
    right_pwm3.ChangeDutyCycle(0)
    right_pwm4.ChangeDutyCycle(0)

# Function to clean up GPIO settings
def cleanup():
    stop()
    GPIO.cleanup()
