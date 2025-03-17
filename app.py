import streamlit as st
from moviepy.editor import VideoFileClip
import requests
import openai
from dotenv import load_dotenv
import os

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

st.set_page_config(page_title="Video to Audio Converter, Transcriber, and Summarizer!")

if not api_key:
    st.warning("Nie znaleziono pliku .env lub brak klucza API w pliku. Proszę wprowadzić klucz API poniżej.")
    api_key = st.text_input("OpenAI API Key", type="password")

openai.api_key = api_key

def video_to_audio(video_file):
    video = VideoFileClip(video_file)
    audio_path = "converted_audio.mp3"
    video.audio.write_audiofile(audio_path)
    return audio_path

def transcribe_audio_with_openai(audio_path):
    if not openai.api_key:
        return "Klucz API nie został ustawiony."

    api_url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    files = {
        'file': (audio_path, open(audio_path, 'rb')),
        'model': (None, 'whisper-1')
    }

    response = requests.post(api_url, headers=headers, files=files)

    if response.status_code == 200:
        return response.json().get("text", "Transcription failed.")
    else:
        return f"Error: {response.status_code}, {response.text}"

def summarize_text(text):
    # Generowanie podsumowania w punktach
    bullet_points_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that summarizes text into bullet points. Please use Polish for the summary."},
            {"role": "user", "content": f"Dokonaj podsumowania poniższego tekstu w punktach w języku polskim:\n\n{text}"}
        ],
        max_tokens=150,
        temperature=0.3
    )

    bullet_points = bullet_points_response.choices[0].message['content'].strip()

    # Generowanie pełnego streszczenia
    full_summary_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that summarizes text. Please use Polish for the summary."},
            {"role": "user", "content": f"Napisz pełne streszczenie poniższego tekstu w języku polskim:\n\n{text}"}
        ],
        max_tokens=300,
        temperature=0.3
    )

    full_summary = full_summary_response.choices[0].message['content'].strip()

    return bullet_points, full_summary

st.title("Video to Audio Converter, Transcriber, and Summarizer!")

uploaded_video = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

if uploaded_video is not None:
    with open("uploaded_video.mp4", "wb") as f:
        f.write(uploaded_video.getbuffer())

    st.success("Video uploaded successfully!")

    # Odtwarzanie przesłanego pliku wideo
    st.write("Odtwarzacz wideo")
    st.video("uploaded_video.mp4")

    if st.button("Convert to Audio"):
        audio_file = video_to_audio("uploaded_video.mp4")

        # Odtwarzanie wynikowego pliku audio
        st.audio(audio_file, format="audio/mp3")

        with open(audio_file, "rb") as f:
            st.download_button(label="Download Audio", data=f, file_name="audio.mp3")

        # Transkrypcja dźwięku
        st.write("Transcription of audio from video:")
        transcription = transcribe_audio_with_openai(audio_file)
        st.write(transcription)

        # Generowanie streszczenia
        st.write("Summary in bullet points (in Polish):")
        bullet_points, full_summary = summarize_text(transcription)
        st.write(bullet_points)

        # Generowanie pełnego streszczenia
        st.write("Full summary (in Polish):")
        st.write(full_summary)

# Odtwarzanie pliku audio
uploaded_audio = st.file_uploader("Upload an audio file", type=["mp3", "wav", "ogg"])

if uploaded_audio is not None:
    st.success("Audio file uploaded successfully!")
    st.audio(uploaded_audio, format=f"audio/{uploaded_audio.name.split('.')[-1]}")

    # Przechowywanie przesłanego audio w pliku
    audio_path = "uploaded_audio." + uploaded_audio.name.split('.')[-1]
    with open(audio_path, "wb") as f:
        f.write(uploaded_audio.getbuffer())

    # Transkrypcja przesłanego dźwięku
    st.write("Transcription of uploaded audio:")
    transcription = transcribe_audio_with_openai(audio_path)
    st.write(transcription)

    # Generowanie streszczenia
    st.write("Summary in bullet points (in Polish):")
    bullet_points, full_summary = summarize_text(transcription)
    st.write(bullet_points)

    # Generowanie pełnego streszczenia
    st.write("Full summary (in Polish):")
    st.write(full_summary)