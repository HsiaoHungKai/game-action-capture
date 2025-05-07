import mss
import numpy as np
import cv2
import os
from pynput import keyboard
import time

save_dir = "screenshots"
os.makedirs(save_dir, exist_ok=True)

UP_dir = os.path.join(save_dir, "UP")
os.makedirs(UP_dir, exist_ok=True)
DOWN_dir = os.path.join(save_dir, "DOWN")
os.makedirs(DOWN_dir, exist_ok=True)
LEFT_dir = os.path.join(save_dir, "LEFT")
os.makedirs(LEFT_dir, exist_ok=True)
RIGHT_dir = os.path.join(save_dir, "RIGHT")
os.makedirs(RIGHT_dir, exist_ok=True)

monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}

sct_instance = None
current_display_image = np.zeros((100, 100, 3), np.uint8)
screenshot_count = 0
keep_running = True

def handle_screenshot_and_save(key_pressed):
    global sct_instance, current_display_image, screenshot_count, monitor

    if not sct_instance:
        print("Error: Screen capture instance not initialized.")
        return

    screenshot_data = sct_instance.grab(monitor)
    img_to_process = np.array(screenshot_data)
    img_to_process = cv2.cvtColor(img_to_process, cv2.COLOR_BGRA2BGR)
    
    # Resize the image to 224x224
    img_to_process = cv2.resize(img_to_process, (224, 224), interpolation=cv2.INTER_AREA)

    folder_path = ""
    action_name = ""

    if key_pressed == keyboard.Key.up:
        folder_path = UP_dir
        action_name = "UP"
    elif key_pressed == keyboard.Key.down:
        folder_path = DOWN_dir
        action_name = "DOWN"
    elif key_pressed == keyboard.Key.left:
        folder_path = LEFT_dir
        action_name = "LEFT"
    elif key_pressed == keyboard.Key.right:
        folder_path = RIGHT_dir
        action_name = "RIGHT"
    else:
        return

    filename = f"screenshot_{time.time()}_{action_name}.png"
    full_path = os.path.join(folder_path, filename)
    cv2.imwrite(full_path, img_to_process)
    print(f"Saved {action_name} screenshot #{screenshot_count}: {filename}")
    
    current_display_image = img_to_process
    screenshot_count += 1
    
def on_key_press(key):
    global keep_running
    
    if not keep_running:
        return False

    if key in [keyboard.Key.up, keyboard.Key.down, keyboard.Key.left, keyboard.Key.right]:
        handle_screenshot_and_save(key)
    
    try:
        if key.char == 'q':
            print("Quit key 'q' pressed globally. Stopping application...")
            keep_running = False
            return False
    except AttributeError:
        pass
    
    return keep_running

cv2.namedWindow("Screenshot", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Screenshot", 960, 540)

with mss.mss() as sct:
    sct_instance = sct
    screenshot_count = 0
    keep_running = True

    initial_screenshot_data = sct_instance.grab(monitor)
    current_display_image = np.array(initial_screenshot_data)
    current_display_image = cv2.cvtColor(current_display_image, cv2.COLOR_BGRA2BGR)
    
    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()

    while keep_running:
        cv2.imshow("Screenshot", current_display_image)
        
        key_cv = cv2.waitKey(30) & 0xFF
        if key_cv == ord('q'):
            if keep_running:
                keep_running = False
                if listener.is_alive():
                    listener.stop()
            break
        
        if not listener.is_alive() and keep_running:
            keep_running = False 

    if listener.is_alive():
        listener.stop()
    listener.join()

print(f"Successfully captured {screenshot_count} screenshots")
cv2.destroyAllWindows()