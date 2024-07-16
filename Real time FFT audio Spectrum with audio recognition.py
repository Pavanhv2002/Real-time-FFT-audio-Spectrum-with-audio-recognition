import numpy as np
import matplotlib.pyplot as plt
import pyaudio
import time
from scipy.fft import fft
import speech_recognition as sr
import threading

# Parameters
CHUNK = 1024  # Number of samples per frame
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
THRESHOLD = 500  # Adjust this based on your noise level

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Function to perform FFT and plot spectrum
def plot_spectrum(y):
    Y = fft(y)
    freq = np.fft.fftfreq(len(y), 1 / RATE)
    mag = np.abs(Y)
    plt.clf()  # Clear the current figure
    plt.plot(freq[:len(freq) // 2], mag[:len(freq) // 2])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title('FFT Spectrum')
    plt.grid(True)
    plt.pause(0.05)  # Pause to allow for real-time plotting

# Function for voice recognition
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print(f"Recognized: {text}")
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")

    return text if 'text' in locals() else ''

# Function to handle voice recognition in a separate thread
def speech_recognition_thread():
    while True:
        recognize_speech()

# Start the voice recognition thread
thread = threading.Thread(target=speech_recognition_thread)
thread.daemon = True
thread.start()

# Main loop
plt.ion()  # Turn on interactive mode for plotting
try:
    while True:
        data = stream.read(CHUNK)
        y = np.frombuffer(data, dtype=np.int16).copy()  # Make a copy of the buffer

        # Apply noise reduction (e.g., simple noise gate)
        y[np.abs(y) < THRESHOLD] = 0

        plot_spectrum(y)

        time.sleep(0.1)  # Adjust sleep time for smoother visualization

except KeyboardInterrupt:
    pass

# Clean up
stream.stop_stream()
stream.close()
p.terminate()
plt.ioff()  # Turn off interactive mode
plt.show()  # Display the final plot if needed
