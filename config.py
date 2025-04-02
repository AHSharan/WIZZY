import os

class Config:
    TRIG_PIN = int(os.getenv('TRIG_PIN', 23))
    ECHO_PIN = int(os.getenv('ECHO_PIN', 24))
    IR_PIN = int(os.getenv('IR_PIN', 17))
    # Add other configurations as needed 