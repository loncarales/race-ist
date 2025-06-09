import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import threading
import queue
import time

# Globals
frame_queue = queue.Queue(maxsize=1)
coords_lock = threading.Lock()
wrist_coords = []
current_action = "None"
stop_flag = False

# Helper
def release_all_keys():
    for k in ["w", "a", "s", "d", "shift"]:
        pyautogui.keyUp(k)

# Thread 1: Capture webcam frames
def capture_frames():
    global stop_flag
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    while not stop_flag:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            if not frame_queue.full():
                frame_queue.put(frame)
    cap.release()

# Thread 2: Detect hands
def detect_hands():
    global wrist_coords, stop_flag
    mp_hands = mp.solutions.hands
    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2) as hands:
        while not stop_flag:
            if not frame_queue.empty():
                frame = frame_queue.get()
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)

                temp_coords = []
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                        h, w, _ = frame.shape
                        px = mp.solutions.drawing_utils._normalized_to_pixel_coordinates(wrist.x, wrist.y, w, h)
                        if px:
                            temp_coords.append(px)
                
                with coords_lock:
                    wrist_coords = temp_coords

                frame_queue.put(frame)  # Put back for display if needed

# Thread 3: Control logic
def control_action():
    global wrist_coords, current_action, stop_flag
    while not stop_flag:
        time.sleep(0.05)
        action = "None"
        with coords_lock:
            coords = wrist_coords.copy()

        if coords:
            x_vals = [x for x, _ in coords]
            y_vals = [y for _, y in coords]
            w, h = 640, 480
            left_zone = int(w * 0.3)
            right_zone = int(w * 0.7)
            top_zone = int(h * 0.25)
            bottom_zone = int(h * 0.75)

            if all(y < top_zone for y in y_vals):
                action = "Nitro"
                pyautogui.keyDown("shift")
            else:
                pyautogui.keyUp("shift")
                if all(y > bottom_zone for y in y_vals) and len(coords) == 2:
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
            release_all_keys()

        if action != current_action:
            print(f"➡️ Action: {action}")
            current_action = action

# Thread 4: Display frame with overlay
def display_output():
    global stop_flag
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    while not stop_flag:
        if not frame_queue.empty():
            frame = frame_queue.get()
            h, w, _ = frame.shape

            left_zone = int(w * 0.3)
            right_zone = int(w * 0.7)
            top_zone = int(h * 0.25)
            bottom_zone = int(h * 0.75)

            # Draw zones
            cv2.line(frame, (left_zone, 0), (left_zone, h), (255, 0, 0), 2)
            cv2.line(frame, (right_zone, 0), (right_zone, h), (255, 0, 0), 2)
            cv2.line(frame, (0, top_zone), (w, top_zone), (0, 255, 0), 2)
            cv2.line(frame, (0, bottom_zone), (w, bottom_zone), (0, 0, 255), 2)

            # Draw landmarks (optional)
            with coords_lock:
                for x, y in wrist_coords:
                    cv2.circle(frame, (x, y), 8, (0, 255, 255), -1)

            cv2.putText(frame, f"Action: {current_action}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.imshow("RaceAssist Parallel", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_flag = True
                break
    cv2.destroyAllWindows()

# ---------- Run Game Pipeline ---------- #
def game():
    t1 = threading.Thread(target=capture_frames)
    t2 = threading.Thread(target=detect_hands)
    t3 = threading.Thread(target=control_action)
    t4 = threading.Thread(target=display_output)

    t1.start()
    t2.start()dd
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()

if __name__ == "__main__":
    game()
