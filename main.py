import time
from extract_audio.extract_audio import ExtractAudio
from audio_to_text.audio_to_text import AudioToText
from analyze_text.analyze_text import AnalyzeText
from process_video.process_video import ProcessVideo
from pipeline_processing.pipeline_processing import Pipeline


if __name__ == "__main__":
    args = {
        "video_path" : "video_2.mp4",
        "audio_path" : "audio_2.wav",
        "df_path" : "text_df.csv",
        "transcript_path" : "transcript.json",
        "output_path" : "output.mp4",
        "threshold_wpm" : 180,
        "run_extract_audio" : False,
        "run_audio_to_text": False,  
        "run_analyze_text": True,   
        "run_process_video": True  
    }
    start_time = time.time()
    pipeline = Pipeline([ExtractAudio(), AudioToText(), AnalyzeText(), ProcessVideo()])
    status = pipeline.run(args)
    if status != 0:
        exit()
    print('All process finished')
    end_time = time.time()
    runtime = end_time - start_time
    print("Runtime:", runtime, "seconds")


    
    
