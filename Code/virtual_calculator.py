import cv2
import numpy as np
import mediapipe as mp
import math

# Mediapipe hands are initialised
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.85, min_tracking_confidence=0.85)

# Calculator Variables
myEquation = ""
clickCooldown = 0
pinchActive = False

# Screen Size
screen_width, screen_height = 1250, 700  

# Buttons size and positions
button_size = 80  
start_x = (screen_width // 2) + 50  
start_y = 100  

# The buttons are created here
button_list = [
    ('7', (start_x, start_y)), ('8', (start_x + button_size, start_y)), ('9', (start_x + 2 * button_size, start_y)), ('*', (start_x + 3 * button_size, start_y)),
    ('4', (start_x, start_y + button_size)), ('5', (start_x + button_size, start_y + button_size)), ('6', (start_x + 2 * button_size, start_y + button_size)), ('-', (start_x + 3 * button_size, start_y + button_size)),
    ('1', (start_x, start_y + 2 * button_size)), ('2', (start_x + button_size, start_y + 2 * button_size)), ('3', (start_x + 2 * button_size, start_y + 2 * button_size)), ('+', (start_x + 3 * button_size, start_y + 2 * button_size)),
    ('0', (start_x, start_y + 3 * button_size)), ('/', (start_x + button_size, start_y + 3 * button_size)), ('.', (start_x + 2 * button_size, start_y + 3 * button_size)), ('=', (start_x + 3 * button_size, start_y + 3 * button_size)),
    ('%', (start_x, start_y + 4 * button_size)), ('AC', (start_x + button_size, start_y + 4 * button_size)), ('C', (start_x + 2 * button_size, start_y + 4 * button_size))
]

def draw_buttons(img):
    # Draws the calculator buttons on the screen.
    for text, pos in button_list:
        cv2.rectangle(img, pos, (pos[0] + button_size, pos[1] + button_size), (255, 255, 255), -1)  # White button
        cv2.rectangle(img, pos, (pos[0] + button_size, pos[1] + button_size), (0, 0, 0), 2)  # Border
        cv2.putText(img, text, (pos[0] + 30, pos[1] + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

def detect_pinch_click(landmarks, img):
    # Detects a button click using a pinch gesture.
    global myEquation, clickCooldown, pinchActive

    index_x, index_y = int(landmarks[8][0]), int(landmarks[8][1])
    middle_x, middle_y = int(landmarks[12][0]), int(landmarks[12][1])

    mid_x = (index_x + middle_x) // 2
    mid_y = (index_y + middle_y) // 2

    distance = math.dist([index_x, index_y], [middle_x, middle_y])

    # Draw hand tracking indicators
    cv2.circle(img, (index_x, index_y), 10, (255, 0, 255), -1)  # Purple circle for index fingertip
    cv2.circle(img, (middle_x, middle_y), 10, (255, 0, 255), -1)  # Purple circle for middle fingertip
    cv2.circle(img, (mid_x, mid_y), 12, (0, 255, 255), -1)  # Yellow circle in between
    cv2.line(img, (index_x, index_y), (middle_x, middle_y), (255, 0, 255), 2)  # Line connecting fingers

    if distance < 40 and not pinchActive and clickCooldown == 0:
        for text, pos in button_list:
            x, y = pos
            if x < mid_x < x + button_size and y < mid_y < y + button_size:
                if text == 'AC':
                    myEquation = ''  # Clear all
                elif text == 'C':
                    myEquation = myEquation[:-1]  # Remove last character
                elif text == '=':
                    try:
                        myEquation = str(eval(myEquation))
                    except:
                        myEquation = 'Error'
                elif text == '%':
                    myEquation += '/100'  # Convert % to decimal
                else:
                    myEquation += text
                pinchActive = True  
                clickCooldown = 1  

    if distance > 50:
        pinchActive = False  

cap = cv2.VideoCapture(0)
cap.set(3, screen_width)  
cap.set(4, screen_height)  

while cap.isOpened():
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = cv2.resize(img, (screen_width, screen_height))
    results = hands.process(img_rgb)

    draw_buttons(img)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = [(lm.x * img.shape[1], lm.y * img.shape[0]) for lm in hand_landmarks.landmark]
            detect_pinch_click(landmarks, img)

    if clickCooldown > 0:
        clickCooldown += 1
        if clickCooldown > 10:
            clickCooldown = 0

    cv2.putText(img, myEquation, (screen_width // 4, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    cv2.imshow("Virtual Calculator", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()