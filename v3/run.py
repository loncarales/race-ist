import cv2
import numpy as np
import mediapipe as mp
import pyautogui

# ---------- Main Game Logic ---------- #
def game():
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    last_action = None

    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            wrist_coords = []
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    px = mp_drawing._normalized_to_pixel_coordinates(wrist.x, wrist.y, w, h)
                    if px:
                        wrist_coords.append(px)

            # Zones
            left_zone = int(w * 0.3)
            right_zone = int(w * 0.7)
            top_zone = int(h * 0.25)
            bottom_zone = int(h * 0.75)

            # Draw boundaries
            cv2.line(frame, (left_zone, 0), (left_zone, h), (255, 0, 0), 2)
            cv2.line(frame, (right_zone, 0), (right_zone, h), (255, 0, 0), 2)
            cv2.line(frame, (0, top_zone), (w, top_zone), (0, 255, 0), 2)
            cv2.line(frame, (0, bottom_zone), (w, bottom_zone), (0, 0, 255), 2)

            action = "None"

            def release_all():
                for k in ["w", "a", "s", "d", "shift"]:
                    pyautogui.keyUp(k)

            if len(wrist_coords) >= 1:
                y_vals = [y for _, y in wrist_coords]
                x_vals = [x for x, _ in wrist_coords]

                if all(y < top_zone for y in y_vals):
                    action = "Nitro"
                    pyautogui.keyDown("shift")
                else:
                    pyautogui.keyUp("shift")
                    if all(y > bottom_zone for y in y_vals) and len(wrist_coords) == 2:
                        action = "Reverse"
                        pyautogui.keyDown("s")
                        pyautogui.keyUp("w")
                        pyautogui.keyUp("a")
                        pyautogui.keyUp("d")
                    elif any(x < left_zone for x in x_vals):
                        action = "Left"
                        pyautogui.keyDown("a")
                        pyautogui.keyUp("d")
                    elif any(x > right_zone for x in x_vals):
                        action = "Right"
                        pyautogui.keyDown("d")
                        pyautogui.keyUp("a")
                    else:
                        action = "Straight"
                        pyautogui.keyDown("w")
                        pyautogui.keyUp("a")
                        pyautogui.keyUp("d")
                        pyautogui.keyUp("s")
            else:
                action = "Brake"
                release_all()

            if action != last_action:
                print(f"➡️ Action: {action}")
                last_action = action

            cv2.putText(frame, f"Action: {action}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.imshow("RaceAssist Advanced", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    game()
