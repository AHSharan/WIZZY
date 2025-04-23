import unittest
import os
import numpy as np
import face_recognition
from face_utils import load_known_faces, identify_faces
import cv2

class TestFaceRecognition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use the existing known_faces directory
        cls.test_dir = 'known_faces'
        
        # Get all image files directly in the known_faces directory
        cls.test_images = []
        for filename in os.listdir(cls.test_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(cls.test_dir, filename)
                image = cv2.imread(image_path)
                if image is not None:
                    cls.test_images.append((filename, image))
        
        if not cls.test_images:
            raise FileNotFoundError("No valid images found in known_faces directory")

    def test_load_known_faces(self):
        """Test loading known faces from directory"""
        known_encodings, known_names = load_known_faces(self.test_dir)
        
        # Check if we got the expected number of encodings
        self.assertGreater(len(known_encodings), 0)
        self.assertEqual(len(known_encodings), len(known_names))
        
        # Check if we have the expected names
        expected_names = [os.path.splitext(f)[0] for f, _ in self.test_images]
        for name in expected_names:
            self.assertIn(name, known_names)

    def test_identify_faces(self):
        """Test face identification in a frame"""
        # Load known faces
        known_encodings, known_names = load_known_faces(self.test_dir)
        
        # Test each image
        for filename, test_image in self.test_images:
            # Use the test image for identification
            test_frame = test_image.copy()
            
            # Test face identification
            face_identities = identify_faces(test_frame, known_encodings, known_names)
            
            # Check if we got face locations
            self.assertGreater(len(face_identities), 0, f"No faces found in {filename}")
            
            # Check the structure of returned data
            for face in face_identities:
                self.assertEqual(len(face), 5)  # top, right, bottom, left, name
                self.assertIsInstance(face[0], int)  # top
                self.assertIsInstance(face[1], int)  # right
                self.assertIsInstance(face[2], int)  # bottom
                self.assertIsInstance(face[3], int)  # left
                self.assertIsInstance(face[4], str)  # name

    def test_identify_faces_no_faces(self):
        """Test face identification with no faces in frame"""
        # Load known faces
        known_encodings, known_names = load_known_faces(self.test_dir)
        
        # Create a test frame with no faces
        test_frame = np.zeros((200, 200, 3), dtype=np.uint8)
        
        # Test face identification
        face_identities = identify_faces(test_frame, known_encodings, known_names)
        
        # Should return empty list when no faces are found
        self.assertEqual(len(face_identities), 0)

if __name__ == '__main__':
    unittest.main() 