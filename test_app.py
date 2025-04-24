from flask import Flask, render_template, Response, jsonify, request
import cv2
import logging
import os

import motor_control

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

# Set up logging
logging.basicConfig(level=logging.INFO)

def gen_frames():
    while running:
        if use_picamera:
            try:
                # Use PiCamera
                for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
                    image = frame.array
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

def cleanup():
    global running
    running = False
    if not use_picamera:
        camera.release()
    motor_control.cleanup()

if __name__ == '__main__':
    try:
        # Enable threading and allow external access
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup() 