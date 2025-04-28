import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import whisper
import ollama
from ollama import Client

# Record input audio
def record_until_silence(threshold=0.01, silence_duration=1.0, sample_rate=44100):
    print("Recording... Speak into the microphone.")
    recording = []
    silence_counter = 0
    
    def callback(indata, frames, time, status):
        nonlocal silence_counter
        volume_norm = np.linalg.norm(indata) / np.sqrt(frames)
        if volume_norm < threshold:
            silence_counter += frames
        else:
            silence_counter = 0
        recording.append(indata.copy())

    with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate):
        while silence_counter < silence_duration * sample_rate:
            sd.sleep(100)

    audio_data = np.concatenate(recording)

    write("input.wav", sample_rate, audio_data)
    print("Recording saved as 'input.wav'")

# STT model (whisper)
def speech_to_text(path): # path to audio (.mp3 or .wav)
    model = whisper.load_model("./models/tiny.en.pt")
    options = whisper.DecodingOptions(fp16=False)
    result = model.transcribe(path, **options.__dict__)
    return result["text"]

# LLM model (Ollama - llama3.2)
def generate_text(input):
    client = Client()
    response = client.create(
        model="jarvis:latest",
        from_="llama3.2:latest",
        system="Your name is Jarvis. You are a virutal assistant. Be concise and conversational.",
        stream=False,
    )

    print(response.status)

    res = ollama.chat(
        model = "jarvis:latest",
        messages = [
            {"role": "user", "content": input}
        ]
    )

    return res["message"]["content"]

# TTS model (Kokoro)
def text_to_speech(input):
    pipeline = KPipeline(lang_code='a', model="kokoro_small")
    text = input
    generator = pipeline(text, voice='af_heart')
    for i, (gs, ps, audio) in enumerate(generator):
        print(i, gs, ps)
        display(Audio(data=audio, rate=24000, autoplay=i==0))
        sf.write(f'{i}.wav', audio, 24000)

        print("Playing recorded audio...")
        data, fs = sf.read(f'{i}.wav', dtype='float32')
        sd.play(data, fs)
        sd.wait()