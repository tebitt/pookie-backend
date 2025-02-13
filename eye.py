import cv2
import numpy as np
from PIL import Image, ImageSequence

class RoboEyes:
    def __init__(self, screen_size=(1920, 1280), gif_paths=[]):
        self.screen_size = screen_size
        self.canvas = np.zeros((screen_size[1], screen_size[0], 3), dtype=np.uint8)  # Black canvas
        self.window_name = "RoboEyes"
        self.gif_paths = gif_paths
        self.current_gif_index = 0
        self.gif_frames = []
        self.load_gifs()
        cv2.namedWindow(self.window_name)
    
    def load_gifs(self):
        """Load all the GIFs and store the frames as lists."""
        for path in self.gif_paths:
            gif = Image.open(path)
            frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]  # Extract each frame
            self.gif_frames.append(frames)

    def show_frame(self, frame):
        """Convert the PIL frame to a format OpenCV can display."""
        frame_rgb = np.array(frame.convert('RGB'))  # Convert PIL image to RGB numpy array
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for OpenCV
        frame_resized = cv2.resize(frame_bgr, self.screen_size)  # Resize to fit the canvas
        cv2.imshow(self.window_name, frame_resized)

    def run(self):
        """Main loop that handles display and input."""
        while True:
            cv2.imshow(self.window_name, self.canvas)  # Show black canvas initially
            
            key = cv2.waitKey(100)  # Wait for key press every 100ms
            
            # Check key input (adjust keys as per your need, e.g., 'n' for next GIF)
            if key == ord('n'):  # 'n' for next GIF
                self.show_next_gif()
            elif key == ord('q'):  # 'q' for quit
                break
        
        cv2.destroyAllWindows()

    def show_next_gif(self):
        """Cycle through the loaded GIFs and display them."""
        if self.gif_frames:
            gif = self.gif_frames[self.current_gif_index]
            
            for frame in gif:  # Display each frame in the current GIF
                self.show_frame(frame)
                cv2.waitKey(100)  # Adjust the delay between frames as per GIF speed
                
            self.current_gif_index = (self.current_gif_index + 1) % len(self.gif_frames)  # Move to next GIF
        else:
            print("No GIFs loaded.")

# Example usage:
# Paths to the eye GIFs
gif_paths = ["eye1.gif", "eye2.gif", "eye3.gif"]

# Create a RoboEyes instance
robo_eyes = RoboEyes(gif_paths=gif_paths)

# Run the display
robo_eyes.run()
