from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
from pydub import AudioSegment
import subprocess
from vistec_ser.inference.inference import infer_sample, setup_server
from datetime import datetime
import threading
import time
from stack import Stack
import os

# Global objects that will be initialized in lifespan
recorder = None
predictor = None
prediction_stack = Stack()  # Shared stack between recorder and predictor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize global objects
    global recorder, predictor
    
    # Setup server components
    config_path = os.path.dirname(os.path.abspath(__file__)) + "/config.yaml"
    model, thaiser_module, temp_dir = setup_server(config_path)
    
    # Initialize recorder and predictor
    recorder = AudioRecorder(temp_dir, prediction_stack)
    predictor = PredictionWorker(model, thaiser_module, prediction_stack, temp_dir)
    
    # Start recording thread
    recording_thread = threading.Thread(target=recorder.start_recording_loop, daemon=True)
    recording_thread.start()
    
    # Start prediction thread
    prediction_thread = threading.Thread(target=predictor.prediction_loop, daemon=True)
    prediction_thread.start()
    
    yield  # Server is running
    
    # Cleanup
    recorder.stop()
    predictor.stop()

    _cleanup_old_files(temp_dir)

app = FastAPI(lifespan=lifespan)

class AudioRecorder:
    def __init__(self, temp_dir, stack):
        self.temp_dir = temp_dir
        self.current_recording = None
        self.stop_flag = False
        self.prediction_stack = stack

    def start_recording_loop(self):
        while not self.stop_flag:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"{self.temp_dir}/recorded_audio_{timestamp}.wav"
            audio_length = 5
            # Start recording
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

            if os.path.exists(audio_filename):
                audio = AudioSegment.from_wav(audio_filename)
                rms = audio.rms
                rms_threshold = 200
                dbfs = audio.dBFS
                dbfs_threshold = -38

                if rms < rms_threshold or dbfs < dbfs_threshold:
                    print(f"Skipping quiet file (RMS: {rms} and dBFS: {dbfs}): {audio_filename}. Setting the latest prediction to none.") 
                    predictor.reset_latest_prediciton()

                else:
                    print(f"Processing (RMS: {rms} and dBFS: {dbfs}): {audio_filename}")
                    self.prediction_stack.put(audio_filename)

    def stop(self):
        self.stop_flag = True

class PredictionWorker:
    def __init__(self, model, thaiser_module, stack, temp_dir):
        self.model = model
        self.thaiser_module = thaiser_module
        self.stop_flag = False
        self.latest_prediction = None
        self.prediction_stack = stack
        self.temp_dir = temp_dir

    def prediction_loop(self):
        while not self.stop_flag:
            try:
                # Get the next audio file from stack
                audio_filename = self.prediction_stack.get_latest(timeout=1)
                # Process the audio file
                inference_loader = self.thaiser_module.extract_feature([audio_filename])
                inference_results = [infer_sample(self.model, sample, emotions=self.thaiser_module.emotions) for sample in inference_loader]
                print(inference_results)
                # Store the latest prediction
                self.latest_prediction = inference_results[0] if inference_results else None
                # Clean up the processed file
                try:
                    print("Removing audio file after processing.")
                    _cleanup_old_files(self.temp_dir)
                    print("Audio file removed.")
                except:
                    pass
                    
            except TimeoutError:  # Specifically catch TimeoutError
                print("No audiofile in stack.")
                print("*–*-*-*-*-*-*-*-*-*-*-*-*")
                time.sleep(1)  # Add a small sleep to prevent CPU spinning
            except Exception as e:  # Catch any other exceptions
                print(f"Error processing audio: {e}")
                print("*–*-*-*-*-*-*-*-*-*-*-*-*")
                pass

    def stop(self):
        self.stop_flag = True

    def get_latest_prediction(self):
        return self.latest_prediction

    def reset_latest_prediciton(self):
        self.latest_prediction = "DNC"

def _cleanup_old_files(temp_dir):
    files = sorted([f for f in os.listdir(temp_dir) if f.startswith("recorded_audio")])
    for old_file in files:
        try:
            os.remove(os.path.join(temp_dir, old_file))
            print("Old files cleaned")
            print("*–*-*-*-*-*-*-*-*-*-*-*-*")
        except:
            pass

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "healthy"}

@app.get("/get_latest_prediction")
async def get_latest_prediction():
    if predictor is None:
        return {"error": "Server not fully initialized"}
    
    prediction = predictor.get_latest_prediction()
    return {"prediction": prediction if prediction is not None else None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", port=8080, reload=True) 