import cv2
from PIL import Image, ImageSequence
import numpy as np
import pyautogui
import os
import multiprocessing
import threading
import random
from fastapi import FastAPI
import time

app = FastAPI()
IDLE_EMOTIONS = ('pookie_idle_1', 'pookie_idle_2', 'pookie_idle_3', 'pookie_idle_4', 'pookie_neutral_1')

class RoboEyes:
    def __init__(self, screen_size=None, is_neutral=None):
        if screen_size is None:
            screen_size = pyautogui.size()
        self.screen_size = screen_size
        self.canvas = np.zeros((screen_size[1], screen_size[0], 3), dtype=np.uint8)
        self.window_name = "RoboEyes"
        self.current_mood = random.choice(IDLE_EMOTIONS)
        self.gif_frames = {}
        self.load_gifs()
        self.last_mood_time = time.time()  # Track the last time a mood was set
        self.is_neutral = is_neutral  # Shared multiprocessing-safe variable

        cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def load_gifs(self):    
        for filename in os.listdir('assets'):
            if filename.endswith('.gif'):
                file_path = os.path.join('assets', filename)
                gif = Image.open(file_path)
                frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]
                self.gif_frames[filename[:-4]] = frames 

    def show_frame(self, frame):
        frame_rgb = np.array(frame.convert('RGB'))
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        frame_resized = cv2.resize(frame_bgr, self.screen_size)
        cv2.imshow(self.window_name, frame_resized)

    def run(self, fps=1, status_queue=None):
        delay_between_frames = int(1000 / fps)
        while True:
            if status_queue is not None:
                self.update(status_queue, delay_between_frames)
                cv2.waitKey(1)

    def update(self, status_queue, delay_between_frames):
        self.status_queue = status_queue  # Store the queue for access in animate_mood
        cv2.imshow(self.window_name, self.canvas)

        # Check if it's time to revert to neutral
        if time.time() - self.last_mood_time > 5 and not self.is_neutral.value:  # 5 seconds timeout for neutral fallback
            self.current_mood = random.choice([IDLE_EMOTIONS])
            self.is_neutral.value = True

        # Process the latest mood in the queue (only if current mood is neutral)
        if self.is_neutral.value and not status_queue.empty():
            # Clear the queue to ensure only the latest mood is processed
            while not status_queue.empty():
                mood = status_queue.get()
            if mood not in IDLE_EMOTIONS:  # Non-neutral mood detected
                self.current_mood = mood
                self.is_neutral.value = False
                self.last_mood_time = time.time()  # Update the last mood time
        else:
            self.current_mood = random.choice(IDLE_EMOTIONS)

        # Animate the current mood
        self.animate_mood(self.current_mood, delay_between_frames)
            
    def animate_mood(self, mood, delay):
        if mood in self.gif_frames:
            gif = self.gif_frames[mood]
            for frame in gif:
                self.show_frame(frame)
                # Check for new mood in the queue (only if current mood is neutral)
                if self.is_neutral.value and not self.status_queue.empty():
                    new_mood = self.status_queue.get()
                    if new_mood not in IDLE_EMOTIONS:  # Non-neutral mood detected
                        self.current_mood = new_mood
                        self.is_neutral.value = False
                        self.last_mood_time = time.time()  # Update the last mood time
                        self.animate_mood(new_mood, delay)  # Play the new mood immediately
                        return  # Exit the current animation loop
                cv2.waitKey(delay)
        else:
            print(f"No GIF available for mood {mood}")

    def read_current_mood(self):
        return self.current_mood

    def set_current_mood(self, mood):
        self.current_mood = mood

# Global variables to share state between processes
status_queue = multiprocessing.Queue()
is_neutral = multiprocessing.Value('b', True)  # Shared variable to track neutral state
robo_eyes_process = None

@app.get("/set_status")
async def set_status(mood: str):
    global status_queue, robo_eyes_process, is_neutral

    if robo_eyes_process is None:
        return {"message": "RoboEyes process is not running"}

    # Only add to the queue if the current mood is neutral
    if is_neutral.value:
        # Clear the queue to ensure only the latest mood is processed
        while not status_queue.empty():
            status_queue.get()

        # Send the new mood to the RoboEyes process
        status_queue.put(mood)
        return {"message": f"{mood.capitalize()} mode activated"}
    else:
        return {"message": "Cannot set new mood: non-neutral mood is currently playing"}

def run_fastapi():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)

def run_eye_process(status_queue, is_neutral):
    robo_eyes = RoboEyes(is_neutral=is_neutral)
    robo_eyes.run(fps=1, status_queue=status_queue)

if __name__ == "__main__":
    # Create and start the RoboEyes process
    robo_eyes_process = multiprocessing.Process(target=run_eye_process, args=(status_queue, is_neutral))
    robo_eyes_process.start()

    # Run FastAPI server in the main thread
    run_fastapi()