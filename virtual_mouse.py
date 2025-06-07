import cv2
import mediapipe as mp
import pyautogui
import math
import webbrowser
import os

# Initialize mediapipe hands module
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize pyautogui
pyautogui.FAILSAFE = False

# Initialize camera
print("Attempting to open camera...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()
else:
    print("Camera opened successfully.")

cv2.namedWindow('Hand Tracking', cv2.WINDOW_NORMAL)

# Initialize variables for storing previous thumb tip position
prev_thumb_x = 0
prev_thumb_y = 0

# Initialize variable for storing previous distance between hands
prev_hand_distance = 0

# Main loop to capture frames from the camera
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read frame.")
            continue

        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)

        # Convert the BGR image to RGB.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame to get hand landmarks
        results = hands.process(rgb_frame)

        # Draw the hand landmarks on the frame.
        if results.multi_hand_landmarks:
            hand_centers = []
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    rgb_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

                # Get coordinates of thumb tip
                thumb_tip = (
                    int(hand_landmarks.landmark[4].x * frame.shape[1]),
                    int(hand_landmarks.landmark[4].y * frame.shape[0]),
                )

                # Calculate displacement of thumb tip position
                thumb_dx = thumb_tip[0] - prev_thumb_x
                thumb_dy = thumb_tip[1] - prev_thumb_y

                # Update cursor position based on thumb displacement
                pyautogui.move(thumb_dx, thumb_dy)

                # Store current thumb tip position for next frame
                prev_thumb_x = thumb_tip[0]
                prev_thumb_y = thumb_tip[1]

                # Check for gestures
                # Left-click gesture: Thumb and index finger tips close together
                index_tip = (
                    int(hand_landmarks.landmark[8].x * frame.shape[1]),
                    int(hand_landmarks.landmark[8].y * frame.shape[0]),
                )
                thumb_index_distance = math.sqrt(
                    (thumb_tip[0] - index_tip[0]) ** 2 + (thumb_tip[1] - index_tip[1]) ** 2
                )
                if thumb_index_distance < 30:
                    pyautogui.click()

                # Right-click gesture: Thumb and middle finger tips close together
                middle_tip = (
                    int(hand_landmarks.landmark[12].x * frame.shape[1]),
                    int(hand_landmarks.landmark[12].y * frame.shape[0]),
                )
                thumb_middle_distance = math.sqrt(
                    (thumb_tip[0] - middle_tip[0]) ** 2 + (thumb_tip[1] - middle_tip[1]) ** 2
                )
                if thumb_middle_distance < 30:
                    pyautogui.rightClick()

                # File opening gesture: Thumb and index finger extended, forming a straight line
                if abs(thumb_tip[1] - index_tip[1]) < 30:
                    if not (thumb_index_distance < 30 or thumb_middle_distance < 30):
                        file_path = r"C:\Users\Lenovo\Downloads\archive (1)\Alzheimer_s Dataset\train"
                        if os.path.exists(file_path):
                            os.startfile(file_path)
                        else:
                            print("Error: File not found.")

                # Website opening gesture: Thumbs up (thumb extended up, all other fingers closed)
                thumb_up = (
                    hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y and
                    all(
                        math.sqrt(
                            (hand_landmarks.landmark[i].x - hand_landmarks.landmark[0].x) ** 2 +
                            (hand_landmarks.landmark[i].y - hand_landmarks.landmark[0].y) ** 2
                        ) < 0.1
                        for i in [5, 8, 12, 16, 20]
                    )
                )
                if thumb_up:
                    website_url = "https://medlineplus.gov/healthcheckup.html"
                    webbrowser.open(website_url)

                # Add the current hand center to the list if the hand is open
                if abs(index_tip[1] - little_tip[1]) < 100 and abs(index_tip[0] - wrist[0]) > 50:
                    hand_centers.append(
                        (
                            int(
                                sum(landmark.x for landmark in hand_landmarks.landmark)
                                / len(hand_landmarks.landmark)
                                * frame.shape[1]
                            ),
                            int(
                                sum(landmark.y for landmark in hand_landmarks.landmark)
                                / len(hand_landmarks.landmark)
                                * frame.shape[0]
                            ),
                        )
                    )

            if len(hand_centers) == 2:
                left_hand_center, right_hand_center = hand_centers

                # Calculate distance between hands
                hand_distance = math.sqrt(
                    (right_hand_center[0] - left_hand_center[0]) ** 2
                    + (right_hand_center[1] - left_hand_center[1]) ** 2
                )

                # Zoom in/out gesture: Move hands away from or closer to each other
                if prev_hand_distance:
                    if hand_distance > prev_hand_distance + 20:
                        pyautogui.hotkey("ctrl", "+")  # Zoom in
                    elif hand_distance < prev_hand_distance - 20:
                        pyautogui.hotkey("ctrl", "-")  # Zoom out

                prev_hand_distance = hand_distance

        # Display the frame
        cv2.imshow("Hand Tracking", cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR))

        # Check for exit key
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()


