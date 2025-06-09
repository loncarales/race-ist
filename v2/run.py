import cv2
import mediapipe as mp
import pyautogui

# Key control functions
def press_key(k): pyautogui.keyDown(k)
def release_key(k): pyautogui.keyUp(k)

# Init
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
font = cv2.FONT_HERSHEY_SIMPLEX

cap = cv2.VideoCapture(0)
last_action = None

with mp_hands.Hands(static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.7) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        action = "None"
        keys_to_press = []

        hand_positions = []
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]

                # Estimate fist by checking how close tip is to MCP (simplified)
                dist = abs(index_tip.y - index_mcp.y)
                is_fist = dist < 0.05  # adjust this threshold as needed

                px = mp_drawing._normalized_to_pixel_coordinates(wrist.x, wrist.y, width, height)
                if px and is_fist:
                    hand_positions.append((px[0], px[1]))  # only consider fist hands

        # Draw line if 2 fists detected
        if len(hand_positions) == 2:
            x1, y1 = hand_positions[0]
            x2, y2 = hand_positions[1]
            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 4)

            # Nitro
            if y1 < height * 0.5 and y2 < height * 0.5:
                action = "Nitro"
                keys_to_press = ["shift"]
            # Direction
            elif y1 < y2:
                action = "Right"
                keys_to_press = ["d"]
            elif y2 < y1:
                action = "Left"
                keys_to_press = ["a"]
            else:
                action = "Straight"
                keys_to_press = ["w"]

        elif len(hand_positions) == 1:
            action = "Straight"
            keys_to_press = ["w"]

        else:
            action = "Brake"
            keys_to_press = ["s"]

        # Handle key changes
        if action != last_action:
            print(f"➡️ Action: {action}")
            for k in ['w', 'a', 's', 'd', 'shift']:
                release_key(k)
            for k in keys_to_press:
                press_key(k)
            last_action = action

        # HUD
        cv2.putText(frame, f"Action: {action}", (40, 50), font, 1, (0, 255, 0), 2)
        cv2.imshow("RaceAssist - Fist Steering", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
