import os
import pandas as pd
from audio_processing.extract_audio import extract_audio
from audio_processing.audio_to_text import audio_to_text
from nlp_processing.analyze_transcript import analyze_transcript

if __name__ == "__main__":
    
    video_path = "test_video.mp4"
    audio_path = "audio_long.wav"
    transcript_path = "transcript_long.csv"

    # Convert video to audio file
    if not os.path.exists(audio_path):
        status = extract_audio(video_path, audio_path)
        if status == 0:
            print("audio file created successfully.")
        else:
            print("Error converting video to audio, aborting...")
            exit()

    # Convert audio to text file (json)
    if not os.path.exists(transcript_path):
        status = audio_to_text(audio_path, transcript_path)
        if status == 0:
            print("Transcript created successfully")
        else:
            print("Failed to convert audio to text, aborting...")
            exit()

    #load transcript file
    df = pd.read_csv(transcript_path)
    
    # analyze_transcript(transcript)
