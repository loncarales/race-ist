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
def game():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # width
    cap.set(4, 480)  # height

    last_keys = []

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

            # Grid partition
            left_zone = int(w / 3)
            right_zone = int(2 * w / 3)
            top_zone = int(h / 3)
            bottom_zone = int(2 * h / 3)

            current_keys = []

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    cx, cy = int(wrist.x * w), int(wrist.y * h)

                    # Draw wrist point
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                    # Determine zone
                    if cy < top_zone:
                        current_keys.append('shift')  # Nitro
                    elif cy > bottom_zone:
                        current_keys.append('s')  # Reverse
                    else:
                        current_keys.append('w')  # Straight

                    if cx < left_zone:
                        current_keys.append('a')  # Left
                    elif cx > right_zone:
                        current_keys.append('d')  # Right
                    # else no left/right

                    break  # Use only first hand

                # Handle key switching
                if current_keys != last_keys:
                    # Release previous keys
                    for key in last_keys:
                        release_key(key)
                    # Press current keys
                    for _ in range(5):  # Interleaved alternating presses
                        for key in current_keys:
                            press_key(key)
                            time.sleep(0.02)
                            release_key(key)
                            time.sleep(0.02)

                    # Keep pressing keys
                    for key in current_keys:
                        press_key(key)

                    last_keys = current_keys

                # Display action
                action_name = "+".join(current_keys).upper() if current_keys else "None"
                cv2.putText(frame, f"Action: {action_name}", (20, h - 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                print(f"[INFO] Action: {action_name}")

            else:
                for key in last_keys:
                    release_key(key)
                last_keys = []

                cv2.putText(frame, "Action: No Hand", (20, h - 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Draw grid
            cv2.line(frame, (left_zone, 0), (left_zone, h), (255, 255, 255), 1)
            cv2.line(frame, (right_zone, 0), (right_zone, h), (255, 255, 255), 1)
            cv2.line(frame, (0, top_zone), (w, top_zone), (255, 255, 255), 1)
            cv2.line(frame, (0, bottom_zone), (w, bottom_zone), (255, 255, 255), 1)

            # Show frame
            cv2.imshow("RaceAssist - 3x3 Motion Grid", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    for key in last_keys:
        release_key(key)
    cap.release()
    cv2.destroyAllWindows()


# Run
if __name__ == "__main__":
    game()
