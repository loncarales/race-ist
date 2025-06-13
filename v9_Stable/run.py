import cv2
import mediapipe as mp
import pyautogui
import time

# Setup MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Keyboard controls
def press_key(k): pyautogui.keyDown(k)
def release_key(k): pyautogui.keyUp(k)

def game():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    last_keys = []
    turn_state = {'a': {'active': False, 'cooldown': 0},
                  'd': {'active': False, 'cooldown': 0}}

    with mp_hands.Hands(min_detection_confidence=0.7,
                        min_tracking_confidence=0.7,
                        max_num_hands=2) as hands:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Camera frame not received!")
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            # Define zones
            left_zone = int(w / 3)
            right_zone = int(2 * w / 3)
            top_zone = int(h / 3)
            bottom_zone = int(2 * h / 3)

            current_keys = []

            # Brake mode
            if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
                current_keys = ['space']
                cv2.putText(frame, "BRAKE (Both Hands)", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                turn_state['a']['active'] = False
                turn_state['d']['active'] = False
                turn_state['a']['cooldown'] = 0
                turn_state['d']['cooldown'] = 0

            elif results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    cx, cy = int(wrist.x * w), int(wrist.y * h)

                    # Draw wrist
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                    # Vertical movement
                    if cy < top_zone:
                        current_keys.append('shift')  # Nitro
                    elif cy > bottom_zone:
                        current_keys.append('s')      # Reverse
                    else:
                        current_keys.append('w')      # Straight

                    # Horizontal movement with flicker decay
                    if cx < left_zone:
                        if not turn_state['a']['active'] and turn_state['a']['cooldown'] == 0:
                            current_keys.append('a')
                            turn_state['a']['active'] = True
                            turn_state['a']['cooldown'] = 3
                        else:
                            turn_state['a']['active'] = False
                            if turn_state['a']['cooldown'] > 0:
                                turn_state['a']['cooldown'] -= 1
                    elif cx > right_zone:
                        if not turn_state['d']['active'] and turn_state['d']['cooldown'] == 0:
                            current_keys.append('d')
                            turn_state['d']['active'] = True
                            turn_state['d']['cooldown'] = 3
                        else:
                            turn_state['d']['active'] = False
                            if turn_state['d']['cooldown'] > 0:
                                turn_state['d']['cooldown'] -= 1
                    else:
                        turn_state['a']['active'] = False
                        turn_state['d']['active'] = False
                        turn_state['a']['cooldown'] = 0
                        turn_state['d']['cooldown'] = 0

                    break  # only one hand used unless both = brake

            # === Handle key changes ===
            if current_keys != last_keys:
                for key in last_keys:
                    release_key(key)

                for key in current_keys:
                    press_key(key)

                last_keys = current_keys

            # Action Display
            action_name = "+".join(current_keys).upper() if current_keys else "None"
            cv2.putText(frame, f"Action: {action_name}", (20, h - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            print(f"[INFO] Action: {action_name}")

            # Draw grid lines
            cv2.line(frame, (left_zone, 0), (left_zone, h), (255, 255, 255), 1)
            cv2.line(frame, (right_zone, 0), (right_zone, h), (255, 255, 255), 1)
            cv2.line(frame, (0, top_zone), (w, top_zone), (255, 255, 255), 1)
            cv2.line(frame, (0, bottom_zone), (w, bottom_zone), (255, 255, 255), 1)

            # Labels
            font = cv2.FONT_HERSHEY_SIMPLEX
            fs = 0.6
            color = (0, 255, 0)
            thick = 2
            cv2.putText(frame, "NITRO", (w // 2 - 40, top_zone - 10), font, fs, color, thick)
            cv2.putText(frame, "REVERSE", (w // 2 - 50, bottom_zone + 30), font, fs, color, thick)
            cv2.putText(frame, "LEFT", (left_zone // 2 - 20, h // 2), font, fs, color, thick)
            cv2.putText(frame, "RIGHT", (right_zone + ((w - right_zone) // 2) - 20, h // 2), font, fs, color, thick)
            cv2.putText(frame, "STRAIGHT", (w // 2 - 50, (top_zone + bottom_zone) // 2), font, fs, color, thick)

            cv2.imshow("RaceAssist - Natural Steering Pulse", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    for key in last_keys:
        release_key(key)
    cap.release()
    cv2.destroyAllWindows()

# Run it
if __name__ == "__main__":
    game()
