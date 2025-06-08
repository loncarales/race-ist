import cv2
import mediapipe as mp
import pyautogui
import time

# Controls
def press_key(k): pyautogui.keyDown(k)
def release_key(k): pyautogui.keyUp(k)

# Init
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
font = cv2.FONT_HERSHEY_SIMPLEX

cap = cv2.VideoCapture(0)

# Zones and states
last_action = None
zone_margin = 0.3  # 30% margin for left/right zones
nitro_threshold_y = 0.25  # Top 25% of screen triggers Nitro

with mp_hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.6) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape
        image = frame.copy()
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        # Borders
        left_border = int(zone_margin * width)
        right_border = int((1 - zone_margin) * width)
        top_nitro = int(nitro_threshold_y * height)

        # Draw zones
        cv2.line(image, (left_border, 0), (left_border, height), (255, 0, 0), 2)
        cv2.line(image, (right_border, 0), (right_border, height), (255, 0, 0), 2)
        cv2.line(image, (0, top_nitro), (width, top_nitro), (0, 0, 255), 2)
        cv2.putText(image, "Left", (20, height//2), font, 0.6, (255, 0, 0), 2)
        cv2.putText(image, "Right", (width - 100, height//2), font, 0.6, (255, 0, 0), 2)
        cv2.putText(image, "Nitro", (20, top_nitro - 10), font, 0.6, (0, 0, 255), 2)

        # Wrist logic
        wrist_coords = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                px = mp_drawing._normalized_to_pixel_coordinates(wrist.x, wrist.y, width, height)
                if px:
                    wrist_coords.append(px)

        action = None
        keys_to_press = []

        if len(wrist_coords) == 2:
            x1, y1 = wrist_coords[0]
            x2, y2 = wrist_coords[1]
            xm = (x1 + x2) // 2
            ym = (y1 + y2) // 2

            # Nitro zone (both wrists high)
            if y1 < top_nitro and y2 < top_nitro:
                action = "Nitro"
                keys_to_press = ["shift"]
            elif xm < left_border:
                action = "Left"
                keys_to_press = ["a"]
            elif xm > right_border:
                action = "Right"
                keys_to_press = ["d"]
            else:
                action = "Straight"
                keys_to_press = ["w"]

        elif len(wrist_coords) == 1:
            action = "Reverse"
            keys_to_press = ["s"]
        else:
            action = "None"

        # If action changed, update keypresses
        if action != last_action:
            print(f"➡️ Action: {action}")
            for k in ['w', 'a', 's', 'd', 'shift']:
                release_key(k)
            for k in keys_to_press:
                press_key(k)
            last_action = action

        # HUD
        cv2.putText(image, f"Action: {action}", (50, 50), font, 0.8, (0, 255, 0), 2)

        cv2.imshow("RaceAssist Steering", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
