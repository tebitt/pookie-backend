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
        self.anger = float(baye_result['anger'])
        self.disgust = float(baye_result['disgust'])
        self.fear = float(baye_result['fear'])
        self.happiness = float(baye_result['happiness'])
        self.neutral = float(baye_result['neutral'])
        self.sadness = float(baye_result['sadness'])
        self.surprise = float(baye_result['surprise'])

    def get_decision_tree(self):
        """
        Returns the emotion based on the decision tree.
        """
        sorted_emotions = self.sort_emotions()[0]
        max_emotion = sorted_emotions[0]
        match max_emotion:
            case 'neutral':
                if self.neutral >= 0.477: return 'Random Neutral Eyes (pookie_idle_)'
                elif self.happiness >= self.disgust + self.sadness + self.anger + self.fear: return 'Playful Eyes'
                else: return 'Slightly Happy Eyes'
                
            case 'happy':
                if self.happiness >= 0.5: return 'Random Happy Eyes'
                else: return 'Random Playful Eyes' 

            case 'anger': 
                if self.anger >= 0.42: return 'Listening Eyes'
                elif sorted_emotions[1] == 'happiness' | sorted_emotions[1] == 'neutral': return 'Angry but Playful Eyes'
                elif sorted_emotions[1] == 'sadness': return 'Angry Eyes'
                elif sorted_emotions[1] == 'disgust' | sorted_emotions[1] == 'fear': return 'Listening Eyes'
                else: return 'Neutral Eyes'
                
            case 'sadness':
                if self.sadness >= 0.26: return 'Listening Eyes'
                elif sorted_emotions[1] == 'happiness' | sorted_emotions[1] == 'neutral': return 'Sad but Playful Eyes'
                elif sorted_emotions[1] == 'disgust' | sorted_emotions[1] == 'fear': return 'Sad but Playful Eyes 2'
                elif sorted_emotions[1] == 'anger': return 'Sad, Listening Eyes'
                else: return 'Neutral Eyes'

            case 'disgust'|'fear':
                if self.disgust >= 0.36 | self.fear >= 0.3: return 'Listening Eyes'
                elif sorted_emotions[1] == 'happiness' | sorted_emotions[1] == 'neutral': return 'Listening Eyes 5'
                elif sorted_emotions[1] == 'sadness' | sorted_emotions[1] == 'anger': return 'Listening Eyes 6'
                else: return 'Neutral Eyes'

            case 'surprise':
                if self.surprise >= 0.5: return 'Surprised Eyes'
                elif sorted_emotions[1] == 'happiness' | sorted_emotions[1] == 'neutral': return 'Surprised but Happy Eyes'
                elif self.happiness < self.disgust + self.sadness + self.anger + self.fear: return 'Surprised but อ้อน'
                else: return 'Neutral Eyes'

    def sort_emotions(self):
        """
        Returns the emotion with the highest probability.
        """
        emotions = {
            'anger': self.anger,
            'disgust': self.disgust,
            'fear': self.fear,
            'happiness': self.happiness,
            'neutral': self.neutral,
            'sadness': self.sadness,
            'surprise': self.surprise
        }
        return tuple(sorted(emotions, key=emotions.get, reverse=True))
    
    def handle_robot_behavior(self):
        """
        Controls the robot's eyes, voice, and movement based on the dominant SER emotion.
        """
        decided_emotion = self.get_decision_tree()

        async def execute_actions():
            await self.move_eyes(decided_emotion)  # Wait for eyes to finish moving
            await asyncio.gather(
                self.move(decided_emotion),
            )

        self.speak(decided_emotion)
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

