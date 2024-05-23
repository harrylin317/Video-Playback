import time
import os
from extract_audio.extract_audio import ExtractAudio
from audio_to_text.audio_to_text import AudioToText
from analyze_text.analyze_text import AnalyzeText
from process_video.process_video import ProcessVideo
from pipeline_processing.pipeline_processing import Pipeline
from slow_video.slow_video import SlowVideo
from play_video.play_video import PlayVideo
from launch_video.launch_video import LaunchVideo

if __name__ == "__main__":
    video_number = '2'
    save_path = f'outputs/output_{video_number}/'
    # save_path = f'outputs/'

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    args = {
        "video_path" : f"video_{video_number}.mp4",
        "audio_path" : os.path.join(save_path, "audio.wav"),
        "df_path" : os.path.join(save_path, "text.csv"),
        "transcript_path" : os.path.join(save_path, "transcript.json"),
        "output_path" : os.path.join(save_path, "output.mp4"),
        "split_max" : 15,
        "threshold_wpm" : 170,
        "run_extract_audio" : True,
        "run_audio_to_text": True,  
        "run_analyze_text": True,   
        "run_process_video": True,
        "run_video_player" : False 
    }
    start_time = time.time()
    # pipeline = Pipeline([ExtractAudio(), AudioToText(), AnalyzeText(), ProcessVideo()])
    # pipeline = Pipeline([ExtractAudio(), AudioToText(), AnalyzeText(), SlowVideo()])
    pipeline = Pipeline([ExtractAudio(), AudioToText(), AnalyzeText(), LaunchVideo()])
    # pipeline = Pipeline([ExtractAudio(), AudioToText(), AnalyzeText(), PlayVideo()])
    status = pipeline.run(args)
    if status != 0:
        exit()
    print('All process finished')
    end_time = time.time()
    runtime = end_time - start_time
    print("Runtime:", runtime, "seconds")


    
    
