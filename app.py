from flask import Flask, render_template, Response, jsonify, request
import cv2
import threading
import logging
import os

# Comment out face recognition import
# from face_utils import load_known_faces, identify_faces
import motor_control
from sensors import read_ultrasonic_distance, read_temperature, read_ir_sensor
from smart_patrol import SmartPatrol

app = Flask(__name__)

running = True
patrol_instance = None  # Global variable to store SmartPatrol instance

# Initialize Raspberry Pi camera
try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 30
    camera.rotation = 180  # Rotate camera 180 degrees
    raw_capture = PiRGBArray(camera, size=(640, 480))
    use_picamera = True
    logging.info("Successfully initialized Raspberry Pi camera")
except (ImportError, Exception) as e:
    logging.error(f"Failed to initialize PiCamera: {str(e)}")
    camera = cv2.VideoCapture(0)
    use_picamera = False
    logging.info("Falling back to USB webcam")

# Comment out face recognition loading
# known_encodings, known_names = load_known_faces('known_faces')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SmartPatrol
def get_sensor_data():
    return {
        'center': read_ultrasonic_distance() < 30,  # True if obstacle within 30cm
        'left': False,  # Will be updated with side sensors
        'right': False,  # Will be updated with side sensors
        'ir': read_ir_sensor()
    }

patrol_instance = SmartPatrol(motor_control, get_sensor_data)

def gen_frames():
    while running:
        if use_picamera:
            try:
                # Use PiCamera
                for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
                    image = frame.array
                    # Comment out face recognition processing
                    # face_data = identify_faces(image, known_encodings, known_names)
                    # for (top, right, bottom, left, name) in face_data:
                    #     cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                    #     cv2.putText(image, name, (left, top - 10),
                    #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
                    ret, buffer = cv2.imencode('.jpg', image)
                    if not ret:
                        continue
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    raw_capture.truncate(0)
            except Exception as e:
                logging.error(f"Error in PiCamera capture: {str(e)}")
                break
        else:
            # Use standard webcam
            success, frame = camera.read()
            if not success:
                logging.error("Failed to capture frame from camera.")
                break
            # Comment out face recognition processing
            # face_data = identify_faces(frame, known_encodings, known_names)
            # for (top, right, bottom, left, name) in face_data:
            #     cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            #     cv2.putText(frame, name, (left, top - 10),
            #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/sensors')
def sensor_data():
    data = {
        "temperature": read_temperature(),
        "distance": read_ultrasonic_distance(),
        "ir_triggered": read_ir_sensor()
    }
    return jsonify(data)

@app.route('/move', methods=['POST'])
def move():
    direction = request.form.get('direction', 'stop')
    speed = int(request.form.get('speed', 50))
    duration = float(request.form.get('duration', 1.0))

    if direction == 'forward':
        motor_control.forward(speed, duration)
    elif direction == 'backward':
        motor_control.backward(speed, duration)
    elif direction == 'left':
        motor_control.turn_left(speed, duration)
    elif direction == 'right':
        motor_control.turn_right(speed, duration)
    else:
        motor_control.stop()
    return jsonify({"status": "ok", "direction": direction})

@app.route('/patrol/start', methods=['POST'])
def start_patrol():
    """Start the smart patrol"""
    global patrol_instance
    try:
        if patrol_instance.start_patrol():
            return jsonify({"status": "success", "message": "Smart patrol started"})
        else:
            return jsonify({"status": "error", "message": "Patrol already running"}), 400
    except Exception as e:
        logger.error(f"Error starting patrol: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/patrol/stop', methods=['POST'])
def stop_patrol():
    """Stop the smart patrol"""
    global patrol_instance
    try:
        patrol_instance.stop_patrol()
        return jsonify({"status": "success", "message": "Smart patrol stopped"})
    except Exception as e:
        logger.error(f"Error stopping patrol: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/patrol/status', methods=['GET'])
def patrol_status():
    """Get the current patrol status"""
    global patrol_instance
    try:
        status = {
            "is_patrolling": patrol_instance.is_patrolling,
            "last_turn": patrol_instance.last_turn.value if patrol_instance.last_turn else None,
            "consecutive_blocks": patrol_instance.consecutive_blocks
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting patrol status: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def cleanup():
    global running, patrol_instance
    running = False
    if not use_picamera:
        camera.release()
    if patrol_instance:
        patrol_instance.stop_patrol()
    motor_control.cleanup()

if __name__ == '__main__':
    try:
        # Enable threading and allow external access
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
