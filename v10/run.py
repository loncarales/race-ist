import cv2
import mediapipe as mp
import pyautogui
import time
from cvzone.Utils import putTextRect

# === Setup MediaPipe Hands ===
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# === Key Control Helpers ===
def key_down(k):
    pyautogui.keyDown(k)

def key_up(k):
    pyautogui.keyUp(k)

def press_key(k):
    pyautogui.press(k)

# === Main Control Function ===
def game():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    is_w_held = False
    active_keys = set()

    with mp_hands.Hands(min_detection_confidence=0.7,
                        min_tracking_confidence=0.7,
                        max_num_hands=2) as hands:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            # Zone Grid
            left_zone = int(w / 3)
            right_zone = int(2 * w / 3)
            top_zone = int(h / 3)
            bottom_zone = int(2 * h / 3)

            action_text = "None"

            # === Brake: Two Hands ===
            if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
                if is_w_held:
                    key_up('w')
                    is_w_held = False
                press_key('space')
                action_text = "BRAKE (SPACE)"
                active_keys = {'space'}

            # === One Hand Detected ===
            elif results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get wrist position
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                cx, cy = int(wrist.x * w), int(wrist.y * h)
                cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                # Reset non-active keys
                for k in ['a', 'd', 's']:
                    if k in active_keys:
                        key_up(k)
                        active_keys.discard(k)

                # === Forward Zone ===
                if top_zone < cy < bottom_zone:
                    if not is_w_held:
                        key_down('w')
                        is_w_held = True
                    active_keys.add('w')
                    action_text = "HOLD W"

                    # Left / Right based on cx
                    if cx < left_zone:
                        key_down('a')
                        active_keys.add('a')
                        action_text += " + HOLD A"
                    elif cx > right_zone:
                        key_down('d')
                        active_keys.add('d')
                        action_text += " + HOLD D"

                # === Nitro Zone ===
                elif cy < top_zone:
                    if is_w_held:
                        key_up('w')
                        is_w_held = False
                    press_key('shift')
                    active_keys = {'shift'}
                    action_text = "NITRO (SHIFT)"

                # === Reverse Zone ===
                elif cy > bottom_zone:
                    if is_w_held:
                        key_up('w')
                        is_w_held = False
                    key_down('s')
                    active_keys.add('s')
                    action_text = "REVERSE (HOLD S)"

            else:
                # No hand detected
                if is_w_held:
                    key_up('w')
                    is_w_held = False
                for k in ['a', 'd', 's']:
                    if k in active_keys:
                        key_up(k)
                        active_keys.discard(k)
                action_text = "None"

            # === UI Grid Overlay ===
            cv2.line(frame, (left_zone, 0), (left_zone, h), (200, 200, 200), 1)
            cv2.line(frame, (right_zone, 0), (right_zone, h), (200, 200, 200), 1)
            cv2.line(frame, (0, top_zone), (w, top_zone), (200, 200, 200), 1)
            cv2.line(frame, (0, bottom_zone), (w, bottom_zone), (200, 200, 200), 1)

            # Zone Labels
            putTextRect(frame, "NITRO", (w//2 - 40, top_zone - 30), scale=1, thickness=1, colorT=(0, 255, 255))
            putTextRect(frame, "REVERSE", (w//2 - 50, bottom_zone + 10), scale=1, thickness=1, colorT=(0, 255, 255))
            putTextRect(frame, "LEFT", (left_zone//2 - 20, h//2), scale=1, thickness=1, colorT=(255, 255, 0))
            putTextRect(frame, "RIGHT", (right_zone + (w - right_zone)//2 - 40, h//2), scale=1, thickness=1, colorT=(255, 255, 0))
            putTextRect(frame, "STRAIGHT", (w//2 - 55, (top_zone + bottom_zone)//2), scale=1, thickness=1, colorT=(255, 255, 255))

            # Action Info
            putTextRect(frame, f"Action: {action_text}", (10, h - 30), scale=1, thickness=2, colorT=(0, 255, 0))

            # Active Key Display
            y_disp = 40
            for k in ['w', 'a', 'd', 's', 'shift', 'space']:
                color = (0, 255, 0) if k in active_keys else (100, 100, 100)
                putTextRect(frame, f"{k.upper()} {'✓' if k in active_keys else ''}", (10, y_disp), scale=0.8, colorT=color)
                y_disp += 30

            print(f"[INFO] Action: {action_text}")
            cv2.imshow("RaceAssist - Final Control Mode", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Cleanup on Exit
    if is_w_held:
        key_up('w')
    for k in ['a', 'd', 's']:
        key_up(k)
    cap.release()
    cv2.destroyAllWindows()

# Run Main
if __name__ == "__main__":
    game()
# https://pyautogui.readthedocs.io/en/latest/keyboard.html