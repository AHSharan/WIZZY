import cv2
import face_recognition
import os

# Set recognition strictness (lower = stricter)
TOLERANCE = 0.4

# Load known face encodings
known_face_encodings = []
known_face_names = []

known_faces_dir = "known_faces"

print("[INFO] Loading known faces...")

for filename in os.listdir(known_faces_dir):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        path = os.path.join(known_faces_dir, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            known_face_encodings.append(encodings[0])
            name = os.path.splitext(filename)[0]
            known_face_names.append(name)
            print(f"[LOADED] {name}")

# Start camera
video_capture = cv2.VideoCapture(0)  # Use 0 for USB cam; for Pi cam, may require tweaks

if not video_capture.isOpened():
    print("[ERROR] Camera not accessible.")
    exit()

print("[INFO] Starting video stream. Press 'q' to quit.")

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("[ERROR] Failed to grab frame.")
        break

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect and encode faces
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        min_distance = min(distances) if distances.size > 0 else 1.0

        # Compare with known faces using strict tolerance
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=TOLERANCE)

        name = "Unknown"

        if True in matches:
            best_match_index = distances.argmin()
            name = known_face_names[best_match_index]

        # Scale back to original size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw rectangle and label
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        label = f"{name} ({1 - min_distance:.2f})" if name != "Unknown" else name
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, label, (left + 6, bottom - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
