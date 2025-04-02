from flask import Flask, render_template, Response, jsonify, request
import cv2
import threading
import logging

from face_utils import load_known_faces, identify_faces
import motor_control
from sensors import read_ultrasonic_distance, read_temperature, read_ir_sensor

app = Flask(__name__)

running = True
camera = cv2.VideoCapture(0)
known_encodings, known_names = load_known_faces('known_faces')

# Set up logging
logging.basicConfig(level=logging.INFO)

def gen_frames():
    while running:
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
