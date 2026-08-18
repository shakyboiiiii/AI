import threading
import sys
import time
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import wave
import speech_recognition as sr
from speech_recognition import AudioData
stop_event = threading.Event()
def wait_for_enter():
    input("\nPress Enter to stop recording...\n")
    stop_event.set()
def spinner():
    spinner_chars = "|/-\\"
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write("\rRecording... " + spinner_chars[idx % len(spinner_chars)])
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write("\rRecording stopped.         \n")
def record_until_enter():
    p = pyaudio.PyAudio()
    format = pyaudio.paInt16
    rate = 16000
    channels = 1
    buffer = 1024
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=buffer)
    frames = []
    threading.Thread(target=wait_for_enter).start()
    threading.Thread(target=spinner).start()
    while not stop_event.is_set():
        try:
            data = stream.read(buffer)
            frames.append(data)
        except Exception as e:
            print("Stream error:", e)
            break
    stream.stop_stream()
    stream.close()
    width = p.get_sample_size(format)
    p.terminate()
    return b"".join(frames), rate, width
def save_audio(data, rate, width, filename="my_audio.wav"):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(width)
        wf.setframerate(rate)
        wf.writeframes(data)
    print(f"Audio saved to {filename}")
def transcribe_audio(data, rate, width, filename="my_transcript.txt"):
    recognizer = sr.Recognizer()
    audio = AudioData(data, rate, width)
    try:
        text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        text = "Could not understand the audio."
    except sr.RequestError as e:
        text = f"API error: {e}"
    print("Transcription:", text)
    with open(filename, "w") as f:
        f.write(text)
    print(f"Transcript saved to {filename}")
def show_waveform(data, rate):
    samples = np.frombuffer(data, dtype=np.int16)
    t = np.linspace(0, len(samples) / rate, num=len(samples))
    plt.plot(t, samples)
    plt.title("Your Voice Waveform")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.show()
def main():
    print("???? Speak into the mic. Press Enter to stop.")
    audio, rate, width = record_until_enter()
    save_audio(audio, rate, width)
    transcribe_audio(audio, rate, width)
    show_waveform(audio, rate)
if __name__ == "__main__":
    main()
