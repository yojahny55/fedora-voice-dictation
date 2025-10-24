import queue
import threading

import numpy as np
import sounddevice as sd
import whisper

# Load the Whisper model
model = whisper.load_model("base")

# Audio parameters
SAMPLE_RATE = 16000
BUFFER_SIZE = 1024
audio_queue = queue.Queue()


def audio_callback(indata, frames, time, status):
    """Callback function to capture audio data."""
    if status:
        print(status)
    audio_queue.put(indata.copy())


def transcribe_audio():
    """Thread to transcribe audio in real time."""
    while True:
        # Block until at least one chunk is available
        first_chunk = audio_queue.get()

        # Collect first chunk and drain any immediately available remaining chunks
        buffers = [first_chunk]
        while not audio_queue.empty():
            buffers.append(audio_queue.get())

        # Combine buffers into a single numpy array
        if buffers:
            audio_data = np.concatenate(buffers, axis=0)
        else:
            audio_data = np.array([], dtype=np.float32)

        # Ensure correct dtype and 1D shape
        audio_data = audio_data.flatten().astype(np.float32)

        if audio_data.size == 0:
            continue

        # Transcribe the audio
        result = model.transcribe(audio_data, language="en")
        print(f"Transcription: {result['text']}")


# Start the transcription thread
transcription_thread = threading.Thread(target=transcribe_audio, daemon=True)
transcription_thread.start()

# Start capturing audio from the microphone
with sd.InputStream(
    callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=BUFFER_SIZE
):
    print("Listening... Press Ctrl+C to stop.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nStopping...")
