import cv2
import mediapipe as mp
import platform
import pyautogui

from pynput.mouse import Button
from pynput.keyboard import Key
from pynput import mouse, keyboard

# Platform detection
PLATFORM = platform.system()
print(f"Detected platform: {PLATFORM}")

# ============ 易 Setup ============

# MediaPipe Hands for gesture detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Control instances
mouse_controller = mouse.Controller()
keyboard_controller = keyboard.Controller()

# Screen dimensions for mouse movement
screen_width, screen_height = pyautogui.size()


# ============  Input Functions ============

def left_click():
    """Perform left mouse click using pynput"""
    mouse_controller.click(Button.left)


def press_mouse_button():
    """Press and hold the left mouse button"""
    mouse_controller.press(Button.left)


def release_mouse_button():
    """Release the left mouse button"""
    mouse_controller.release(Button.left)


def move_mouse(x, y):
    """Move the mouse to absolute position"""
    mouse_controller.position = (x, y)


def press_escape():
    """Press the escape key using pynput"""
    keyboard_controller.press(Key.esc)
    keyboard_controller.release(Key.esc)


def check_permissions():
    """Check if accessibility permissions are granted"""
    if PLATFORM == "Darwin":
        print("\n" + "=" * 50)
        print("macOS SETUP REQUIRED:")
        print("=" * 50)
        print("1. Go to System Preferences > Security & Privacy")
        print("2. Click on 'Privacy' tab")
        print("3. Select 'Accessibility' from the left sidebar")
        print("4. Click the lock icon to make changes")
        print("5. Add Terminal (or your Python IDE) to the list")
        print("6. Make sure it's checked/enabled")
        print("7. You may need to restart your application")
        print("=" * 50)

    # Test if we have permission by trying a small action
    try:
        test_pos = mouse_controller.position
        return True
    except Exception as e:
        print(f"❌ Permission issue: {e}")
        return False


# ============  Gesture Recognition Functions ============

def get_finger_positions(hand_landmarks, w, h):
    """Extract finger tip and joint positions"""
    landmarks = {}

    # Thumb
    landmarks['thumb_tip'] = (int(hand_landmarks.landmark[4].x * w),
                              int(hand_landmarks.landmark[4].y * h))
    landmarks['thumb_ip'] = (int(hand_landmarks.landmark[3].x * w),
                             int(hand_landmarks.landmark[3].y * h))

    # Index finger
    landmarks['index_tip'] = (int(hand_landmarks.landmark[8].x * w),
                              int(hand_landmarks.landmark[8].y * h))
    landmarks['index_pip'] = (int(hand_landmarks.landmark[6].x * w),
                              int(hand_landmarks.landmark[6].y * h))

    # Middle finger
    landmarks['middle_tip'] = (int(hand_landmarks.landmark[12].x * w),
                               int(hand_landmarks.landmark[12].y * h))
    landmarks['middle_pip'] = (int(hand_landmarks.landmark[10].x * w),
                               int(hand_landmarks.landmark[10].y * h))

    # Ring finger
    landmarks['ring_tip'] = (int(hand_landmarks.landmark[16].x * w),
                             int(hand_landmarks.landmark[16].y * h))
    landmarks['ring_pip'] = (int(hand_landmarks.landmark[14].x * w),
                             int(hand_landmarks.landmark[14].y * h))

    # Pinky
    landmarks['pinky_tip'] = (int(hand_landmarks.landmark[20].x * w),
                              int(hand_landmarks.landmark[20].y * h))
    landmarks['pinky_pip'] = (int(hand_landmarks.landmark[18].x * w),
                              int(hand_landmarks.landmark[18].y * h))

    # Wrist for reference
    landmarks['wrist'] = (int(hand_landmarks.landmark[0].x * w),
                          int(hand_landmarks.landmark[0].y * h))

    return landmarks


def is_finger_up(tip, pip):
    """Check if finger is extended (tip higher than pip)"""
    return tip[1] < pip[1]


def detect_left_hand_gesture(landmarks):
    """Detect gestures for left hand (click and escape)"""
    fingers_up = []

    # Thumb (for left hand, thumb tip should be RIGHT of thumb ip due to mirroring)
    if landmarks['thumb_tip'][0] > landmarks['thumb_ip'][0]:
        fingers_up.append(1)
    else:
        fingers_up.append(0)

    # Other fingers
    for finger in ['index', 'middle', 'ring', 'pinky']:
        if is_finger_up(landmarks[f'{finger}_tip'], landmarks[f'{finger}_pip']):
            fingers_up.append(1)
        else:
            fingers_up.append(0)

    # Left hand gestures
    if fingers_up == [0, 1, 0, 0, 0]:  # Only index finger up
        return "LEFT_CLICK"
    elif fingers_up == [0, 1, 1, 0, 0]:  # Index and middle finger up
        return "ESCAPE"
    elif fingers_up == [0, 0, 0, 0, 0]:  # Fist
        return "FIST"
    elif fingers_up == [1, 1, 1, 1, 1]:  # Open palm
        return "OPEN_PALM"

    return "UNKNOWN"


def detect_right_hand_gesture(landmarks):
    """Detect gestures for right hand (mouse movement and drag)"""
    fingers_up = []

    # Thumb (for right hand, thumb tip should be LEFT of thumb ip due to mirroring)
    if landmarks['thumb_tip'][0] < landmarks['thumb_ip'][0]:
        fingers_up.append(1)
    else:
        fingers_up.append(0)

    # Other fingers
    for finger in ['index', 'middle', 'ring', 'pinky']:
        if is_finger_up(landmarks[f'{finger}_tip'], landmarks[f'{finger}_pip']):
            fingers_up.append(1)
        else:
            fingers_up.append(0)

    # Right hand gestures with new drag functionality
    if fingers_up == [0, 1, 0, 0, 0]:  # Only index finger up - mouse cursor control
        return "MOUSE_CURSOR"
    elif fingers_up == [0, 1, 1, 0, 0]:  # Index and middle finger up - drag mode
        return "MOUSE_DRAG"
    elif fingers_up == [0, 0, 0, 0, 0]:  # Fist
        return "FIST"
    elif fingers_up == [1, 1, 1, 1, 1]:  # Open palm
        return "OPEN_PALM"

    return "UNKNOWN"


def map_hand_to_screen(hand_x, hand_y, frame_w, frame_h):
    """Map hand position to screen coordinates"""
    # Normalize hand position (0-1)
    norm_x = hand_x / frame_w
    norm_y = hand_y / frame_h

    # Map to screen coordinates
    screen_x = int(norm_x * screen_width)
    screen_y = int(norm_y * screen_height)

    # Clamp to screen bounds
    screen_x = max(0, min(screen_width - 1, screen_x))
    screen_y = max(0, min(screen_height - 1, screen_y))

    return screen_x, screen_y


# ============  Main Function ============

def dual_hand_gesture_controller():
    """Main gesture controller function with dual hand support"""

    # Check permissions
    if not check_permissions():
        print("\nPlease grant accessibility permissions and restart the application.")
        return

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # Width
    cap.set(4, 480)  # Height

    # State management for both hands
    left_hand_state = {
        'last_gesture': None,
        'cooldown': 0,
        'cooldown_frames': 10
    }

    right_hand_state = {
        'last_gesture': None,
        'cooldown': 0,
        'cooldown_frames': 10,  # Shorter cooldown for mouse movement
        'mouse_smoothing': [],  # For smoothing mouse movement
        'is_dragging': False,   # Track if currently dragging
        'drag_start_pos': None  # Starting position for drag
    }

    # Create window
    cv2.namedWindow("Dual Hand Gesture Controller")

    # Start MediaPipe hands with 2 hands
    with mp_hands.Hands(min_detection_confidence=0.7,
                        min_tracking_confidence=0.7,
                        max_num_hands=2) as hands:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Camera frame not received!")
                break

            # Detect if user closed window manually
            if cv2.getWindowProperty("Dual Hand Gesture Controller", cv2.WND_PROP_VISIBLE) < 1:
                print("[INFO] Window closed.")
                break

            frame = cv2.flip(frame, 1)  # Mirror image
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            left_gesture = "NO_HAND"
            right_gesture = "NO_HAND"
            left_action = False
            right_action = False

            # ========== ✋ Hand Detection and Gesture Recognition ==========
            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                      results.multi_handedness):
                    # Determine if this is left or right hand
                    hand_label = handedness.classification[0].label

                    # Draw hand mesh
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Get finger positions
                    landmarks = get_finger_positions(hand_landmarks, w, h)

                    # Color code by hand
                    if hand_label == "Left":
                        # Left hand - blue circles
                        color = (255, 0, 0)  # Blue
                        left_gesture = detect_left_hand_gesture(landmarks)

                        # Visual feedback
                        cv2.circle(frame, landmarks['index_tip'], 8, color, -1)
                        cv2.circle(frame, landmarks['middle_tip'], 8, color, -1)
                        cv2.putText(frame, f"L: {left_gesture}",
                                    (landmarks['wrist'][0] - 50, landmarks['wrist'][1] - 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                    else:  # Right hand
                        # Right hand - green circles (red when dragging)
                        color = (0, 0, 255) if right_hand_state['is_dragging'] else (0, 255, 0)
                        right_gesture = detect_right_hand_gesture(landmarks)

                        # Visual feedback
                        cv2.circle(frame, landmarks['index_tip'], 8, color, -1)
                        cv2.circle(frame, landmarks['middle_tip'], 8, color, -1)
                        cv2.putText(frame, f"R: {right_gesture}",
                                    (landmarks['wrist'][0] - 50, landmarks['wrist'][1] - 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                        # Handle mouse cursor movement
                        if right_gesture == "MOUSE_CURSOR":
                            # Use index finger tip for mouse control
                            screen_x, screen_y = map_hand_to_screen(
                                landmarks['index_tip'][0], landmarks['index_tip'][1], w, h)

                            # Add to smoothing buffer
                            right_hand_state['mouse_smoothing'].append((screen_x, screen_y))
                            if len(right_hand_state['mouse_smoothing']) > 5:
                                right_hand_state['mouse_smoothing'].pop(0)

                            # Calculate smoothed position
                            if len(right_hand_state['mouse_smoothing']) >= 3:
                                avg_x = sum(
                                    pos[0] for pos in right_hand_state['mouse_smoothing']) / len(
                                    right_hand_state['mouse_smoothing'])
                                avg_y = sum(
                                    pos[1] for pos in right_hand_state['mouse_smoothing']) / len(
                                    right_hand_state['mouse_smoothing'])

                                move_mouse(int(avg_x), int(avg_y))
                                right_action = True

                        # Handle drag functionality
                        elif right_gesture == "MOUSE_DRAG":
                            # Use index finger tip for mouse control
                            screen_x, screen_y = map_hand_to_screen(
                                landmarks['index_tip'][0], landmarks['index_tip'][1], w, h)

                            # Add to smoothing buffer
                            right_hand_state['mouse_smoothing'].append((screen_x, screen_y))
                            if len(right_hand_state['mouse_smoothing']) > 5:
                                right_hand_state['mouse_smoothing'].pop(0)

                            # Calculate smoothed position
                            if len(right_hand_state['mouse_smoothing']) >= 3:
                                avg_x = sum(
                                    pos[0] for pos in right_hand_state['mouse_smoothing']) / len(
                                    right_hand_state['mouse_smoothing'])
                                avg_y = sum(
                                    pos[1] for pos in right_hand_state['mouse_smoothing']) / len(
                                    right_hand_state['mouse_smoothing'])

                                # Start dragging if not already dragging
                                if not right_hand_state['is_dragging']:
                                    press_mouse_button()
                                    right_hand_state['is_dragging'] = True
                                    right_hand_state['drag_start_pos'] = (int(avg_x), int(avg_y))
                                    print("[RIGHT HAND] Started dragging")

                                # Move mouse while dragging
                                move_mouse(int(avg_x), int(avg_y))
                                right_action = True

            # Check if we need to stop dragging (no drag gesture detected)
            if right_gesture != "MOUSE_DRAG" and right_hand_state['is_dragging']:
                release_mouse_button()
                right_hand_state['is_dragging'] = False
                right_hand_state['drag_start_pos'] = None
                print("[RIGHT HAND] Stopped dragging")

            # ==========  Action Execution ==========

            # Handle left hand actions
            if left_hand_state['cooldown'] > 0:
                left_hand_state['cooldown'] -= 1

            if left_gesture != left_hand_state['last_gesture'] and left_hand_state[
                'cooldown'] == 0:
                try:
                    if left_gesture == "LEFT_CLICK":
                        left_click()
                        left_action = True
                        left_hand_state['cooldown'] = left_hand_state['cooldown_frames']
                        print("[LEFT HAND] Left Click Performed")

                    elif left_gesture == "ESCAPE":
                        press_escape()
                        left_action = True
                        left_hand_state['cooldown'] = left_hand_state['cooldown_frames']
                        print("[LEFT HAND] Escape Key Pressed")

                except Exception as e:
                    print(f"[ERROR] Left hand action failed: {e}")

                left_hand_state['last_gesture'] = left_gesture

            # ========== ️ Visual Feedback ==========

            # Display current gestures
            left_color = (0, 255, 0) if left_action else (255, 255, 255)
            right_color = (0, 255, 0) if right_action else (255, 255, 255)

            cv2.putText(frame, f"Left Hand: {left_gesture}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, left_color, 2)
            cv2.putText(frame, f"Right Hand: {right_gesture}", (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, right_color, 2)

            # Display drag status
            if right_hand_state['is_dragging']:
                cv2.putText(frame, "DRAGGING ACTIVE", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # Display platform info
            cv2.putText(frame, f"Platform: {PLATFORM}", (20, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

            # Display cooldowns
            if left_hand_state['cooldown'] > 0:
                cv2.putText(frame, f"Left Cooldown: {left_hand_state['cooldown']}", (20, 160),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

            if right_hand_state['cooldown'] > 0:
                cv2.putText(frame, f"Right Cooldown: {right_hand_state['cooldown']}", (20, 180),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

            # Instructions
            instructions = [
                "LEFT HAND (Blue):",
                "  INDEX = Left Click",
                "  PEACE = Escape",
                "",
                "RIGHT HAND (Green/Red):",
                "  INDEX = Mouse Cursor",
                "  PEACE = Drag Mode",
				"",
                "Press 'q' to quit"
            ]

            for i, instruction in enumerate(instructions):
                cv2.putText(frame, instruction, (20, h - 280 + i * 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Developer label
            cv2.putText(frame, "Dual Hand Gesture Controller v4.1 - Drag Mode", (10, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Action feedback
            if left_action or right_action:
                cv2.putText(frame, "ACTION EXECUTED!", (w // 2 - 100, h // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            # Show current mouse position for debugging
            current_mouse_pos = mouse_controller.position
            cv2.putText(frame, f"Mouse: {current_mouse_pos}", (w - 200, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Show drag start position if dragging
            if right_hand_state['is_dragging'] and right_hand_state['drag_start_pos']:
                cv2.putText(frame, f"Drag Start: {right_hand_state['drag_start_pos']}", (w - 200, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

            # ========== ️ Show Window ==========
            cv2.imshow("Dual Hand Gesture Controller", frame)

            # Manual exit shortcut
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Cleanup - make sure to release mouse button if still dragging
    if right_hand_state['is_dragging']:
        release_mouse_button()

    cap.release()
    cv2.destroyAllWindows()


# ==========  Run Controller ==========
if __name__ == "__main__":
    print("Starting Dual Hand Gesture Controller...")
    print(f"Platform: {PLATFORM}")
    print(f"Screen Resolution: {screen_width}x{screen_height}")

    print("\n️  LEFT HAND GESTURES (Blue):")
    print("- Point with INDEX finger = Left Click")
    print("- Peace sign (INDEX + MIDDLE) = Escape")

    print("\n️  RIGHT HAND GESTURES (Green/Red):")
    print("- Point with INDEX finger = Mouse Cursor Control")
    print("- Peace sign (INDEX + MIDDLE) = Drag Mode (hold left click + move)")

    print("\n- Press 'q' to quit")
    print("- Use both hands simultaneously for full control!")
    print("- Right hand turns RED when dragging is active")
    print("\nReady to use!")

    try:
        dual_hand_gesture_controller()
    except Exception as e:
        print(f"Error: {e}")
        if PLATFORM == "Darwin":
            print("\nIf you see permission errors, make sure to:")
            print("1. Go to System Preferences > Security & Privacy > Privacy")
            print("2. Select 'Accessibility' and add your Terminal/IDE")
            print("3. Restart the application")
