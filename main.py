import cv2
import mediapipe as mp
import speech_recognition as sr
import pyautogui
import system_control
import time

# Initialize Hand & Face Tracking
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Initialize Camera
cap = cv2.VideoCapture(0)
screen_width, screen_height = pyautogui.size()
prev_x, prev_y = 0, 0  # For smooth cursor movement
nod_history, shake_history, brightness_history = [], [], []  # To store past movement data

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"🗣️ You said: {command}")
            return command
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            print("🤷 Couldn't understand the command.")
    return None

def process_tracking():
    global prev_x, prev_y, nod_history, shake_history, brightness_history

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Camera not found. Please check your webcam.")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process Hand and Face Tracking
        hand_results = hands.process(rgb_frame)
        face_results = face_mesh.process(rgb_frame)

        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get landmarks
                index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                x, y = int(index_finger.x * screen_width), int(index_finger.y * screen_height)

                # Move cursor smoothly
                smooth_x = int(prev_x * 0.7 + x * 0.3)
                smooth_y = int(prev_y * 0.7 + y * 0.3)
                pyautogui.moveTo(smooth_x, smooth_y, duration=0.1)
                prev_x, prev_y = smooth_x, smooth_y

                # Store y-coordinates for brightness control (Swipe Detection)
                brightness_history.append(y)
                if len(brightness_history) > 5:
                    brightness_history.pop(0)

                # Ensure we have enough data before checking brightness change
                if len(brightness_history) >= 2:
                    if brightness_history[-1] < brightness_history[0] - 30:  # Swipe Up
                        system_control.execute_command("increase brightness")
                        brightness_history.clear()

                    elif brightness_history[-1] > brightness_history[0] + 30:  # Swipe Down
                        system_control.execute_command("decrease brightness")
                        brightness_history.clear()

        # Detect Face Nodding or Shaking
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION)

                nose = face_landmarks.landmark[1]  # Nose tip

                # Store movement history
                nod_history.append(nose.y)
                shake_history.append(nose.x)

                if len(nod_history) > 5:
                    nod_history.pop(0)
                if len(shake_history) > 5:
                    shake_history.pop(0)

                # Detect nod (Yes) - Vertical movement
                if len(nod_history) >= 2 and max(nod_history) - min(nod_history) > 0.02:
                    system_control.execute_command("volume up")
                    nod_history.clear()

                # Detect shake (No) - Horizontal movement
                if len(shake_history) >= 2 and max(shake_history) - min(shake_history) > 0.04:
                    system_control.execute_command("volume down")
                    shake_history.clear()

        cv2.imshow("🖐 Gesture & Face Control", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

if __name__ == "__main__":
    print("🎤 Speak a command or use gestures!")

    while True:
        command = recognize_speech()
        if command:
            system_control.execute_command(command)

        process_tracking()

    cap.release()
    cv2.destroyAllWindows()
