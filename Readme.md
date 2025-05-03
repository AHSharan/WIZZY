# WIZZY Surveillance Robot

## Overview
WIZZY is an advanced self-patrolling surveillance robot powered by a Raspberry Pi 4. It combines manual control capabilities with intelligent autonomous patrolling, real-time sensor monitoring, and video streaming. The robot features sophisticated obstacle avoidance, area coverage optimization, and a web-based control interface.

## Core Features

### Autonomous Navigation
- Smart patrol system with obstacle avoidance
- Area coverage optimization
- Intelligent path planning and decision making
- Stuck detection and recovery mechanisms
- Pattern recognition for efficient movement

### Manual Control
- Web-based control interface
- Directional movement (forward, backward, left, right)
- Real-time movement control
- Emergency stop functionality

### Sensor Integration
- Ultrasonic distance sensor for obstacle detection
- Temperature monitoring (DS18B20)
- Infrared sensors for edge detection
- Real-time sensor data display
- Multi-sensor fusion for environment analysis

### Video and Surveillance
- Live video streaming
- Camera rotation support (180°)
- Fallback to USB webcam if PiCamera is unavailable
- High-resolution video feed (640x480 @ 30fps)

## Technical Requirements

### Hardware
- Raspberry Pi 4
- Raspbian OS
- Camera module (compatible with Raspberry Pi)
- Ultrasonic distance sensor (HC-SR04)
- Temperature sensor (DS18B20)
- Infrared sensors
- Motor driver (L298N or similar)
- DC motors (4x)
- Power supply (12V recommended)

### Software Dependencies
- Python 3.x
- Flask (2.0.1) - Web framework
- OpenCV (4.5.3.56) - Computer vision
- NumPy (1.21.2) - Numerical computing
- PiCamera (1.13) - Camera interface
- RPi.GPIO (0.7.0) - GPIO control
- face-recognition (1.3.0) - Face detection
- python-dotenv (0.19.0) - Environment management
- gunicorn (20.1.0) - Production server

## Pin Connections

### Motor Connections (L298N Driver)
```
Motor 1 (Front Left):
- IN1: GPIO 4
- IN2: GPIO 17
- EN: GPIO 18

Motor 2 (Front Right):
- IN1: GPIO 27
- IN2: GPIO 22
- EN: GPIO 23

Motor 3 (Rear Left):
- IN1: GPIO 5
- IN2: GPIO 6
- EN: GPIO 12

Motor 4 (Rear Right):
- IN1: GPIO 13
- IN2: GPIO 19
- EN: GPIO 26
```

### Sensor Connections
```
Ultrasonic Sensor (HC-SR04):
- TRIG: GPIO 29
- ECHO: GPIO 34
- VCC: 5V
- GND: GND

Infrared Sensor:
- Signal: GPIO 37
- VCC: 3.3V
- GND: GND

Temperature Sensor (DS18B20):
- Data: GPIO 4 (1-Wire)
- VCC: 3.3V
- GND: GND
- Note: Requires 4.7kΩ pull-up resistor
```

### Power Connections
```
Motor Driver:
- 12V Input: Connect to 12V power supply
- 5V Output: Can be used to power Raspberry Pi
- GND: Connect to common ground

Raspberry Pi:
- Power: 5V (from motor driver or separate supply)
- GND: Connect to common ground
```

### Camera Connection
```
Raspberry Pi Camera Module:
- Connect to CSI port on Raspberry Pi
- Ensure camera is enabled in raspi-config
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Hardware Setup:**
   - Connect motors to motor driver
   - Connect sensors to appropriate GPIO pins
   - Mount camera module
   - Ensure proper power supply

4. **Configuration:**
   - Enable camera in Raspberry Pi settings
   - Configure GPIO pins in `config.py`
   - Set up environment variables if needed

## Usage

### Starting the Robot
1. **Launch the web server:**
   ```bash
   sudo python app.py
   ```

2. **Access the interface:**
   - Open web browser
   - Navigate to `http://<raspberry-pi-ip>:5000`

### Control Options
- **Manual Mode:**
  - Use web interface buttons for direct control
  - Monitor real-time sensor data
  - View live video feed

- **Autonomous Mode:**
  - Start/stop patrol mode
  - Monitor patrol status
  - View coverage statistics

### Remote Access with ngrok
For remote access to the robot's web interface from outside your local network:

1. **Install ngrok:**
   ```bash
   # Download ngrok
   wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm.tgz
   # Extract
   tar xvzf ngrok-v3-stable-linux-arm.tgz
   ```

2. **Start ngrok tunnel:**
   ```bash
   # Start tunnel to Flask server
   ./ngrok http 5000
   ```

3. **Access the robot remotely:**
   - Use the HTTPS URL provided by ngrok
   - The URL will look like: `https://xxxx-xx-xx-xxx-xx.ngrok.io`
   - Share this URL to access the robot from anywhere

4. **Security Considerations:**
   - Use ngrok's authentication features
   - Consider setting up basic auth for the web interface
   - Monitor ngrok dashboard for unauthorized access
   - Use ngrok's paid tier for static URLs if needed

## Testing
The project includes comprehensive test suites:
```bash
# Run all tests
python test_app.py
python test_motor_control.py
python test_ir_sensors.py
python test_face_utils.py
```

## Safety and Maintenance
- Automatic GPIO cleanup on shutdown
- Emergency stop functionality
- Regular sensor calibration
- System health monitoring

## Project Structure
- `app.py` - Main Flask application
- `smart_patrol.py` - Autonomous navigation logic
- `motor_control.py` - Motor control interface
- `sensors.py` - Sensor management
- `face_utils.py` - Face recognition utilities
- `config.py` - Configuration settings
- `templates/` - Web interface templates
- `known_faces/` - Face recognition database

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [OpenCV](https://opencv.org/) - Computer vision
- [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) - GPIO control
- [PiCamera](https://picamera.readthedocs.io/) - Camera interface