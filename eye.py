import cv2
import numpy as np
from PIL import Image, ImageSequence
import pyautogui  # Use this to dynamically get the screen size

class RoboEyes:
    def __init__(self, gif_paths=[], screen_size=None):
        if screen_size is None:
            screen_size = pyautogui.size()
        self.screen_size = screen_size
        self.canvas = np.zeros((screen_size[1], screen_size[0], 3), dtype=np.uint8)
        self.window_name = "RoboEyes"
        self.gif_paths = gif_paths
        self.gif_frames = []
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
            cv2.imshow(self.window_name, self.canvas)  # Show black canvas initially
            
            key = cv2.waitKey(100)  # Wait for key press every 100ms
            
            if key == ord('1'):
                self.show_gif(0, delay_between_frames)  # Show first GIF
            elif key == ord('2'):
                self.show_gif(1, delay_between_frames)  # Show second GIF
            elif key == ord('3'):
                self.show_gif(2, delay_between_frames)  # Show third GIF
            elif key == ord('q'):  # 'q' for quit
                break
        
        cv2.destroyAllWindows()

    def show_gif(self, gif_index, delay):
        if gif_index < len(self.gif_frames):
            gif = self.gif_frames[gif_index]
            
            for frame in gif:  
                self.show_frame(frame)
                cv2.waitKey(delay)
        else:
            print(f"No GIF available for index {gif_index}")

# examples
gif_paths = ["assets/pookie_neutral_1.gif", "assets/pookie_neutral_2.gif", "assets/pookie_angry_1.gif"]

robo_eyes = RoboEyes(gif_paths=gif_paths)

robo_eyes.run(fps=4)
