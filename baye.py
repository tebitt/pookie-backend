import os, glob

FER_DICT_EMO = {"neutral": 0, "anger": 1, "happiness": 2, "sadness": 3, "disgust": 4, "fear": 5, "surprise": 6}
SER_DICT_EMO = {"neutral": 0, "anger": 1, "happiness": 2, "sadness": 3, "frustration": 4}
BAYE_EMOTION = {"neutral": 0, "anger": 0, "happiness": 0, "sadness": 0, "disgust": 0, "fear": 0, "surprise": 0}
EMOTION_TABLE = {"neutral": "", "anger": "", "happiness": "", "sadness": "", "disgust": "", "fear": "", "surprise": ""}
NODE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/bn"

csv_list = glob.glob(NODE_DIR + "/*.csv")

for csv in csv_list:
    with open(csv, 'r') as f:
        table = [line.split(',') for line in f]
        table = tuple([tuple(float(x.strip()) for x in line) for line in table])

        EMOTION_TABLE[csv[31:-4]] = table

inference_res_fer = input("Enter the FER emotion: ")
inference_res_ser = input("Enter the SER emotion: ")

for emotion in EMOTION_TABLE:
    BAYE_EMOTION[emotion] = EMOTION_TABLE[emotion][FER_DICT_EMO[inference_res_fer]][SER_DICT_EMO[inference_res_ser]]

print(BAYE_EMOTION)