import streamlit as st
import sounddevice as sd
import numpy as np
import time
import os
import base64
from scipy.io.wavfile import write
import tempfile
import queue
from models import speech_to_text, text_to_speech
from function_calling import handle_chat

st.set_page_config(
    page_title="JARVIS Voice Assistant",
    layout="wide"
)

os.makedirs("temp", exist_ok=True)
os.makedirs("temp/audio_history", exist_ok=True)

st.title("MDST - JARVIS")
st.markdown("""
This app combines speech recognition, language processing, and function calling to create a voice-powered assistant
that can perform tasks like sending emails, creating calendar events, and searching the web.
""")

def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
                <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'sample_rate' not in st.session_state:
    st.session_state.sample_rate = 44100
if 'silence_threshold' not in st.session_state:
    st.session_state.silence_threshold = 0.01  # Adjust for microphone sensitivity
if 'silence_duration' not in st.session_state:
    st.session_state.silence_duration = 1.5  # Seconds of silence to stop recording
if 'audio_counter' not in st.session_state:
    st.session_state.audio_counter = 0
if 'autoplay_enabled' not in st.session_state:
    st.session_state.autoplay_enabled = True

def record_audio_until_silence():
    if st.session_state.is_recording:
        return
        
    st.session_state.is_recording = True
    
    audio_queue = queue.Queue()
    
    status_container = st.empty()
    with status_container.container():
        status_text = st.empty()
        recording_indicator = st.empty()
    
    silence_samples = 0
    is_speaking = False
    silence_threshold = st.session_state.silence_threshold
    silence_frames = int(st.session_state.silence_duration * st.session_state.sample_rate)
    
    def audio_callback(indata, frames, time, status):
        """This callback is called from a separate thread"""
        nonlocal silence_samples, is_speaking
        
        if status:
            print(f"Error in audio recording: {status}")
        
        volume_norm = np.linalg.norm(indata) / np.sqrt(frames)
        
        if volume_norm > silence_threshold:
            is_speaking = True
            silence_samples = 0
        elif is_speaking:  # Count silence after speech detected
            silence_samples += frames
            
        audio_queue.put(indata.copy())
    
    recording_indicator.markdown("**Recording...**")
    status_text.text("Speak now. I'll listen until you stop talking...")
    
    try:
        with sd.InputStream(callback=audio_callback, channels=1, samplerate=st.session_state.sample_rate):
            timeout_counter = 0
            max_timeout = 50  # 5 seconds (10 checks per second)
            
            while not is_speaking and timeout_counter < max_timeout:
                status_text.text(f"Waiting for speech... {(max_timeout - timeout_counter) / 10:.1f}s")
                time.sleep(0.1)
                timeout_counter += 1
            
            if not is_speaking:
                status_text.text("No speech detected. Try again.")
                time.sleep(1)
                status_container.empty()
                st.session_state.is_recording = False
                return
            
            while silence_samples < silence_frames:
                status_text.text("Recording... (Stop talking to end recording)")
                time.sleep(0.1)
        
        audio_chunks = []
        while not audio_queue.empty():
            audio_chunks.append(audio_queue.get())
        
        if audio_chunks:
            audio_data = np.concatenate(audio_chunks)
            
            user_audio_path = f"temp/audio_history/user_{st.session_state.audio_counter}.wav"
            write(user_audio_path, st.session_state.sample_rate, audio_data)
            
            temp_file = "temp/input.wav"
            write(temp_file, st.session_state.sample_rate, audio_data)
            
            status_text.text("Processing your request...")
            
            try:
                input_text = speech_to_text(temp_file)
                
                if not input_text or input_text.strip() == "":
                    status_text.text("Could not understand audio. Please try again.")
                    time.sleep(2)
                    status_container.empty()
                    st.session_state.is_recording = False
                    return
                
                st.session_state.conversation_history.append({
                    "role": "user", 
                    "content": input_text,
                    "audio": user_audio_path
                })
                
                response = handle_chat(input_text)
                
                status_text.text("Generating speech response...")
                assistant_audio_files = text_to_speech(response, f"temp/audio_history/assistant_{st.session_state.audio_counter}")
                
                st.session_state.conversation_history.append({
                    "role": "assistant", 
                    "content": response,
                    "audio": assistant_audio_files
                })
                
                st.session_state.audio_counter += 1
                
            except Exception as e:
                st.error(f"Error processing request: {str(e)}")
        
    except Exception as e:
        st.error(f"Error during recording: {str(e)}")
    
    finally:
        status_container.empty()
        st.session_state.is_recording = False
        st.rerun()

def process_text_input():
    if st.session_state.text_input:
        input_text = st.session_state.text_input
        
        st.session_state.conversation_history.append({
            "role": "user", 
            "content": input_text,
            "audio": None
        })
        
        with st.status("Processing..."):
            response = handle_chat(input_text)
            
            assistant_audio_files = text_to_speech(response, f"temp/audio_history/assistant_{st.session_state.audio_counter}")
            
            st.session_state.conversation_history.append({
                "role": "assistant", 
                "content": response,
                "audio": assistant_audio_files
            })
            
            st.session_state.audio_counter += 1

col1, col2 = st.columns(2)

with col1:
    st.subheader("Voice Input")
    record_button = st.button(
        "Start Recording", 
        key="record_button", 
        disabled=st.session_state.is_recording,
        use_container_width=True
    )
    
    if record_button:
        record_audio_until_silence()
    
    with st.expander("Voice Recording Settings"):
        st.slider(
            "Silence Threshold", 
            min_value=0.001, 
            max_value=0.05, 
            value=st.session_state.silence_threshold,
            step=0.001,
            format="%.3f",
            key="silence_threshold_slider",
            help="Lower values make the system more sensitive to silence"
        )
        
        st.slider(
            "Silence Duration (seconds)", 
            min_value=0.5, 
            max_value=3.0, 
            value=st.session_state.silence_duration,
            step=0.1,
            format="%.1f",
            key="silence_duration_slider",
            help="How long to wait after detecting silence before stopping recording"
        )
        
        st.session_state.silence_threshold = st.session_state.silence_threshold_slider
        st.session_state.silence_duration = st.session_state.silence_duration_slider
        
        st.checkbox("Enable audio autoplay", value=st.session_state.autoplay_enabled, key="autoplay_checkbox")
        st.session_state.autoplay_enabled = st.session_state.autoplay_checkbox

with col2:
    st.subheader("Text Input")
    st.text_input("Type your message:", key="text_input", on_change=process_text_input)

st.subheader("Conversation History")
chat_container = st.container(height=500, border=True)

if (
    st.session_state.conversation_history 
    and st.session_state.conversation_history[-1]["role"] == "assistant"
    and st.session_state.conversation_history[-1]["audio"]
    and st.session_state.autoplay_enabled
):
    latest_audio = st.session_state.conversation_history[-1]["audio"][0] if isinstance(
        st.session_state.conversation_history[-1]["audio"], list
    ) else st.session_state.conversation_history[-1]["audio"]
    
    autoplay_audio(latest_audio)

with chat_container:
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            pass
            # st.markdown(f"**You**: {message['content']}")
            # if message.get("audio"):
            #     st.audio(message["audio"])
        else:
            st.markdown(f"**Assistant**: {message['content']}")
            if message.get("audio"):
                if isinstance(message["audio"], list):
                    with st.expander("Audio Response Segments"):
                        for i, audio_file in enumerate(message["audio"]):
                            st.audio(audio_file, format="audio/wav")
                else:
                    st.audio(message["audio"], format="audio/wav")

with st.sidebar:
    st.subheader("System Information")
    st.markdown("**Available Functions:**")
    st.markdown("- Send Email")
    st.markdown("- Create Calendar Event")
    st.markdown("- Search the Web")
    
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.audio_counter = 0
        st.rerun()