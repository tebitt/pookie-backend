# import pvporcupine
import sounddevice as sd
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__)) + '/.env')

ACCESS_KEY = os.getenv("ACCESS_KEY")
KEYWORD_FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/models/hello-poo-kie_en_linux_v3_0_0.ppn'

FRAME_LENGTH = 512
CHANNELS = 1
SAMPLE_RATE = 44100


# try:
#     porcupine = pvporcupine.create(
#         access_key=ACCESS_KEY,
#         keyword_paths=[KEYWORD_FILE_PATH]
#     )

#     def audio_callback(indata, frames, time, status):
#         if status:
#             print(f"Stream status: {status}")
#         pcm = np.frombuffer(indata, dtype=np.int16)
#         if len(pcm) == FRAME_LENGTH:
#             keyword_index = porcupine.process(pcm)
#             if keyword_index == 0:
#                 print("Detected keyword!")

#     print(f"Listening for the keyword '{KEYWORD_FILE_PATH}'...")

#     with sd.InputStream(
#         samplerate=SAMPLE_RATE,
#         blocksize=FRAME_LENGTH,
#         channels=CHANNELS,
#         dtype='int16',
#         callback=audio_callback
#     ):
#         while True:
#             try:
#                 sd.sleep(1000)
#             except KeyboardInterrupt:
#                 print("Stopping...")
#                 break

# except pvporcupine.PorcupineError as e:
#     print(f"Porcupine error: {e}")
# except Exception as e:
#     print(f"An error occurred: {e}")
# finally:
#     if 'porcupine' in locals():
#         porcupine.delete()
