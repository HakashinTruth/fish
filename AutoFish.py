import mss
import cv2
import numpy as np
import time
import math
import keyboard
import os
import random
import pydirectinput
import pyautogui

# --- SETTINGS ---
CENTER_X, CENTER_Y = 1000, 500  
RADIUS = 200  
CIRCLE_SPEED = 0.25  

SCAN_REGION = {"top": 150, "left": 300, "width": 1200, "height": 700}
BAR_REGION = {'left': 1460, 'top': 136, 'width': 70, 'height': 900}

BOBBER_LOWER = np.array([0, 120, 100])  
BOBBER_UPPER = np.array([10, 255, 255])

# --- GLOBAL ---
running = False
angle = 0
catch_count = 0  

def roblox_click(x, y, hold=0.02):
    pydirectinput.moveTo(x, y)
    pydirectinput.mouseDown()
    time.sleep(hold)
    pydirectinput.mouseUp()

def check_bar_presence():
    with mss.mss() as sct:
        sct_img = sct.grab(BAR_REGION)
        frame = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, dark_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        return cv2.countNonZero(dark_mask) > 2000

def find_bobber_in_water():
    with mss.mss() as sct:
        img = sct.grab(SCAN_REGION)
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, BOBBER_LOWER, BOBBER_UPPER)
        coords = cv2.findNonZero(mask)
        if coords is not None:
            avg_x = int(np.mean(coords[:, :, 0]))
            avg_y = int(np.mean(coords[:, :, 1]))
            return avg_x + SCAN_REGION["left"], avg_y + SCAN_REGION["top"]
    return None

def solve_minigame_loop(should_fail=False):
    global running
    if should_fail:
        print(f"!!! [FAIL MODE] Catch #{catch_count} - Avoiding Bobber !!!")
        pydirectinput.moveTo(50, 50) # Run away from the bar
        # Wait here until the game actually ends
        while running and check_bar_presence():
            time.sleep(0.5)
        print(">>> Minigame failed intentionally. Moving to recast...")
        return # Return to main loop to trigger recast

    print(f">>> Minigame Active! Solve #{catch_count}")
    is_holding = False
    time.sleep(1.2) 
    
    with mss.mss() as sct:
        while running:
            sct_img = sct.grab(BAR_REGION)
            frame = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
            
            if not check_bar_presence():
                print(f"<<< Catch #{catch_count} Finished.")
                pyautogui.mouseUp()
                break

            bobber_mask = cv2.inRange(frame, np.array([150, 150, 150]), np.array([255, 255, 255]))
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            zone_mask = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([180, 255, 255]))

            b_coords = cv2.findNonZero(bobber_mask)
            z_coords = cv2.findNonZero(zone_mask)

            if b_coords is not None and z_coords is not None:
                bobber_y = np.mean(b_coords[:, :, 1])
                zone_y = np.mean(z_coords[:, :, 1])

                if bobber_y < zone_y:
                    if not is_holding:
                        pyautogui.mouseDown()
                        is_holding = True
                else:
                    if is_holding:
                        pyautogui.mouseUp()
                        is_holding = False
            time.sleep(0.01)

def toggle_bot():
    global running
    running = not running
    if not running: pyautogui.mouseUp()
    print(f"BOT STATUS: {'ENABLED' if running else 'DISABLED'}")

keyboard.add_hotkey('[', toggle_bot)
keyboard.add_hotkey(']', lambda: os._exit(0))

print("-" * 30)
print("MASTER ROBLOX FISHER LOADED")
print("-" * 30)

try:
    while True:
        if not running:
            time.sleep(0.1)
            continue

        target = find_bobber_in_water()

        if target is None:
            angle += CIRCLE_SPEED
            sx = int(CENTER_X + (math.cos(angle) * RADIUS))
            sy = int(CENTER_Y + (math.sin(angle) * RADIUS))
            pydirectinput.moveTo(sx, sy)
            time.sleep(0.01)
        else:
            print("Bobber Spotted! Waiting 1s...")
            time.sleep(1.0) # The 1s cooldown you wanted
            
            bx, by = target
            start_time = time.time()
            side = "left"
            game_detected = False

            while running and (time.time() - start_time < 12):
                if check_bar_presence():
                    catch_count += 1
                    game_detected = True
                    
                    fail_this_one = (catch_count % 10 == 0)
                    print(f"\n[BAR DETECTED] Progress: {catch_count}/10")
                    
                    # This runs and waits for the game to end (Success or Fail)
                    solve_minigame_loop(should_fail=fail_this_one)
                    break

                offset = -2 if side == "left" else 2
                roblox_click(bx + offset, by, hold=0.02)
                side = "right" if side == "left" else "left"
                time.sleep(0.05)

            # --- UNIVERSAL RECAST ---
            # This triggers whether you Won or Failed the minigame
            if running and game_detected:
                time.sleep(1.5) 
                print("Recasting...")
                for _ in range(5):
                    roblox_click(1040, 620, hold=0.05); time.sleep(0.2)
                for _ in range(5):
                    roblox_click(1400, 620, hold=0.05); time.sleep(0.2)
                time.sleep(1.0)
                angle = 0

except Exception as e:
    pyautogui.mouseUp()
    print(f"Error: {e}")
    os._exit(0)