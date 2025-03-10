import os
import platform
import pyautogui

def execute_command(command):
    system = platform.system()
    
    if "lumos" in command or "increase brightness" in command:
        if system == "Windows":
            os.system("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,100)")
        elif system == "Linux":
            os.system("xrandr --output eDP-1 --brightness 1.0")  # Adjust eDP-1 if needed
        print("💡 Brightness increased.")

    elif "nox" in command or "decrease brightness" in command:
        if system == "Windows":
            os.system("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,50)")
        elif system == "Linux":
            os.system("xrandr --output eDP-1 --brightness 0.5")
        print("🌙 Brightness decreased.")

    elif "open camera" in command:
        os.system("start microsoft.windows.camera:")
        print("📸 Camera opened.")

    elif "shutdown" in command:
        os.system("shutdown /s /t 10")  # 10-second delay
        print("⚠️ Shutting down in 10 seconds...")

    elif "cancel shutdown" in command:
        os.system("shutdown /a")
        print("⛔ Shutdown canceled.")

    elif "volume up" in command:
        for _ in range(3):  # Increase volume step-wise
            pyautogui.press("volumeup")
        print("🔊 Volume increased.")

    elif "volume down" in command:
        for _ in range(3):  # Decrease volume step-wise
            pyautogui.press("volumedown")
        print("🔉 Volume decreased.")

    elif "mute" in command:
        pyautogui.press("volumemute")
        print("🔇 Muted.")

    else:
        print("🤷 Command not recognized.")
