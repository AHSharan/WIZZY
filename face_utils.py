import os
import face_recognition
import numpy as np

# Function to load known faces from a directory
def load_known_faces(known_faces_dir='known_faces'):
    known_encodings = []
    known_names = []
    for name in os.listdir(known_faces_dir):
        person_dir = os.path.join(known_faces_dir, name)
        if not os.path.isdir(person_dir):
            continue
        for filename in os.listdir(person_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(person_dir, filename)
                image = face_recognition.load_image_file(filepath)
                encodings = face_recognition.face_encodings(image)
                if len(encodings) > 0:
                    known_encodings.append(encodings[0])
                    known_names.append(name)
    return known_encodings, known_names

# Function to identify faces in a given frame
def identify_faces(frame, known_encodings, known_names):
    rgb_frame = frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encs = face_recognition.face_encodings(rgb_frame, face_locations)
    face_identities = []

    for face_enc, (top, right, bottom, left) in zip(face_encs, face_locations):
        matches = face_recognition.compare_faces(known_encodings, face_enc, tolerance=0.6)
        name = "Unknown"
        if True in matches:
            match_idx = np.argmax(matches)
            name = known_names[match_idx]
        face_identities.append((top, right, bottom, left, name))
    return face_identities
