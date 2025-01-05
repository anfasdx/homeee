import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Specify video source (0 for webcam, or use a file path)
video_source = 0  # Change to 'hand-video.mp4' for a video file

# Set window width and height
window_width = 650
window_height = 500

# Initialize video capture
video_capture = cv2.VideoCapture(video_source)
if not video_capture.isOpened():
    print("Error: Unable to access video source.")
    exit()

# Initialize drawing variables
prev_x, prev_y = None, None

# Create a blank canvas
canvas = np.zeros((480, 640, 3), dtype=np.uint8)

# Initialize pen color
pen_color = (0, 255, 0)  # Default to green
color_name = "Green"

def is_finger_raised(landmarks, finger_tip, finger_mcp):
    return landmarks[finger_tip].y < landmarks[finger_mcp].y

def draw_landmarks(frame, hand_landmarks, handedness):
    color = (255, 0, 0) if handedness == 'Right' else (0, 0, 255)
    mp_drawing.draw_landmarks(
        frame,
        hand_landmarks,
        mp_hands.HAND_CONNECTIONS,
        mp_drawing.DrawingSpec(color=color, thickness=2),
        mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=2),
    )

def draw_reset_button(frame):
    cv2.rectangle(frame, (10, 10), (110, 60), (0/255, 51/255, 102/255), -1)
    cv2.putText(frame, 'Reset', (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (194, 157, 200), 2)

def is_reset_button_clicked(x, y):
    return 10 <= x <= 110 and 10 <= y <= 60

def get_pen_color(thumb_tip_y, thumb_mcp_y):
    global color_name
    if thumb_tip_y < thumb_mcp_y - 0.1:
        color_name = "Green"
        return (0, 255, 0)
    elif thumb_tip_y < thumb_mcp_y:
        color_name = "Red"
        return (0, 0, 255)
    elif thumb_tip_y < thumb_mcp_y + 0.1:
        color_name = "Blue"
        return (255, 0, 0)
    else:
        color_name = "White"
        return (255, 255, 255)

with mp_hands.Hands() as hands:
    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Unable to fetch frame.")
            break

        # Flip the frame for a mirrored effect
        frame = cv2.flip(frame, 1)

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame for hand tracking
        results = hands.process(rgb_frame)

        closest_right_hand = None
        min_distance = float('inf')

        # Find the closest right hand
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_label = handedness.classification[0].label
                if hand_label == 'Right':
                    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    distance = index_finger_tip.z
                    if distance < min_distance:
                        min_distance = distance
                        closest_right_hand = hand_landmarks

        # Draw landmarks and hand connections for the closest right hand
        if closest_right_hand:
            draw_landmarks(frame, closest_right_hand, 'Right')

            h, w, _ = frame.shape
            index_finger_tip = closest_right_hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

            if (is_finger_raised(closest_right_hand.landmark, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP) and
                not is_finger_raised(closest_right_hand.landmark, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP) and
                not is_finger_raised(closest_right_hand.landmark, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP) and
                not is_finger_raised(closest_right_hand.landmark, mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP)):
                # Draw a green dot at the index finger tip
                cv2.circle(frame, (cx, cy), 3, pen_color, -1)
                # Draw on the canvas
                if prev_x is not None and prev_y is not None:
                    cv2.line(canvas, (prev_x, prev_y), (cx, cy), pen_color, 3)
                prev_x, prev_y = cx, cy
            else:
                prev_x, prev_y = None, None

        # Combine the frame and canvas
        combined_frame = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)

        # Draw the reset button
        draw_reset_button(combined_frame)

        # Display the current pen color
        cv2.putText(combined_frame, f'Color: {color_name}', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Resize the combined frame
        resized_frame = cv2.resize(combined_frame, (window_width, window_height))

        # Display the frame
        cv2.imshow('Hand Tracking', resized_frame)

        # Check for mouse click
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

        # Check for mouse click to reset canvas
        def mouse_callback(event, x, y, flags, param):
            global canvas
            if event == cv2.EVENT_LBUTTONDOWN:
                if is_reset_button_clicked(x, y):
                    canvas = np.zeros((480, 640, 3), dtype=np.uint8)
        
        cv2.setMouseCallback('Hand Tracking', mouse_callback)

# Release resources and close the display window
video_capture.release()
cv2.destroyAllWindows()
# Initialize variables for dragging
dragging = False
drag_start_x, drag_start_y = None, None
canvas_offset_x, canvas_offset_y = 0, 0

def is_hand_closed(landmarks):
    return all(
        is_finger_raised(landmarks, finger_tip, finger_mcp)
        for finger_tip, finger_mcp in [
            (mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.THUMB_MCP),
            (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP),
            (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP),
            (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_MCP),
            (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_MCP),
        ]
    )

with mp_hands.Hands() as hands:
    while video_capture.isOpened():
        ret, frame =