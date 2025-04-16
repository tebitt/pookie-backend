import os
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

try:
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

    print(f"Listening for the keyword '{KEYWORD_FILE_PATH}'...")

    while True:
        try:
            # Read audio data from the stream
            audio_chunk = stream.read(FRAME_LENGTH)

            # Convert the audio data to a list of 16-bit integers
            pcm = struct.unpack_from("h" * FRAME_LENGTH, audio_chunk)
            # print(pcm)

            # Process the audio frame with Porcupine
            keyword_index = porcupine.process(pcm)
            if keyword_index == 0:
                print(f"Detected keyword!")
                # Perform action upon keyword detection here
                # For example:
                # print("Hello Cookie detected!")

        except IOError as e:
            print(f"Error reading audio stream: {e}")
        except KeyboardInterrupt:
            print("Stopping...")
            break

except pvporcupine.PorcupineError as e:
    print(f"Porcupine error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'stream' in locals() and stream.is_active():
        stream.stop_stream()
        stream.close()
    if 'audio' in locals():
        audio.terminate()
    if 'porcupine' in locals():
        porcupine.delete()
