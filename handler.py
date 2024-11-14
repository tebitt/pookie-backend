import time
from eye import RoboEyes

class Handler:
    def __init__(self, ser_result=None, fer_result=None, robot_eyes=None):
        self.ser_neutral = 0.0
        self.ser_anger = 0.0
        self.ser_happiness = 0.0
        self.ser_sadness = 0.0
        self.ser_frustration = 0.0

        self.fer_result = fer_result  # Placeholder for FER result, to be added as needed

        # If ser_result is provided, set individual emotion probabilities
        if ser_result:
            self.set_ser_emotions(ser_result)

        self.robot_eyes = robot_eyes

    def set_ser_emotions(self, ser_result):
        """
        Parses the SER result and sets individual emotion probabilities.
        """
        print(ser_result)
        self.ser_neutral = float(ser_result['prediction']['prob'].get("neutral", 0.0))
        self.ser_anger = float(ser_result['prediction']['prob'].get("anger", 0.0))
        self.ser_happiness = float(ser_result['prediction']['prob'].get("happiness", 0.0))
        self.ser_sadness = float(ser_result['prediction']['prob'].get("sadness", 0.0))
        self.ser_frustration = float(ser_result['prediction']['prob'].get("frustration", 0.0))

    def get_dominant_emotion(self):
        """
        Determines the dominant emotion based on the highest probability.
        """
        emotions = {
            "neutral": self.ser_neutral,
            "anger": self.ser_anger,
            "happiness": self.ser_happiness,
            "sadness": self.ser_sadness,
            "frustration": self.ser_frustration,
        }
        dominant_emotion = max(emotions, key=emotions.get)
        print(f"SER Dominant Emotion: {dominant_emotion}")
        return dominant_emotion

    def handle_robot_behavior(self):
        """
        Controls the robot's eyes, voice, and movement based on the dominant SER emotion.
        """
        emotion = self.get_dominant_emotion()
        if emotion == "sadness":
            self.move_eyes("sadness")
            self.speak("I'm here for you.")
            self.move("console")

        elif emotion == "happiness":
            self.move_eyes("happiness")
            self.speak("You seem happy!")
            self.move("dance")

        # Additional behaviors based on other emotions

    def move_eyes(self, expression):
        match expression:
            case "sadness":
                self.robot_eyes.sadness_mode = True
                self.robot_eyes.sadness_start_time = time.time()
            case "happiness":
                self.robot_eyes.happiness_mode = True
                self.robot_eyes.happiness_start_time = time.time()
        

    def speak(self, message):
        print(f"Speaking: {message}")

    def move(self, action):
        print(f"Moving robot: {action}")
