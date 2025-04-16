import cv2
import mediapipe as mp
import math
import numpy as np
import time
import asyncio
import aiohttp
import warnings
warnings.simplefilter("ignore", UserWarning)

import torch
import torch.nn 
import torch.nn.functional 
from PIL import Image
from torchvision import transforms
from handler import Handler
from rate_limiter import RateLimiter
import os, glob

from cv_models import Bottleneck, ResNet, LSTMPyTorch
from dotenv import load_dotenv
import pvporcupine
import pyaudio
import struct 

load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__)) + '/.env')

ACCESS_KEY = os.getenv("ACCESS_KEY")
KEYWORD_FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/models/hello-poo-kie_en_raspberry-pi_v3_0_0.ppn'
FRAME_LENGTH = 512
CHANNELS = 1
SAMPLE_RATE = 16000
FORMAT = pyaudio.paInt16


FER_DICT_EMO = {"neutral": 0, "anger": 1, "happiness": 2, "sadness": 3, "disgust": 4, "fear": 5, "surprise": 6}
SER_DICT_EMO = {"neutral": 0, "anger": 1, "happiness": 2, "sadness": 3, "frustration": 4}
EMOTION_TABLE = {"neutral": "", "anger": "", "happiness": "", "sadness": "", "disgust": "", "fear": "", "surprise": ""}
BAYE_EMOTION = {"neutral": 0, "anger": 0, "happiness": 0, "sadness": 0, "disgust": 0, "fear": 0, "surprise": 0}

NODE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/bn"

csv_list = glob.glob(NODE_DIR + "/*.csv")

for csv in csv_list:
    with open(csv, 'r') as f:
        table = [line.split(',') for line in f]
        table = tuple([tuple(float(x.strip()) for x in line) for line in table])
        EMOTION_TABLE[csv[len(NODE_DIR) + 1:-4]] = table

SER_SERVER_URL = 'http://127.0.0.1:8080'

def ResNet50(num_classes, channels=3):
    return ResNet(Bottleneck, [3,4,6,3], num_classes, channels)

def pth_processing(fp):
    class PreprocessInput(torch.nn.Module):
        def init(self):
            super(PreprocessInput, self).init()

        def forward(self, x):
            x = x.to(torch.float32)
            x = torch.flip(x, dims=(0,))
            x[0, :, :] -= 91.4953
            x[1, :, :] -= 103.8827
            x[2, :, :] -= 131.0912
            return x

    def get_img_torch(img):
        ttransform = transforms.Compose([
            transforms.PILToTensor(),
            PreprocessInput()
        ])
        img = img.resize((224, 224), Image.Resampling.NEAREST)
        img = ttransform(img)
        img = torch.unsqueeze(img, 0)
        return img
    return get_img_torch(fp)

def norm_coordinates(normalized_x, normalized_y, image_width, image_height):
    x_px = min(math.floor(normalized_x * image_width), image_width - 1)
    y_px = min(math.floor(normalized_y * image_height), image_height - 1)
    return x_px, y_px

def get_box(fl, w, h):
    idx_to_coors = {}
    for idx, landmark in enumerate(fl.landmark):
        landmark_px = norm_coordinates(landmark.x, landmark.y, w, h)
        if landmark_px:
            idx_to_coors[idx] = landmark_px

    x_min = np.min(np.asarray(list(idx_to_coors.values()))[:,0])
    y_min = np.min(np.asarray(list(idx_to_coors.values()))[:,1])
    endX = np.max(np.asarray(list(idx_to_coors.values()))[:,0])
    endY = np.max(np.asarray(list(idx_to_coors.values()))[:,1])

    (startX, startY) = (max(0, x_min), max(0, y_min))
    (endX, endY) = (min(w - 1, endX), min(h - 1, endY))
    
    return startX, startY, endX, endY

def display_EMO_PRED(img, box, label='', color=(128, 128, 128), txt_color=(255, 255, 255), line_width=2):
    lw = line_width or max(round(sum(img.shape) / 2 * 0.003), 2)
    text2_color = (255, 0, 255)
    p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
    cv2.rectangle(img, p1, p2, text2_color, thickness=lw, lineType=cv2.LINE_AA)
    font = cv2.FONT_HERSHEY_SIMPLEX

    tf = max(lw - 1, 1)
    text_fond = (0, 0, 0)
    text_width_2, text_height_2 = cv2.getTextSize(label, font, lw / 3, tf)
    text_width_2 = text_width_2[0] + round(((p2[0] - p1[0]) * 10) / 360)
    center_face = p1[0] + round((p2[0] - p1[0]) / 2)

    cv2.putText(img, label,
                (center_face - round(text_width_2 / 2), p1[1] - round(((p2[0] - p1[0]) * 20) / 360)), font,
                lw / 3, text_fond, thickness=tf, lineType=cv2.LINE_AA)
    cv2.putText(img, label,
                (center_face - round(text_width_2 / 2), p1[1] - round(((p2[0] - p1[0]) * 20) / 360)), font,
                lw / 3, text2_color, thickness=tf, lineType=cv2.LINE_AA)
    return img

def display_FPS(img, text, margin=1.0, box_scale=1.0):
    img_h, img_w, _ = img.shape
    line_width = int(min(img_h, img_w) * 0.001)
    thickness = max(int(line_width / 3), 1)

    font_face = cv2.FONT_HERSHEY_SIMPLEX
    font_color = (0, 0, 0)
    font_scale = thickness / 1.5

    t_w, t_h = cv2.getTextSize(text, font_face, font_scale, None)[0]

    margin_n = int(t_h * margin)
    sub_img = img[0 + margin_n: 0 + margin_n + t_h + int(2 * t_h * box_scale),
              img_w - t_w - margin_n - int(2 * t_h * box_scale): img_w - margin_n]

    white_rect = np.ones(sub_img.shape, dtype=np.uint8) * 255

    img[0 + margin_n: 0 + margin_n + t_h + int(2 * t_h * box_scale),
    img_w - t_w - margin_n - int(2 * t_h * box_scale):img_w - margin_n] = cv2.addWeighted(sub_img, 0.5, white_rect, .5, 1.0)

    cv2.putText(img=img,
                text=text,
                org=(img_w - t_w - margin_n - int(2 * t_h * box_scale) // 2,
                     0 + margin_n + t_h + int(2 * t_h * box_scale) // 2),
                fontFace=font_face,
                fontScale=font_scale,
                color=font_color,
                thickness=thickness,
                lineType=cv2.LINE_AA,
                bottomLeftOrigin=False)
    return img

async def get_ser_prediction(session, rate_limiter):
    try:
        # Try to acquire permission to make a request
        if await rate_limiter.acquire():
            async with session.get(f"{SER_SERVER_URL}/get_latest_prediction") as response:
                if response.status == 200:
                    prediction_result = await response.json()
                    return prediction_result, None
        # Return remaining time until next request
        return None, rate_limiter.time_until_next_request()
    except Exception as e:
        print(f"Error getting SER prediction: {str(e)}")
        return None, None

async def main():
    await asyncio.sleep(1)

    handler = Handler()
    print("Initiating Handler")

    ser_rate_limiter = RateLimiter(interval_seconds=10)
    handler_rate_limiter = RateLimiter(interval_seconds=10)

    name_backbone_model = os.path.dirname(os.path.abspath(__file__)) + '/models/FER_static_ResNet50_AffectNet.pt'
    name_LSTM_model = 'Aff-Wild2'

    # Load models
    print("Loading Models")
    pth_backbone_model = ResNet50(7, channels=3)
    pth_backbone_model.load_state_dict(torch.load(name_backbone_model))
    pth_backbone_model.eval()

    pth_LSTM_model = LSTMPyTorch()
    pth_LSTM_model.load_state_dict(torch.load(os.path.dirname(os.path.abspath(__file__)) + '/models/FER_dinamic_LSTM_{0}.pt'.format(name_LSTM_model)))
    pth_LSTM_model.eval()

    print("Models loaded")
    FER_LABELS = ["neutral", "happiness", "sadness", "surprise", "fear", "disgust", "anger"]
    DICT_EMO = {0: FER_LABELS[0], 1: FER_LABELS[1], 2: FER_LABELS[2], 3: FER_LABELS[3], 4: FER_LABELS[4], 5: FER_LABELS[5], 6: FER_LABELS[6]}
        # Create a Porcupine instance with a custom keyword file
    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[KEYWORD_FILE_PATH]
    )

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open an audio input stream
    stream = audio.open(
        rate=SAMPLE_RATE,
        channels=CHANNELS,
        format=FORMAT,
        input=True,
        frames_per_buffer=FRAME_LENGTH
    )
    
    async with aiohttp.ClientSession() as session:
        print("Starting capture")
        cap = cv2.VideoCapture(0)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = np.round(cap.get(cv2.CAP_PROP_FPS))
        lstm_features = []
        last_ser_prediction = {'prediction': {'name': 'temp'}}

        with mp.solutions.face_mesh.FaceMesh(min_detection_confidence=0.5) as face_mesh:
            while cap.isOpened():
                t1 = time.time()
                _, frame = cap.read()
                if frame is None:
                    break

                frame_copy = frame.copy()
                frame_copy.flags.writeable = False
                frame_copy = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(frame_copy)
                frame_copy.flags.writeable = True

                if results.multi_face_landmarks:
                    for fl in results.multi_face_landmarks:
                        handler_limit_bool = await handler_rate_limiter.acquire() 
                        startX, startY, endX, endY = get_box(fl, w, h)
                        cur_face = frame_copy[startY:endY, startX:endX]

                        cur_face = pth_processing(Image.fromarray(cur_face))
                        features = torch.nn.functional.relu(pth_backbone_model.extract_features(cur_face)).detach().numpy()

                        if len(lstm_features) == 0:
                            lstm_features = [features] * 10
                        else:
                            lstm_features = lstm_features[1:] + [features]

                        lstm_f = torch.from_numpy(np.vstack(lstm_features))
                        lstm_f = torch.unsqueeze(lstm_f, 0)
                        output = pth_LSTM_model(lstm_f).detach().numpy()

                        cl = np.argmax(output)
                        label = DICT_EMO[cl]
                        frame = display_EMO_PRED(frame, (startX, startY, endX, endY), 
                                               label + ' {0:.1%}'.format(output[0][cl]), 
                                               line_width=3)

                        # Get SER prediction with rate limiting
                        ser_prediction, wait_time = await get_ser_prediction(session, ser_rate_limiter)
                        if ser_prediction:
                            if ser_prediction['prediction'] is not None:
                                if ser_prediction['prediction'] == 'DNC':
                                    print('No SER prediction available')
                                    last_ser_prediction = {'prediction': {'name': 'temp'}}
                                elif last_ser_prediction['prediction']['name'] != ser_prediction['prediction']['name']:
                                    last_ser_prediction = ser_prediction
                        print('ser_prediction:', ser_prediction)
                    
                        # Display the last known SER prediction and waiting time
                        y_position = 30  # Starting y position for text
                        # Display waiting time if rate limited
                        if wait_time is not None and wait_time > 0:
                            wait_text = f"Next prediction in: {wait_time:.1f}s"
                            cv2.putText(frame, wait_text, (10, y_position), cv2.FONT_HERSHEY_SIMPLEX,
                                    1, (255, 165, 0), 2, cv2.LINE_AA)
                        
                        if last_ser_prediction['prediction']['name'] != "temp" and handler_limit_bool:
                            fer_values = output[0]
                            inferred_fer_label = FER_LABELS[max(range(len(fer_values)), key=lambda i: fer_values[i])]
                            inferred_ser_label = max(last_ser_prediction['prediction']['prob'], key=lambda k: float(last_ser_prediction['prediction']['prob'][k]))
                            for emotion in EMOTION_TABLE:
                                BAYE_EMOTION[emotion] = EMOTION_TABLE[emotion][SER_DICT_EMO[inferred_ser_label]][FER_DICT_EMO[inferred_fer_label]]
                                
                            print(BAYE_EMOTION)
                            handler = Handler(BAYE_EMOTION)
                            handler.handle_robot_behavior()
                            handler_limit_bool = False
                        elif last_ser_prediction['prediction']['name'] == "temp" and handler_limit_bool:
                            fer_values = output[0]
                            inferred_fer_label, inferred_fer_prob = FER_LABELS[max(range(len(fer_values)), key=lambda i: fer_values[i])], fer_values[max(range(len(fer_values)), key=lambda i: fer_values[i])]
                            if inferred_fer_prob > 0.6:
                                handler = Handler({"neutral":fer_values[0], "happiness":fer_values[1], "sadness": fer_values[2], "surprise": fer_values[3], "fear": fer_values[4], "disgust": fer_values[5], "anger": fer_values[6]})
                                handler.handle_robot_behavior()
                                handler_limit_bool = False

                t2 = time.time()
                frame = display_FPS(frame, 'FPS: {0:.1f}'.format(1 / (t2 - t1)), box_scale=.5)

                cv2.imshow('Webcam', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                await asyncio.sleep(0.01)

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main())
