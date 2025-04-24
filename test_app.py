from flask import Flask, render_template, Response, jsonify, request
import cv2
import logging
import os
import RPi.GPIO as GPIO
import time
from smart_patrol import SmartPatrol

# Set up logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Clean up GPIO at start
GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.cleanup()  # Clean up GPIO first

# IR Sensor pins - Updated to use free GPIO pins
IR_LEFT = 14    # GPIO14 - free
IR_CENTER = 15  # GPIO15 - free
IR_RIGHT = 24   # GPIO24 - free

# Setup IR sensors
def setup_ir_sensors():
    GPIO.setup(IR_LEFT, GPIO.IN)
    GPIO.setup(IR_CENTER, GPIO.IN)
    GPIO.setup(IR_RIGHT, GPIO.IN)

# Read IR sensors
def read_ir_sensors():
    return {
        'left': GPIO.input(IR_LEFT),
        'center': GPIO.input(IR_CENTER),
        'right': GPIO.input(IR_RIGHT)
    }

import motor_control

app = Flask(__name__)
running = True
camera = None
use_picamera = False

# Initialize IR sensors
setup_ir_sensors()

# Initialize smart patrol
smart_patrol = SmartPatrol(motor_control, read_ir_sensors)

def init_camera():
    global camera, use_picamera
    try:
        # First try PiCamera
        from picamera2 import Picamera2  # Using newer PiCamera2 library
        camera = Picamera2()
        camera.configure(camera.create_preview_configuration(main={"size": (640, 480)}))
        camera.start()
        use_picamera = True
        logger.info("Successfully initialized Picamera2")
    except Exception as e:
        logger.error(f"Failed to initialize PiCamera2: {str(e)}")
        try:
            # Fallback to USB webcam
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                raise Exception("Failed to open USB webcam")
            use_picamera = False
            logger.info("Successfully initialized USB webcam")
        except Exception as e:
            logger.error(f"Failed to initialize USB webcam: {str(e)}")
            raise

def gen_frames():
    global camera, running
    while running:
        try:
            if use_picamera:
                # Use PiCamera2
                frame = camera.capture_array()
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                # Use USB webcam
                success, frame = camera.read()
                if not success:
                    logger.error("Failed to capture frame from camera.")
                    break
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            logger.error(f"Error capturing frame: {str(e)}")
            break

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/move', methods=['POST'])
def move():
    try:
        direction = request.form.get('direction', 'stop')
        duration = float(request.form.get('duration', 1.0))

        # Read IR sensors before moving
        ir_data = read_ir_sensors()
        
        # Basic collision avoidance
        if direction == 'forward' and ir_data['center']:
            return jsonify({"status": "blocked", "message": "Obstacle detected ahead", "sensors": ir_data}), 400
        elif direction == 'left' and ir_data['left']:
            return jsonify({"status": "blocked", "message": "Obstacle detected on left", "sensors": ir_data}), 400
        elif direction == 'right' and ir_data['right']:
            return jsonify({"status": "blocked", "message": "Obstacle detected on right", "sensors": ir_data}), 400

        if direction == 'forward':
            motor_control.forward(duration=duration)
        elif direction == 'backward':
            motor_control.backward(duration=duration)
        elif direction == 'left':
            motor_control.turn_left(duration=duration)
        elif direction == 'right':
            motor_control.turn_right(duration=duration)
        else:
            motor_control.stop()
        
        # Return both movement status and sensor data
        return jsonify({
            "status": "ok", 
            "direction": direction,
            "sensors": read_ir_sensors()
        })
    except Exception as e:
        logger.error(f"Error in move command: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/sensors')
def get_sensors():
    try:
        sensor_data = read_ir_sensors()
        return jsonify({
            "status": "ok",
            "sensors": sensor_data
        })
    except Exception as e:
        logger.error(f"Error reading sensors: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/patrol', methods=['POST'])
def patrol():
    try:
        action = request.form.get('action', 'start')
        if action == 'start':
            if smart_patrol.start_patrol():
                return jsonify({"status": "ok", "message": "Smart patrol started"})
            else:
                return jsonify({"status": "error", "message": "Patrol already running"}), 400
        else:
            smart_patrol.stop_patrol()
            return jsonify({"status": "ok", "message": "Smart patrol stopped"})
    except Exception as e:
        logger.error(f"Error in patrol command: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def cleanup():
    global running, camera
    running = False
    if camera:
        if use_picamera:
            camera.stop()
        else:
            camera.release()
    smart_patrol.stop_patrol()  # Stop patrol if running
    motor_control.cleanup()
    GPIO.cleanup()

if __name__ == '__main__':
    try:
        init_camera()  # Initialize camera before starting the app
        # Enable threading and allow external access
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
    finally:
        cleanup() 