import win32api
import win32con
from time import sleep
import keyboard
from pyautogui import pixel


def mouse_click(coordinate):
    """Using the win32 module for clicks as it offers a significant speed advantage over the pyautogui clicker. Also
    using a small sleep window as clicks sometimes don't register without it."""
    offset = 10

    coordinate = [coordinate[0], coordinate[1] + offset]
    win32api.SetCursorPos(coordinate)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def start():
    mouse_click(start_button)


# Set coordinates for game parameters. We only need to analyze 1 pixel per row since the entire box would be black
#   across the lane. This will give us a significant speed advantage rather than analyzing an entire lane.
start_button = [719, 465]
lane1 = [572, 215]
lane2 = [660, 215]
lane3 = [740, 215]
lane4 = [843, 215]

# Black pixel for tile
target_rgb = [0, 0, 0]

# Buffer time to pull up game window
sleep(3)
start()

# Using elif here to save on processing time as there is never 2 tiles in different lanes simultaneously
while keyboard.is_pressed('q') == False:
    if pixel(lane1[0], lane1[1])[0] == 0:
        mouse_click(lane1)
    elif pixel(lane2[0], lane2[1])[0] == 0:
        mouse_click(lane2)
    elif pixel(lane3[0], lane3[1])[0] == 0:
        mouse_click(lane3)
    elif pixel(lane4[0], lane4[1])[0] == 0:
        mouse_click(lane4)
    else:
        pass
