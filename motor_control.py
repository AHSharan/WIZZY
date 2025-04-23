import RPi.GPIO as GPIO
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define all motor pins
M1_IN1, M1_IN2, M1_EN = 4, 17, 18
M2_IN1, M2_IN2, M2_EN = 27, 22, 23
M3_IN1, M3_IN2, M3_EN = 5, 6, 12
M4_IN1, M4_IN2, M4_EN = 13, 19, 26

# All GPIOs to setup
ALL_PINS = [M1_IN1, M1_IN2, M1_EN,
            M2_IN1, M2_IN2, M2_EN,
            M3_IN1, M3_IN2, M3_EN,
            M4_IN1, M4_IN2, M4_EN]

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(ALL_PINS, GPIO.OUT)

# Enable all motors
GPIO.output(M1_EN, GPIO.HIGH)
GPIO.output(M2_EN, GPIO.HIGH)
GPIO.output(M3_EN, GPIO.HIGH)
GPIO.output(M4_EN, GPIO.HIGH)

# --- Movement Functions ---

def forward(duration=None):
    logging.info("Moving forward")
    for (IN1, IN2) in [(M1_IN1, M1_IN2), (M2_IN1, M2_IN2), (M3_IN1, M3_IN2), (M4_IN1, M4_IN2)]:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    if duration:
        time.sleep(duration)
        stop()

def backward(duration=None):
    logging.info("Moving backward")
    for (IN1, IN2) in [(M1_IN1, M1_IN2), (M2_IN1, M2_IN2), (M3_IN1, M3_IN2), (M4_IN1, M4_IN2)]:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
    if duration:
        time.sleep(duration)
        stop()

def turn_left(duration=None):
    logging.info("Turning left")
    # Left motors backward, right motors forward
    for (IN1, IN2) in [(M1_IN1, M1_IN2), (M3_IN1, M3_IN2)]:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
    for (IN1, IN2) in [(M2_IN1, M2_IN2), (M4_IN1, M4_IN2)]:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    if duration:
        time.sleep(duration)
        stop()

def turn_right(duration=None):
    logging.info("Turning right")
    # Left motors forward, right motors backward
    for (IN1, IN2) in [(M1_IN1, M1_IN2), (M3_IN1, M3_IN2)]:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    for (IN1, IN2) in [(M2_IN1, M2_IN2), (M4_IN1, M4_IN2)]:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
    if duration:
        time.sleep(duration)
        stop()

def stop():
    logging.info("Stopping")
    for (IN1, IN2) in [(M1_IN1, M1_IN2), (M2_IN1, M2_IN2), (M3_IN1, M3_IN2), (M4_IN1, M4_IN2)]:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)

def cleanup():
    stop()
    GPIO.cleanup()

# --- Test Block ---
if __name__ == "__main__":
    try:
        print("Starting 4-motor test...")

        forward(duration=2)
        time.sleep(1)

        backward(duration=2)
        time.sleep(1)

        turn_left(duration=2)
        time.sleep(1)

        turn_right(duration=2)
        time.sleep(1)

        stop()
        print("Test complete!")

    except KeyboardInterrupt:
        print("Test interrupted by user.")

    finally:
        cleanup()
