import cv2
import mediapipe as mp
import pyautogui
import time

# Setup MediaPipe and PyAutoGUI
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Controls
def press_key(k): pyautogui.keyDown(k)
def release_key(k): pyautogui.keyUp(k)

# Main function
def game():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # width
    cap.set(4, 480)  # height

    last_key = None  # Track last key pressed to avoid repetition

    # Define screen zone boundaries
    left_ratio = 0.33
    right_ratio = 0.66

    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=1) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)

            # Draw 3 vertical zones
            left_zone = int(w * left_ratio)
            right_zone = int(w * right_ratio)
            cv2.line(frame, (left_zone, 0), (left_zone, h), (255, 255, 0), 2)
            cv2.line(frame, (right_zone, 0), (right_zone, h), (0, 255, 255), 2)
            cv2.putText(frame, "LEFT", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.putText(frame, "STRAIGHT", (w//2 - 60, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(frame, "RIGHT", (w - 100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

            action = "None"

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Extract wrist coordinates
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    cx, cy = int(wrist.x * w), int(wrist.y * h)

                    # Draw wrist point
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                    # Decide zone
                    if cx < left_zone:
                        action = "Left"
                        current_key = "a"
                    elif cx > right_zone:
                        action = "Right"
                        current_key = "d"
                    else:
                        action = "Straight"
                        current_key = "w"

                    break  # Only use first hand

                # Handle key press logic
                if current_key != last_key:
                    if last_key:
                        release_key(last_key)
                    press_key(current_key)
                    last_key = current_key
            else:
                # No hand detected
                if last_key:
                    release_key(last_key)
                    last_key = None
                action = "No Hand"

            # Display action
            cv2.putText(frame, f"Action: {action}", (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("RaceAssist - Simple Steering", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Cleanup
    if last_key:
        release_key(last_key)
    cap.release()
    cv2.destroyAllWindows()

# Entry point
if __name__ == "__main__":
    game()
