import numpy as np
from pydub import AudioSegment
from pydub.playback import play
import aiohttp
import asyncio
import os
import pygame
import cv2

class Handler:
    def __init__(self, baye_result=None):
        self.baye_result = baye_result
        self.anger = 0.0
        self.disgust = 0.0
        self.fear = 0.0
        self.happiness = 0.0
        self.neutral = 0.0
        self.sadness = 0.0
        self.surprise = 0.0

        if baye_result is not None:
            self.set_emotions(baye_result)

    def set_emotions(self, baye_result):
        """
        Parses the FER result and sets individual emotion probabilities.
        """
        self.fer_anger = float(baye_result['anger'])
        self.fer_disgust = float(baye_result['disgust'])
        self.fer_fear = float(baye_result['fear'])
        self.fer_happiness = float(baye_result['happiness'])
        self.fer_neutral = float(baye_result['neutral'])
        self.fer_sadness = float(baye_result['sadness'])
        self.fer_surprise = float(baye_result['surprise'])

    def get_dominant_emotion(self):
        """
        Returns the emotion with the highest probability.
        """
        return max(self.baye_result, key=self.baye_result.get)

    def handle_robot_behavior(self):
        """
        Controls the robot's eyes, voice, and movement based on the dominant SER emotion.
        """
        dominant_emotion = self.get_dominant_emotion()

        async def execute_actions():
            await self.move_eyes(dominant_emotion)  # Wait for eyes to finish moving
            await asyncio.gather(
                self.move(dominant_emotion),
            )

        self.speak(dominant_emotion)
        asyncio.ensure_future(execute_actions())

    def speak(self, emotion):
        current_path = os.getcwd()
        audio_path = os.path.join(current_path, 'audio', f'{emotion}.wav')
        try:
            sound = AudioSegment.from_file(audio_path)
            play(sound)
        except Exception as e:
            print(f"An error occurred while trying to play the audio: {e}")


    async def move(self, emotion):
        DEMO_EXIST = ['neutral', 'sadness', 'happiness']
        if emotion not in DEMO_EXIST:
            emotion = "neutral"

        # Construct the video path
        current_path = os.getcwd()
        video_path = os.path.join(current_path, 'demo', f'{emotion}.mp4')

        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file '{video_path}' not found.")

            # Initialize Pygame
            pygame.init()
            pygame.display.set_caption(f"Playing: {emotion}")

            # Open the video file with OpenCV
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise Exception(f"Unable to open video: {video_path}")

            # Get video dimensions
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Default to 30 FPS if FPS is unavailable

            # Create Pygame window
            screen = pygame.display.set_mode((width, height))

            # Main loop to play video
            clock = pygame.time.Clock()
            while cap.isOpened():
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        cap.release()
                        pygame.quit()
                        return

                ret, frame = cap.read()
                if not ret:
                    break

                # Convert OpenCV frame (BGR) to Pygame surface (RGB)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

                # Display the frame in Pygame
                screen.blit(frame, (0, 0))
                pygame.display.flip()

                # Maintain video frame rate
                clock.tick(fps)

            # Clean up after playback
            cap.release()
            pygame.quit()

        except Exception as e:
            print(f"An error occurred: {e}")


    async def move_eyes(self, expression):
        EYES_SERVER_URL = f"http://127.0.0.1:8081/set_status?mood={expression}"
        try:
             async with aiohttp.ClientSession() as session:
                    async with session.get(EYES_SERVER_URL) as response:
                        if response.status == 200:
                            print("Eyes moved successfully")
                        else:
                            print(f"Failed to move eyes. Status code: {response.status}")
        except Exception as e:
            print(f"Error sending request: {e}")
            return None, None

