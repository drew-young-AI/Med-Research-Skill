import ctypes
import time
import sys
import os
from pynput import keyboard
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 全局變數來追蹤狀態
last_p_time = 0
alt_pressed = False
pattern_matched = False
# 從 .env 讀取，優先順序：HOTKEY_STRING > CYCH_PASSWORD > 預設值
output_text = os.getenv("HOTKEY_STRING")
if not output_text:
    output_text = os.getenv("CYCH_PASSWORD", "EatFood`12345")


def set_english_input_layout():
    if sys.platform != "win32":
        return None
    try:
        user32 = ctypes.windll.user32
        current_layout = user32.GetKeyboardLayout(0)
        english_layout = user32.LoadKeyboardLayoutW("00000409", 1)
        if english_layout:
            user32.ActivateKeyboardLayout(english_layout, 0)
            return current_layout
    except Exception as e:
        print(f"[input method] 無法切換至英文: {e}")
    return None


def restore_input_layout(layout):
    if sys.platform != "win32" or not layout:
        return
    try:
        ctypes.windll.user32.ActivateKeyboardLayout(layout, 0)
    except Exception as e:
        print(f"[input method] 無法還原輸入法: {e}")

def on_press(key):
    global last_p_time, alt_pressed, pattern_matched
    
    try:
        if hasattr(key, 'vk') and key.vk is not None:
            print(f"[press] vk={key.vk} alt={alt_pressed}")
        elif hasattr(key, 'char') and key.char:
            print(f"[press] char='{key.char}' alt={alt_pressed}")
        else:
            print(f"[press] {key}")

        if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            alt_pressed = True
            print("  -> alt down")
            return

        is_p_key = False
        if hasattr(key, 'vk') and key.vk == 0x50:
            is_p_key = True
        elif hasattr(key, 'char') and key.char and key.char.lower() == 'p':
            is_p_key = True

        if not is_p_key:
            return

        print("  -> P down")
        if not alt_pressed:
            print("  -> ignore P without Alt")
            return

        current_time = time.time()
        if last_p_time != 0 and current_time - last_p_time < 0.5:
            pattern_matched = True
            print("  -> Alt+P+P detected")
            last_p_time = 0
        else:
            last_p_time = current_time
            print("  -> first P recorded")
    except Exception as e:
        print(f"[error] {e}")

def on_release(key):
    global alt_pressed, last_p_time, pattern_matched
    
    try:
        if hasattr(key, 'vk') and key.vk is not None:
            print(f"[release] vk={key.vk}")
        elif hasattr(key, 'char') and key.char:
            print(f"[release] char='{key.char}'")
        else:
            print(f"[release] {key}")

        if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            print("  -> alt up")
            if pattern_matched:
                previous_layout = set_english_input_layout()
                try:
                    kb_controller = keyboard.Controller()
                    kb_controller.type(output_text)
                    print(f"[{time.strftime('%H:%M:%S')}] typed: {output_text}")
                finally:
                    restore_input_layout(previous_layout)
                pattern_matched = False
            alt_pressed = False
            last_p_time = 0
    except Exception as e:
        print(f"[error] {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        output_text = sys.argv[1]

    print("hotkey started")
    print(f"text: {output_text}")
    print("shortcut: Alt + P + P")
    print("press Ctrl+C to stop")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()