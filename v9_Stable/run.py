import cv2
import mediapipe as mp
import pyautogui
import time

# ============ 🧠 Setup ============

# MediaPipe Hands for gesture detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Control keyboard input
def press_key(k): pyautogui.keyDown(k)
def release_key(k): pyautogui.keyUp(k)

# ============ 🎮 Main Function ============

def game():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # Width
    cap.set(4, 480)  # Height

    last_keys = []  # Keys pressed in last frame
    # State machine to add decay logic to turns
    turn_state = {
        'a': {'active': False, 'cooldown': 0},
        'd': {'active': False, 'cooldown': 0}
    }

    # Create window to allow close detection
    cv2.namedWindow("RaceAssist - Natural Steering Pulse")

    # Start MediaPipe hands
    with mp_hands.Hands(min_detection_confidence=0.7,
                        min_tracking_confidence=0.7,
                        max_num_hands=2) as hands:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Camera frame not received!")
                break

            # Detect if user closed window manually
            if cv2.getWindowProperty("RaceAssist - Natural Steering Pulse", cv2.WND_PROP_VISIBLE) < 1:
                print("[INFO] Window closed.")
                break

            frame = cv2.flip(frame, 1)  # Mirror image
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            # Define screen zones: left, right, top, bottom thirds
            left_zone = int(w / 3)
            right_zone = int(2 * w / 3)
            top_zone = int(h / 3)
            bottom_zone = int(2 * h / 3)

            current_keys = []      # Keys to press this frame
            action_text = ""       # What action is being done (to display)

            # ========== ✋ BRAKE Mode (Both hands visible) ==========
            if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
                current_keys = ['space']
                action_text = "BRAKE (Both Hands)"
                turn_state['a']['active'] = False
                turn_state['d']['active'] = False
                turn_state['a']['cooldown'] = 0
                turn_state['d']['cooldown'] = 0

                cv2.putText(frame, action_text, (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

            # ========== ✋ Single Hand Control ==========
            elif results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand mesh
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Get wrist position
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    cx, cy = int(wrist.x * w), int(wrist.y * h)

                    # Visualize wrist point
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                    # 🟢 Vertical Movement Detection
                    if cy < top_zone:
                        current_keys.append('shift')    # Nitro
                    elif cy > bottom_zone:
                        current_keys.append('s')        # Reverse
                    else:
                        current_keys.append('w')        # Straight

                    # 🔄 Horizontal Movement + Turn Flicker Handling
                    if cx < left_zone:
                        if not turn_state['a']['active'] and turn_state['a']['cooldown'] == 0:
                            current_keys.append('a')
                            turn_state['a']['active'] = True
                            turn_state['a']['cooldown'] = 3
                            action_text = "W + A [Flicker]"
                        else:
                            turn_state['a']['active'] = False
                            if turn_state['a']['cooldown'] > 0:
                                turn_state['a']['cooldown'] -= 1
                            action_text = "W"
                    elif cx > right_zone:
                        if not turn_state['d']['active'] and turn_state['d']['cooldown'] == 0:
                            current_keys.append('d')
                            turn_state['d']['active'] = True
                            turn_state['d']['cooldown'] = 3
                            action_text = "W + D [Flicker]"
                        else:
                            turn_state['d']['active'] = False
                            if turn_state['d']['cooldown'] > 0:
                                turn_state['d']['cooldown'] -= 1
                            action_text = "W"
                    else:
                        # Center zone – reset turning
                        turn_state['a']['active'] = False
                        turn_state['d']['active'] = False
                        turn_state['a']['cooldown'] = 0
                        turn_state['d']['cooldown'] = 0
                        action_text = "W"

                    break  # Only 1 hand considered unless both = brake

            # ========== ⌨️ Handle Keyboard Input ==========
            if current_keys != last_keys:
                for key in last_keys:
                    release_key(key)
                for key in current_keys:
                    press_key(key)
                last_keys = current_keys

            # ========== 🪧 On-screen Action Display ==========
            if not action_text:
                action_text = "+".join(current_keys).upper() if current_keys else "None"

            cv2.putText(frame, f"Action: {action_text}", (20, h - 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            print(f"[INFO] Action: {action_text}")

            # ========== 📐 Grid Lines & Labels ==========
            cv2.line(frame, (left_zone, 0), (left_zone, h), (255, 255, 255), 1)
            cv2.line(frame, (right_zone, 0), (right_zone, h), (255, 255, 255), 1)
            cv2.line(frame, (0, top_zone), (w, top_zone), (255, 255, 255), 1)
            cv2.line(frame, (0, bottom_zone), (w, bottom_zone), (255, 255, 255), 1)

            # Zone Labels
            font = cv2.FONT_HERSHEY_SIMPLEX
            fs = 0.6
            color = (0, 255, 0)
            thick = 2
            cv2.putText(frame, "NITRO", (w // 2 - 40, top_zone - 10), font, fs, color, thick)
            cv2.putText(frame, "REVERSE", (w // 2 - 50, bottom_zone + 30), font, fs, color, thick)
            cv2.putText(frame, "LEFT", (left_zone // 2 - 20, h // 2), font, fs, color, thick)
            cv2.putText(frame, "RIGHT", (right_zone + ((w - right_zone) // 2) - 20, h // 2), font, fs, color, thick)
            cv2.putText(frame, "STRAIGHT", (w // 2 - 50, (top_zone + bottom_zone) // 2), font, fs, color, thick)

            # 🧩 Developer Label
            cv2.putText(frame, "RaceAssist By KintsugiDev.Studio", (10, h - 20),
                        font, 0.55, (255, 255, 255), 2)

            # ========== 🖼️ Show Window ==========
            cv2.imshow("RaceAssist - Natural Steering Pulse", frame)

            # Manual exit shortcut
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Cleanup
    for key in last_keys:
        release_key(key)
    cap.release()
    cv2.destroyAllWindows()

# ========== 🚀 Run Game Loop ==========
if __name__ == "__main__":
    game()
