import RPi.GPIO as GPIO
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define GPIO pins
M1_IN1 = 4
M1_IN2 = 17
M1_EN = 18

M2_IN1 = 27
M2_IN2 = 22
M2_EN = 23

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup([M1_IN1, M1_IN2, M1_EN, M2_IN1, M2_IN2, M2_EN], GPIO.OUT)

# Always enable motors (full speed)
GPIO.output(M1_EN, GPIO.HIGH)
GPIO.output(M2_EN, GPIO.HIGH)

# --- Movement Functions ---

def forward(duration=None):
    logging.info("Moving forward")
    GPIO.output(M1_IN1, GPIO.HIGH)
    GPIO.output(M1_IN2, GPIO.LOW)
    GPIO.output(M2_IN1, GPIO.HIGH)
    GPIO.output(M2_IN2, GPIO.LOW)
    if duration:
        time.sleep(duration)
        stop()

def backward(duration=None):
    logging.info("Moving backward")
    GPIO.output(M1_IN1, GPIO.LOW)
    GPIO.output(M1_IN2, GPIO.HIGH)
    GPIO.output(M2_IN1, GPIO.LOW)
    GPIO.output(M2_IN2, GPIO.HIGH)
    if duration:
        time.sleep(duration)
        stop()

def turn_left(duration=None):
    logging.info("Turning left")
    GPIO.output(M1_IN1, GPIO.LOW)
    GPIO.output(M1_IN2, GPIO.HIGH)
    GPIO.output(M2_IN1, GPIO.HIGH)
    GPIO.output(M2_IN2, GPIO.LOW)
    if duration:
        time.sleep(duration)
        stop()

def turn_right(duration=None):
    logging.info("Turning right")
    GPIO.output(M1_IN1, GPIO.HIGH)
    GPIO.output(M1_IN2, GPIO.LOW)
    GPIO.output(M2_IN1, GPIO.LOW)
    GPIO.output(M2_IN2, GPIO.HIGH)
    if duration:
        time.sleep(duration)
        stop()

def stop():
    logging.info("Stopping")
    GPIO.output(M1_IN1, GPIO.LOW)
    GPIO.output(M1_IN2, GPIO.LOW)
    GPIO.output(M2_IN1, GPIO.LOW)
    GPIO.output(M2_IN2, GPIO.LOW)

def cleanup():
    stop()
    GPIO.cleanup()
if __name__ == "__main__":
    try:
        print("Starting motor test...")
        forward(duration=2)
        time.sleep(1)

        backward(duration=2)
        time.sleep(1)

        turn_left(duration=2)
        time.sleep(1)

        turn_right(duration=2)
        time.sleep(1)

        stop()
        print("Motor test complete.")

    except KeyboardInterrupt:
        print("Test interrupted by user.")

    finally:
        cleanup()
