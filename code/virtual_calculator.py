import cv2
import numpy as np
import mediapipe as mp
import math
import color_panel

# Initialize Mediapipe Hands module for hand tracking
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

myEquation = "" 
pinchActive = False  #Keeps track of whether a pinch gesture is active
calc_position = (600, 100)  #it is the Default position of the calculator on the screen
moving_calc = False 

def get_valid_color():
    color = color_panel.get_selected_color()
    return color if isinstance(color, tuple) and len(color) == 3 else (255, 255, 255)  # Default color is white

input_text_color = get_valid_color()

# the Screen size
screen_width, screen_height = 1400, 750

# Define the size of calculator buttons and their positions & each button is a square of 80x80 pixels
button_size = 80 

# the layout of buttons of the calculator screen
button_list = [
    ('AC', (0, 0)), ('C', (0, 1)), ('%', (0, 2)), ('/', (0, 3)), 
    ('7', (1, 0)), ('8', (1, 1)), ('9', (1, 2)), ('*', (1, 3)), 
    ('4', (2, 0)), ('5', (2, 1)), ('6', (2, 2)), ('-', (2, 3)), 
    ('1', (3, 0)), ('2', (3, 1)), ('3', (3, 2)), ('+', (3, 3)), 
    ('0', (4, 0)), ('.', (4, 1)), ('Clr', (4, 2)), ('=', (4, 3))
]

# is is a function to draw the calculator buttons on the screen
def draw_buttons(img, position):
    x_offset, y_offset = position
    for text, (row, col) in button_list:
        x, y = x_offset + col * button_size, y_offset + row * button_size
        cv2.rectangle(img, (x, y), (x + button_size, y + button_size), (255, 255, 255), -1)
        cv2.rectangle(img, (x, y), (x + button_size, y + button_size), (0, 0, 0), 2)
        cv2.putText(img, text, (x + 20, y + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

# this is a function to detect pinch gestures for clicking buttons and moving the calculator
def detect_pinch_click(landmarks, img):
    global myEquation, pinchActive, calc_position, moving_calc, input_text_color

    # Extract necessary fingertip landmarks
    thumb = landmarks[4]
    index = landmarks[8] 
    ring = landmarks[16] 

    distance_thumb_index = math.dist(thumb, index)
    distance_thumb_ring = math.dist(thumb, ring)

    mid_x, mid_y = (thumb[0] + index[0]) // 2, (thumb[1] + index[1]) // 2

    # the marking of dot on index, thumb and ring finger and line from the thumb to index finger
    cv2.circle(img, (thumb[0], thumb[1]), 10, (255, 0, 255), -1)  
    cv2.circle(img, (index[0], index[1]), 10, (255, 0, 255), -1)  
    cv2.circle(img, (ring[0], ring[1]), 10, (255, 0, 255), -1)  
    cv2.circle(img, (mid_x, mid_y), 12, (0, 255, 255), -1)  
    cv2.line(img, (thumb[0], thumb[1]), (index[0], index[1]), (255, 0, 255), 2)

    # If the thumb and ring fingers are near to pinch, activates the movement of calculator buttons screen
    if distance_thumb_ring < 40 and not pinchActive:
        moving_calc = True
        pinchActive = True

    if moving_calc:
        calc_position = (mid_x - 2 * button_size, mid_y - 2 * button_size)

    # if the thumb and index finger are close to pinch then buttons are pressed 
    if distance_thumb_index < 40 and not pinchActive and not moving_calc:
        x_offset, y_offset = calc_position
        for text, (row, col) in button_list:
            x, y = x_offset + col * button_size, y_offset + row * button_size
            if x < mid_x < x + button_size and y < mid_y < y + button_size:
                if text == 'AC':
                    myEquation = ''  # Clears every input character
                elif text == 'C':
                    myEquation = myEquation[:-1]  # Remove last character of the input
                elif text == '=':
                    try:
                        myEquation = str(eval(myEquation))  # performs the operation and return value
                    except:
                        myEquation = 'Error'
                elif text == '%':
                    myEquation += '/100'  # Convert percentage
                elif text == 'Clr':
                    color_panel.open_color_panel()
                    input_text_color = get_valid_color()
                else:
                    myEquation += text
                pinchActive = True


    if distance_thumb_index > 50 and distance_thumb_ring > 50:
        pinchActive = False
        moving_calc = False

# Opens the webcam
cap = cv2.VideoCapture(0)
cap.set(3, screen_width)
cap.set(4, screen_height)

while cap.isOpened():
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1) 
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb) 

    draw_buttons(img, calc_position)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = [(int(lm.x * img.shape[1]), int(lm.y * img.shape[0])) for lm in hand_landmarks.landmark]
            detect_pinch_click(landmarks, img)

    input_text_color = get_valid_color()

    cv2.putText(img, myEquation, (calc_position[0] + 20, calc_position[1] - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, input_text_color, 3)
    
    cv2.imshow("Virtual Calculator", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
