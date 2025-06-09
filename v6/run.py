import cv2
import mediapipe as mp
import pyautogui

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Controls
def press_keys(keys):
    for k in keys:
        pyautogui.keyDown(k)

def release_keys(keys):
    for k in keys:
        pyautogui.keyUp(k)

def release_all():
    for k in ["w", "a", "s", "d"]:
        pyautogui.keyUp(k)

def game():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    last_keys = set()

    left_ratio = 0.33
    right_ratio = 0.66
    center_y_ratio = 0.5

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

            # Zones
            left_zone = int(w * left_ratio)
            right_zone = int(w * right_ratio)
            center_x = w // 2
            center_y = int(h * center_y_ratio)

            # Draw guides
            cv2.line(frame, (center_x, 0), (center_x, h), (0, 255, 255), 2)
            cv2.line(frame, (left_zone, center_y), (right_zone, center_y), (0, 255, 0), 2)

            action = "None"
            current_keys = set()

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    cx, cy = int(wrist.x * w), int(wrist.y * h)

                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                    if cx < left_zone:
                        action = "Left + Forward"
                        current_keys = {"a", "w"}
                    elif cx > right_zone:
                        action = "Right + Forward"
                        current_keys = {"d", "w"}
                    else:
                        if cy < center_y:
                            action = "Straight"
                            current_keys = {"w"}
                        else:
                            action = "Reverse"
                            current_keys = {"s"}

                    break
            else:
                action = "No Hand"
                current_keys = set()

            # Key management
            if current_keys != last_keys:
                release_keys(last_keys - current_keys)
                press_keys(current_keys - last_keys)
                last_keys = current_keys

            # Display
            cv2.putText(frame, f"Action: {action}", (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.imshow("RaceAssist - Enhanced Steering", frame)
            print(f"[INFO] Action: {action}")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    release_all()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    game()
