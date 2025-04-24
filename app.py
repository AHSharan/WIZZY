from flask import Flask, render_template, Response, jsonify, request
import cv2
import threading
import logging
import os

from face_utils import load_known_faces, identify_faces
import motor_control
from sensors import read_ultrasonic_distance, read_temperature, read_ir_sensor

app = Flask(__name__)

running = True

# Initialize Raspberry Pi camera
try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 30
    camera.rotation = 180  # Adjust if your camera is upside down
    raw_capture = PiRGBArray(camera, size=(640, 480))
    use_picamera = True
    logging.info("Successfully initialized Raspberry Pi camera")
except (ImportError, Exception) as e:
    logging.error(f"Failed to initialize PiCamera: {str(e)}")
    camera = cv2.VideoCapture(0)
    use_picamera = False
    logging.info("Falling back to USB webcam")

known_encodings, known_names = load_known_faces('known_faces')

# Set up logging
logging.basicConfig(level=logging.INFO)

def gen_frames():
    while running:
        if use_picamera:
            try:
                # Use PiCamera
                for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
                    image = frame.array
                    face_data = identify_faces(image, known_encodings, known_names)
                    for (top, right, bottom, left, name) in face_data:
                        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.putText(image, name, (left, top - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
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
            face_data = identify_faces(frame, known_encodings, known_names)
            for (top, right, bottom, left, name) in face_data:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
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

@app.route('/patrol', methods=['POST'])
def patrol():
    try:
        motor_control.forward(speed=50, duration=2)
        motor_control.turn_right(speed=50, duration=1)
        motor_control.forward(speed=50, duration=2)
        motor_control.stop()
        return jsonify({"status": "patrol_complete"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cleanup():
    global running
    running = False
    camera.release()
    motor_control.cleanup()

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
