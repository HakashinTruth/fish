import pyautogui
import mss
import cv2
import numpy as np
import time
import os
import keyboard

# Left 1460, Top 136, Width 70, Height 1075 - cords for 1080p
BAR_REGION = {'left': 1460, 'top': 136, 'width': 70, 'height': 900} # Height capped at 900 for 1080p safety

is_holding = False 
is_fishing = False 

print("DETECT  FISH")
print("Status: looking for Minigame Bar...")
print(" ']' to EXIT.")

def solve_minigame():
    global is_holding, is_fishing
    
    with mss.mss() as sct:
        while True:
            if keyboard.is_pressed(']'):
                pyautogui.mouseUp()
                os._exit(0) 

            # CAPTURE
            sct_img = sct.grab(BAR_REGION)
            frame = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)

            # DETECTION
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Threshold 50 = very dark. Increase to 70 if it doesn't detect.
            _, dark_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
            dark_pixel_count = cv2.countNonZero(dark_mask)

            # THRESHOLD 
            # Lowered from 10,000 to 2,000 because 1080p has fewer pixels
            if dark_pixel_count > 2000: 
                if not is_fishing:
                    print(f">>> Bar Detected ({dark_pixel_count} px). Waiting 2s...")
                    time.sleep(2) 
                    is_fishing = True
                
                # FISHING LOGIC
                # Bobber Mask (Look for white/light bobber)
                bobber_mask = cv2.inRange(frame, np.array([150, 150, 150]), np.array([255, 255, 255]))
                
                # MASK
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                zone_mask = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([180, 255, 255]))

                b_coords = cv2.findNonZero(bobber_mask)
                z_coords = cv2.findNonZero(zone_mask)

                if b_coords is not None and z_coords is not None:
                    bobber_y = np.mean(b_coords[:, :, 1])
                    zone_y = np.mean(z_coords[:, :, 1])

                    # If bobber is above the zone, then Hold
                    if bobber_y < zone_y:
                        if not is_holding:
                            pyautogui.mouseDown()
                            is_holding = True
                    else:
                        if is_holding:
                            pyautogui.mouseUp()
                            is_holding = False
                
                time.sleep(0.01) 
            
            else:
                if is_fishing:
                    print("<<< Bar Disappeared. Resetting.")
                    pyautogui.mouseUp() 
                    is_holding = False
                    is_fishing = False
                time.sleep(0.1)

try:
    solve_minigame()
except Exception as e:
    pyautogui.mouseUp()
    print(f"Error: {e}")