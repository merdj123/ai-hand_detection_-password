import cv2
import mediapipe as mp
import face_recognition
import numpy as np
import pickle
import serial
import time
import playsound

# Load known face encodings
ENCODINGS_FILE = "face_encodings.pickle"
with open(ENCODINGS_FILE, "rb") as file:
    known_face_encodings, known_face_names = pickle.load(file)

# Initialize MediaPipe hand recognition
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Initialize Arduino connection (adjust port if needed)
arduino = serial.Serial("COM3", 9600)  # Change "COM3" if needed
time.sleep(2)

# Correct password sequence and entered password
correct_password = [1, 2, 3, 5, 4]
entered_password = []

# Variables to detect a stable gesture for 2 seconds
prev_fingers = None
stable_start_time = None
gesture_registered = False

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Mirror the image for a natural mirror-like view
    frame = cv2.flip(frame, 1)

    # Convert frame for face recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Check if a known face is recognized
    face_authenticated = False
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        if True in matches:
            face_authenticated = True
            break

    if not face_authenticated:
        cv2.putText(frame, "Unauthorized!", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # Reset gesture variables if face not recognized
        prev_fingers = None
        stable_start_time = None
        gesture_registered = False
        cv2.imshow("Face & Hand Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue

    # Process hand detection using MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    fingers_detected = 0
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Count extended fingers:
            # Thumb: For mirrored image, check if thumb tip is to the left of thumb IP.
            if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                fingers_detected += 1
            # For index, middle, ring, and pinky:
            for tip in [8, 12, 16, 20]:
                if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                    fingers_detected += 1

    # Only consider valid counts (1 to 5)
    if 0 < fingers_detected <= 5:
        # If the gesture has changed, reset the timer and registration flag.
        if prev_fingers is None or fingers_detected != prev_fingers:
            prev_fingers = fingers_detected
            stable_start_time = time.time()
            gesture_registered = False
        else:
            # If same gesture as before, check if it's been steady for 2 seconds.
            if time.time() - stable_start_time >= 2 and not gesture_registered:
                # Register the gesture input
                entered_password.append(fingers_detected)
                arduino.write(str(fingers_detected).encode())  # Light up corresponding LEDs
                gesture_registered = True
                # Optionally, reset the timer to avoid double input
                stable_start_time = time.time()
    else:
        # If no valid gesture, reset stability tracking
        prev_fingers = None
        stable_start_time = None
        gesture_registered = False

    # Display the current entered password on the frame
    password_text = "Entered Password: " + " ".join(map(str, entered_password))
    cv2.putText(frame, password_text, (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Check if full password is entered
    if len(entered_password) == len(correct_password):
        if entered_password == correct_password:
            print("Correct Password!")
            playsound.playsound(r"C:\Users\IdeaPad\PycharmProjects\LED_hand_face_id\.venv\success.mp3")
            arduino.write(b"S")
        else:
            print("Wrong Password!")
            playsound.playsound(r"error.mp3")
            arduino.write(b"F")
        cv2.putText(frame, "Password Processed. Resetting...", (50, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("Face & Hand Recognition", frame)
        cv2.waitKey(1)
        time.sleep(2)  # Hold message for 2 seconds
        entered_password = []
        prev_fingers = None
        stable_start_time = None
        gesture_registered = False

    # Show the webcam feed
    cv2.imshow("Face & Hand Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
