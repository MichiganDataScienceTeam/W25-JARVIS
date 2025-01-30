# JARVIS

This repository contains the materials and code for the JARVIS project, a personal assistant inspired by Marvel’s J.A.R.V.I.S. Over the course of the semester, we will integrate voice recognition (speech-to-text), text-to-speech (TTS), natural language processing (NLP), and various task automation features.

The project is split into *two phases*:
1. **API-Powered Assistant (Weeks 1–4):** Utilize existing APIs (OpenAI, Whisper, etc.) to quickly develop JARVIS’ core functionality: speech recognition, TTS, and dynamic response generation.
2. **Offline Assistant (Weeks 5–10):** Replace cloud APIs with locally hosted models (using tools like [Ollama](https://ollama.ai/) and [Hugging Face](https://huggingface.co/)) to make JARVIS fully offline, handling everything from speech recognition and TTS to NLP on your own machine.

### Skills Learned 
- Voice Recognition and TTS
- Natural Language Processing (NLP)
- Offline Model Hosting (e.g., Ollama, Hugging Face)
- Working with Python libraries, asynchronous code, and APIs
- Automated Task Handling / Command System

### Weekly Slides 
Slides for supplementary learning can be found [here](https://drive.google.com/drive/folders/1bRHaBEFkx2ifdLgm-WceLcliEblSebY6?usp=sharing) (UMich login required).

### Requirements
- **Solid Python Skills:** You must be very comfortable with Python (object-oriented concepts, asynchronous programming, etc.).
- **Operating System:** macOS 11 or later, Windows 10 or later, or any modern Linux distribution.
- **API Familiarity:** You should have a strong understanding of how APIs work and how to integrate them.
- **(Optional) ML Experience:** Helpful but not required. We will cover essential ML topics as needed.

## Project Timeline

| Week | Date  | Topic                                            | Objective             |
|-----:|:-----:|:-------------------------------------------------|:----------------------|
| 1    | 1/26  | Introduction, Setup, Voice Input + TTS           | |
| 2    | 2/2   | Basic Command Handling System with LangChain     | |
| 3    | 2/9   | OpenAI API for Dynamic Response Generation       | |
| 4    | 2/16  | Ollama for Local Hosting                         | |
| 5    | 2/23  | Hugging Face Crash Course                        | Project Checkpoint    |
| -    | -     | Spring Break                                     | |
| -    | -     | Spring Break                                     | |
| 6    | 3/16  | Offline NLP Pipeline                             | |
| 7    | 3/23  | Integrating Offline Speech Recognition, TTS, NLP | |
| 8    | 3/30  | Development Time                                 | |
| 9    | 4/6   | Development Time                                 | |
| 10   | 4/13  | Final Expo Prep                                  | Final Deliverable Due |
| -    | 4/19  | Final Project Exposition 🎉                      | Presentation Due      |


> **Note**: Weeks **1–4** focus on creating JARVIS with cloud APIs. Weeks **5–10** focus on transitioning to an offline solution.

## Getting Started

If your local environment proves challenging, utilize cloud notebooks like [Google Colab](https://colab.research.google.com/) or [Kaggle](https://www.kaggle.com/).

### 1. Clone the Repository
   ```bash
    git clone https://github.com/MichiganDataScienceTeam/W25-JARVIS.git
    cd W25-JARVIS
   ```
### 2. Set Up Your Environment
We recommend using a virtual environment (requires Python 3.9 or later):
   ```bash
    python3 -m venv env

    source env/bin/activate  # Mac/Linux
    env\Scripts\activate     # Windows
    
    pip install -r requirements.txt
   ```

### API Keys (Phase 1)
In the initial phase, you will need an [OpenAI API](https://openai.com/) key (for GPT), plus any other keys for TTS or speech recognition if not handled locally.

Create a file named .env in the project’s root directory:
   ```bash
    # .env
    OPENAI_API_KEY=your_api_key
    OTHER_API_KEYS=...
    ...
   ```
Then, load it in your scripts:
   ```py
    from dotenv import load_dotenv
    load_dotenv()
    import os
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
   ```
**__**IMPORTANT:**__ Never commit API keys or .env files to Git.**

When using `openai`, setting the API key should look like this:
  ```py
  import openai
  
  openai.api_key = os.getenv("OPENAI_API_KEY")
  ```

### Using LangChain

We will make use of LangChain to handle LLM-driven workflows. Once your .env is set and loaded, LangChain will automatically pick up environment variables (e.g., OPENAI_API_KEY). If not, do the following:

```py
X_API_KEY = os.getenv("API_KEY_NAME")
# then, pass the API KEY variable where necessary
```

### Local Hosting (Phase 2)
After learning to integrate cloud APIs, we will shift towards offline hosting. Tools we’ll be using include:
- [Ollama](https://ollama.ai/) for local large language models.
- [Hugging Face Transformers](https://github.com/huggingface/transformers) for offline NLP.

## Deliverables
By the end of the project, you should have:
- A speech-to-text pipeline that captures voice commands.
- A text-to-speech engine that vocalizes JARVIS’ responses.
- A command handling system capable of both basic (hard-coded) commands and dynamic commands powered by large language models (cloud or local).
- An offline setup that relies on local models, culminating in a personal assistant that can handle open-ended queries, schedule reminders, and more — entirely on-device.

## Other Resources
- Python Basics: [Official Python Documentation](https://docs.python.org/3/)
- Speech Recognition: [SpeechRecognition Library](https://pypi.org/project/SpeechRecognition/), [OpenAI Whisper](https://github.com/openai/whisper)
- TTS: [pyttsx3](https://pypi.org/project/pyttsx3/), [gTTS](https://pypi.org/project/gTTS/) (for cloud-based TTS)
- Hugging Face: [Transformers Documentation](https://github.com/huggingface/transformers)
- Ollama: [Ollama](https://ollama.ai/)
- OpenAI Whisper: [OpenAI Whisper Repo](https://github.com/openai/whisper)

## Acknowledgements 
#### Project Leads
- Aarushi Shah – aarushah@umich.edu
- Muhammad (Abubakar) Siddiq – siddiq@umich.edu

#### Project Members
- Alexander Devine
- Kajal Patel
- Luke Davey
- Naveen Premkumar
- Pear Seraypheap
