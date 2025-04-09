import face_recognition
import cv2
import os
import pickle

# Directories for storing images and encodings
KNOWN_FACES_DIR = "known_faces"
ENCODINGS_FILE = "face_encodings.pickle"

# Create folder if it doesn't exist
if not os.path.exists(KNOWN_FACES_DIR):
    os.makedirs(KNOWN_FACES_DIR)

# Initialize webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Capture an image from the webcam for face recognition
print("Please look at the camera. Press 's' to take a picture of your face.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Display the webcam feed
    cv2.imshow("Capture Face Image", frame)

    # Wait for the user to press 's' to capture an image
    key = cv2.waitKey(1) & 0xFF
    if key == ord("s"):
        # Save the captured image to the known_faces directory
        image_filename = os.path.join(KNOWN_FACES_DIR, "my_face.jpg")
        cv2.imwrite(image_filename, frame)
        print(f"Face image saved as {image_filename}")
        break

    # Press 'q' to quit
    if key == ord("q"):
        print("Exiting without saving.")
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()

# Process the captured image for face encoding
print("Processing the captured face image...")

# Load the saved image
image_path = os.path.join(KNOWN_FACES_DIR, "my_face.jpg")
image = face_recognition.load_image_file(image_path)
encodings = face_recognition.face_encodings(image)

if encodings:
    encoding = encodings[0]  # Take the first encoding (if multiple faces are found)

    # Save the face encoding and name (using 'my_face' as the name)
    try:
        if os.path.exists(ENCODINGS_FILE):
            with open(ENCODINGS_FILE, "rb") as file:
                known_face_encodings, known_face_names = pickle.load(file)
        else:
            known_face_encodings, known_face_names = [], []

        # Append the new encoding and name
        known_face_encodings.append(encoding)
        known_face_names.append("my_face")  # Use 'my_face' as the name for this image

        # Save the updated encodings and names to the pickle file
        with open(ENCODINGS_FILE, "wb") as file:
            pickle.dump((known_face_encodings, known_face_names), file)
        print("Face encoding saved!")

    except Exception as e:
        print(f"Error while saving face encoding: {e}")

else:
    print("No faces detected in the image.")

