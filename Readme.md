# WIZZY Surveillance Robot

## Overview
WIZZY is a self-patrolling surveillance robot powered by a Raspberry Pi 4. It features manual controls, real-time sensor data display, and video streaming capabilities. The robot can move in various directions and patrol autonomously.

## Features
- Manual control of the robot's movement (forward, backward, left, right, stop).
- Real-time sensor data display (temperature, distance, infrared sensor status).
- Live video feed from the robot's camera.
- Autonomous patrol functionality.

## Requirements
- Raspberry Pi 4
- Raspbian OS
- Camera module (compatible with Raspberry Pi)
- Ultrasonic distance sensor
- Temperature sensor (DS18B20)
- Infrared sensor
- Motors and motor driver
- Required Python libraries:
  - Flask
  - OpenCV
  - RPi.GPIO
  - unittest (for testing)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install required Python libraries:**
   ```bash
   pip install Flask opencv-python RPi.GPIO
   ```

3. **Set up GPIO pins:**
   Ensure that the GPIO pins are correctly wired to the motors and sensors as defined in the code.

4. **Enable the camera:**
   Make sure the camera module is enabled in the Raspberry Pi configuration settings.

## Usage

1. **Run the Flask application:**
   ```bash
   sudo python app.py
   ```

2. **Access the web interface:**
   Open a web browser and navigate to `http://<raspberry-pi-ip>:5000` to access the control interface.

3. **Control the robot:**
   Use the buttons on the web interface to control the robot's movement and refresh the sensor data.

## Testing
To run the unit tests for motor control, execute the following command:
```bash
python test_motor_control.py
```

## Cleanup
To stop the robot and clean up GPIO settings, you can use the cleanup function defined in the code. This is automatically called when the application is terminated.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments
- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [OpenCV](https://opencv.org/) for image processing.
- [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) for GPIO control on Raspberry Pi.