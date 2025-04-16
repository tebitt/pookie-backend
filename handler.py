import numpy as np
from pydub import AudioSegment
from pydub.playback import play
import time
import aiohttp
import asyncio
import os
import pygame
import random
import cv2
from adafruit_servokit import ServoKit

motor = ServoKit(channels = 16)

lm = motor.servo[0]
bm = motor.servo[4]
um = motor.servo[8]
rm = motor.servo[12]
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

        print(baye_result)

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

    def decision_tree(self):
        """
        Returns the emotion based on the decision tree.
        """
        sorted_emotions = self.sort_emotions()
        max_emotion = sorted_emotions[0]
        match max_emotion:
            case 'neutral':
                if self.neutral >= 0.477: return 'pookie_neutral_1'
                elif self.happiness >= self.disgust + self.sadness + self.anger + self.fear: 'pookie_slightly_happy'
                else: return 'pookie_playful_1'
                
            case 'happiness':
                if self.happiness >= 0.5: return random.choice(['pookie_slightly_happy', 'pookie_very_happy'])
                else: return random.choice(['pookie_playful_2', 'pookie_playful_3'])

            case 'anger': 
                if self.anger >= 0.42: return 'pookie_listen_1'
                elif sorted_emotions[1] == 'happiness' or sorted_emotions[1] == 'neutral': return 'pookie_angry_1'
                elif sorted_emotions[1] == 'sadness': return 'pookie_angry_2'
                elif sorted_emotions[1] == 'disgust' or sorted_emotions[1] == 'fear': return 'pookie_listen_3'
                else: return 'pookie_neutral_1'
                
            case 'sadness':
                if self.sadness >= 0.26: return 'pookie_listen_2'
                elif sorted_emotions[1] == 'happiness' or sorted_emotions[1] == 'neutral': return 'pookie_sad_1'
                elif sorted_emotions[1] == 'disgust' or sorted_emotions[1] == 'fear': return 'pookie_sad_2'
                elif sorted_emotions[1] == 'anger': return 'pookie_listen_4'
                else: return 'pookie_neutral_1'

            case 'disgust'|'fear':
                if self.disgust >= 0.36 or self.fear >= 0.3: return 'pookie_listen_7'
                elif sorted_emotions[1] == 'happiness' or sorted_emotions[1] == 'neutral': return 'pookie_listen_5'
                elif sorted_emotions[1] == 'sadness' or sorted_emotions[1] == 'anger': return 'pookie_listen_6'
                else: return 'pookie_neutral_1'

            case 'surprise':
                if self.surprise >= 0.5: return 'pookie_surprise_3'
                elif sorted_emotions[1] == 'happiness' or sorted_emotions[1] == 'neutral': return 'pookie_surprise_1'
                elif self.happiness < self.disgust + self.sadness + self.anger + self.fear: return 'pookie_surprise_2'
                else: return 'pookie_neutral_1'

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
        decided_emotion = self.decision_tree()

        async def execute_actions():
            await self.move_eyes(decided_emotion)  # Wait for eyes to finish moving
            await asyncio.gather(
                self.move(decided_emotion),
            )
        
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
        """
        Moves the robot based on the emotion.
        """
        def move(m, angle):
            m.angle = angle

        def base():
            move(rm,180) # decrease angle -> rotates up
            move(lm,120) # increase angle -> rotates up
            move(um,180) #decrease angle -> go left
            move(bm,90)

        def action_1():
            base()
            time.sleep(0.2)
            move(rm,120)
            move(um,120)
            time.sleep(3)
            base()

        def action_2():
            base()
            for i in range(2):
                move(rm,120)
                move(lm,180)
                # move(um,180)
                # move(um,120)
                time.sleep(0.2)
                base()
                time.sleep(0.2)
            base()
        def action_3():
            base()
            for i in range(2):
                move(bm,180)
                move(lm,180)
                move(rm,120)
                time.sleep(0.3)
                move(lm,120)
                move(rm,180)
                time.sleep(0.3)   
                move(bm,60)
                time.sleep(0.3) 
            base()

        def action_6():
            base()
            for i in range(4):
                move(rm,120)
                move(lm,180)
            
                time.sleep(0.3)   

                base()

                time.sleep(0.3)   

        match emotion:
            case 'pookie_neutral_1':
                print("Neutral")
            case 'pookie_slightly_happy':
                print("Slightly happy")
                action_1()
            case 'pookie_very_happy':
                print("Very happy")
                action_3()
            case 'pookie_playful_1':
                action_2()
            case 'pookie_playful_2':
                print("Playful 2")
            case 'pookie_playful_3':
                print("Playful 3")
            case 'pookie_listen_1':
                print("Listen 1")
            case 'pookie_listen_3':
                print("Listen 3")
            case 'pookie_angry_1':
                print("Angry 1")
            case 'pookie_angry_2':
                print("Angry 2")
            case 'pookie_sad_1':
                print("Sad 1")
                action_6()


    async def move_eyes(self, expression):
        EYES_SERVER_URL = f"http://127.0.0.1:8081/set_status?mood={expression}"
        if expression is not None:
            try:
                async with aiohttp.ClientSession() as session:
                        async with session.get(EYES_SERVER_URL) as response:
                            if response.status == 200:
                                print("Eyes moved successfully")
                                self.speak(expression)
                            else:
                                print(f"Failed to move eyes. Status code: {response.status}")
            except Exception as e:
                print(f"Error sending request: {e}")
                return None, None

