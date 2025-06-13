import cv2
import mediapipe as mp
import pyautogui
import time

# Setup MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Controls
def press_key(k): pyautogui.keyDown(k)
def release_key(k): pyautogui.keyUp(k)

# Main game function
def game():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # width
    cap.set(4, 480)  # height

    last_key = None

    # Ratio thresholds
    left_ratio = 0.33
    right_ratio = 0.66
    center_horizontal_ratio = 0.5  # midpoint of screen height

    with mp_hands.Hands(min_detection_confidence=0.7,
                        min_tracking_confidence=0.7,
                        max_num_hands=1) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            # Define zones
            left_zone = int(w * left_ratio)
            right_zone = int(w * right_ratio)
            center_line_x = int(w / 2)
            center_line_y = int(h * center_horizontal_ratio)

            # Draw center vertical line
            cv2.line(frame, (center_line_x, 0), (center_line_x, h), (0, 255, 255), 2)

            # Draw horizontal line in center column
            cv2.line(frame, (left_zone, center_line_y), (right_zone, center_line_y), (0, 255, 0), 2)

            # Label zones
            cv2.putText(frame, "LEFT", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.putText(frame, "STRAIGHT", (center_line_x - 70, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(frame, "REVERSE", (center_line_x - 70, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, "RIGHT", (w - 100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

            action = "None"

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Wrist position
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    cx, cy = int(wrist.x * w), int(wrist.y * h)

                    # Draw dot at wrist
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                    # Determine zone
                    if cx < left_zone:
                        action = "Left"
                        current_key = "a"
                    elif cx > right_zone:
                        action = "Right"
                        current_key = "d"
                    else:
                        if cy < center_line_y:
                            action = "Straight"
                            current_key = "w"
                        else:
                            action = "Reverse"
                            current_key = "s"

                    break  # Use first hand only

                # Handle keypress switch
                if last_key != current_key:
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
                current_key = None

            # Show current action
            cv2.putText(frame, f"Action: {action}", (20, h - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.imshow("RaceAssist - Zone Control", frame)

            # 🔁 Continuous console feedback
            print(f"[INFO] Action: {action}")

            # Quit with 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Cleanup
    if last_key:
        release_key(last_key)
    cap.release()
    cv2.destroyAllWindows()

# Run
if __name__ == "__main__":
    game()
