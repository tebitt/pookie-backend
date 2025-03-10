import cv2
import numpy as np
from PIL import Image, ImageSequence
import pyautogui
import os


class RoboEyes:
    def __init__(self, gif_paths=[], screen_size=None):
        if screen_size is None:
            screen_size = pyautogui.size()
        self.screen_size = screen_size
        self.canvas = np.zeros((screen_size[1], screen_size[0], 3), dtype=np.uint8)
        self.window_name = "RoboEyes"
        self.gif_paths = gif_paths
        self.gif_frames = []
        self.current_gif_index = None  # Track the currently playing GIF index
        self.load_gifs()
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

    def load_gifs(self):
        for path in self.gif_paths:
            gif = Image.open(path)
            frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]  # Extract each frame
            self.gif_frames.append(frames)

    def show_frame(self, frame):
        frame_rgb = np.array(frame.convert('RGB'))
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        frame_resized = cv2.resize(frame_bgr, self.screen_size)
        cv2.imshow(self.window_name, frame_resized)

    def run(self, fps=1):
        delay_between_frames = int(1000 / fps)  # Calculate delay in milliseconds
        while True:
            cv2.imshow(self.window_name, self.canvas)

            key = cv2.waitKey(100)  

            if key == ord('1'):
                self.current_gif_index = 0  
            if key == ord('2'):
                self.current_gif_index = 1  
            if key == ord('3'):
                self.current_gif_index = 2  
            if key == ord('q'):  
                break

            if self.current_gif_index is not None:
                self.show_gif(self.current_gif_index, delay_between_frames)

        cv2.destroyAllWindows()

    def show_gif(self, gif_index, delay):
        if gif_index < len(self.gif_frames):
            gif = self.gif_frames[gif_index]
            for frame in gif:
                self.show_frame(frame)
                # Check if a key has been pressed during the GIF display
                if cv2.waitKey(delay) in [ord('1'), ord('2'), ord('3'), ord('q')]:
                    break  # Stop the current GIF and break to check for new input
        else:
            print(f"No GIF available for index {gif_index}")

# examples
gif_paths = ["assets/pookie_neutral_1.gif", "assets/pookie_angry_1.gif", "assets/pookie_angry_2.gif"]

robo_eyes = RoboEyes(gif_paths=gif_paths)

robo_eyes.run(fps=2)
