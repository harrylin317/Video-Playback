import os
import pandas as pd
from audio_processing.extract_audio import extract_audio
from audio_processing.audio_to_text import audio_to_text
from nlp_processing.combine_words import combine_words
from nlp_processing.analyze_text import analyze_text
from video_processing.slow_video import slow_video
import json


if __name__ == "__main__":
    
    video_path = "test_video.mp4"
    audio_path = "audio_long.wav"
    df_path = "text_df.csv"
    transcript_path = "transcript.json"

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

    if not os.path.exists(df_path):
        with open(transcript_path, 'r') as f:
            transcript = json.load(f)

        # combine words into sentences
        df = combine_words(transcript)    

        # analyze text
        df = analyze_text(df)
        
        df.to_csv(df_path, index=False)

    df = pd.read_csv(df_path)
    slow_video(df, video_path)
    
