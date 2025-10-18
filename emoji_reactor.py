import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

SMILE_THRESHOLD = 0.35
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 720
EMOJI_WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

try:
    figured_emoji = cv2.imread("monkey-figured.png")
    thinking_emoji = cv2.imread("monkey-thinking.png")
    straight_face_emoji = cv2.imread("monkey-straight.png")

    if figured_emoji is None:
        raise FileNotFoundError("monkey-figured.png not found")
    if thinking_emoji is None:
        raise FileNotFoundError("monkey-thinking.png not found")
    if straight_face_emoji is None:
        raise FileNotFoundError("monkey-straight.png not found")

    figured_emoji = cv2.resize(figured_emoji, EMOJI_WINDOW_SIZE)
    thinking_emoji = cv2.resize(thinking_emoji, EMOJI_WINDOW_SIZE)
    straight_face_emoji = cv2.resize(straight_face_emoji, EMOJI_WINDOW_SIZE)
    
except Exception as e:
    print("Error loading emoji images!")
    print(f"Details: {e}")
    print("\nExpected files:")
    print("- monkey-figured.png (figured it out)")
    print("- monkey-thinking.png (thinking pose)")
    print("- monkey-straight.png (straight face)")
    exit()

blank_emoji = np.zeros((EMOJI_WINDOW_SIZE[0], EMOJI_WINDOW_SIZE[1], 3), dtype=np.uint8)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

cv2.namedWindow('Emoji Output', cv2.WINDOW_NORMAL)
cv2.namedWindow('Camera Feed', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Camera Feed', WINDOW_WIDTH, WINDOW_HEIGHT)
cv2.resizeWindow('Emoji Output', WINDOW_WIDTH, WINDOW_HEIGHT)
cv2.moveWindow('Camera Feed', 100, 100)
cv2.moveWindow('Emoji Output', WINDOW_WIDTH + 150, 100)

print("Controls:")
print("  Press 'q' to quit")
print("  Finger near mouth = Thinking")
print("  Smile + Finger above eyes = Figured it out!")
print("  Normal face = Straight face")

with mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5) as face_mesh, \
     mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False

        current_state = "STRAIGHT_FACE"
        is_smiling = False
        
        # Get frame dimensions for denormalizing coordinates
        h, w, _ = frame.shape

        # Check facial expression
        results_face = face_mesh.process(image_rgb)
        nose_y = None
        mouth_y = None
        eye_y = None
        
        if results_face.multi_face_landmarks:
            for face_landmarks in results_face.multi_face_landmarks:
                # Get mouth corners and lips for smile detection
                left_corner = face_landmarks.landmark[291]
                right_corner = face_landmarks.landmark[61]
                upper_lip = face_landmarks.landmark[13]
                lower_lip = face_landmarks.landmark[14]

                mouth_width = ((right_corner.x - left_corner.x)**2 + (right_corner.y - left_corner.y)**2)**0.5
                mouth_height = ((lower_lip.x - upper_lip.x)**2 + (lower_lip.y - upper_lip.y)**2)**0.5
                
                if mouth_width > 0:
                    mouth_aspect_ratio = mouth_height / mouth_width
                    if mouth_aspect_ratio > SMILE_THRESHOLD:
                        is_smiling = True
                
                # Get reference points for finger position tracking
                # Nose tip (landmark 1)
                nose_y = face_landmarks.landmark[1].y
                # Mouth center (landmark 13)
                mouth_y = face_landmarks.landmark[13].y
                # Eye level (average of left and right eye - landmarks 159 and 386)
                left_eye = face_landmarks.landmark[159]
                right_eye = face_landmarks.landmark[386]
                eye_y = (left_eye.y + right_eye.y) / 2

        # Check hand position
        results_hands = hands.process(image_rgb)
        if results_hands.multi_hand_landmarks:
            for hand_landmarks in results_hands.multi_hand_landmarks:
                # Get index finger tip (landmark 8) and wrist (landmark 0)
                index_tip = hand_landmarks.landmark[8]
                wrist = hand_landmarks.landmark[0]
                
                # Draw hand landmarks on camera feed for debugging
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Check if finger is near mouth (within threshold)
                if mouth_y is not None:
                    mouth_distance = abs(index_tip.y - mouth_y)
                    # Also check horizontal distance to mouth center
                    mouth_center_x = 0.5  # Approximate center
                    horizontal_distance = abs(index_tip.x - mouth_center_x)
                    
                    # If finger is near mouth area (within 15% of frame height and reasonable horizontal distance)
                    if mouth_distance < 0.15 and horizontal_distance < 0.25:
                        current_state = "THINKING"
                
                # Check if finger is above eye level and person is smiling
                if eye_y is not None and is_smiling:
                    # If finger is above eye level (y coordinate is smaller)
                    if index_tip.y < eye_y:
                        current_state = "FIGURED"
        
        # If no hand detected but smiling, keep straight face
        # If hand not in special position, check base state
        if current_state == "STRAIGHT_FACE":
            if is_smiling:
                current_state = "STRAIGHT_FACE"  # You can change this if you want smiling without hand to show a different emoji
        
        # Select emoji based on state
        if current_state == "FIGURED":
            emoji_to_display = figured_emoji
            emoji_name = "💡 Figured!"
        elif current_state == "THINKING":
            emoji_to_display = thinking_emoji
            emoji_name = "🤔 Thinking"
        else:  # STRAIGHT_FACE
            emoji_to_display = straight_face_emoji
            emoji_name = "😐 Straight"

        camera_frame_resized = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        cv2.putText(camera_frame_resized, f'STATE: {current_state} {emoji_name}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(camera_frame_resized, f'Smiling: {is_smiling}', (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(camera_frame_resized, 'Press "q" to quit', (10, WINDOW_HEIGHT - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow('Camera Feed', camera_frame_resized)
        cv2.imshow('Emoji Output', emoji_to_display)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
