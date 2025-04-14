import time
from datetime import datetime
import os
import subprocess
from pydub import AudioSegment

temp_dir = "/home/orin_nano/pookie-backend/temp"

def _cleanup_old_files():
    files = sorted([f for f in os.listdir(temp_dir) if f.startswith("recorded_audio")])
    for old_file in files[:-1]:
        try:
            os.remove(os.path.join(temp_dir, old_file))
        except:
            pass

while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"{temp_dir}/recorded_audio_{timestamp}.wav"
        audio_length = 5
        # Start recording
        print("Start Recording")

        command = [
            "ffmpeg",
            "-y",
            "-f", "pulse",
            "-i", "default",
            "-t", f"{audio_length}",
            "-ar", "44100",
            "-ac", "2",
            audio_filename
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)  # Wait for recording to complete
        process.terminate()
        print("Finish Recording")

        if os.path.exists(audio_filename):
            audio = AudioSegment.from_wav(audio_filename) 
            rms = audio.rms
            rms_threshold = 500
            dbfs = audio.dBFS
            dbfs_threshold = -35

            if rms < rms_threshold and dbfs < dbfs_threshold:
                print(f"Skipping quiet file (RMS: {rms} and dBFS: {dbfs}): {audio_filename}") 
                # os.remove(audio_filename)
            # Add to prediction queue
            else:
                print(f"Processing (RMS: {rms} and dBFS: {dbfs}): {audio_filename}")
        # Clean up old recordings
        _cleanup_old_files()