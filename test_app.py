from flask import Flask, render_template, Response, jsonify, request
import cv2
import logging
import os
import RPi.GPIO as GPIO

# Set up logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Clean up GPIO at start
GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.cleanup()  # Clean up GPIO first

import motor_control

app = Flask(__name__)
running = True
camera = None
use_picamera = False

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
        return jsonify({"status": "ok", "direction": direction})
    except Exception as e:
        logger.error(f"Error in move command: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def cleanup():
    global running, camera
    running = False
    if camera:
        if use_picamera:
            camera.stop()
        else:
            camera.release()
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