import time
from audio_processing.audio_processing import AudioProcessing
from text_processing.text_processing import TextProcessing
from video_processing.video_processing import VideoProcessing
from pipeline_processing.pipeline_processing import Pipeline


if __name__ == "__main__":
    args = {
        "video_path" : "video_2.mp4",
        "audio_path" : "audio_2.wav",
        "df_path" : "text_df.csv",
        "transcript_path" : "transcript.json",
        "output_path" : "output.mp4",
        "threshold_wpm" : 160
    }
    start_time = time.time()
    pipeline = Pipeline([AudioProcessing(), TextProcessing(), VideoProcessing()])
    status = pipeline.run(args)
    if status != 0:
        exit()
    print('All process finished')
    end_time = time.time()
    runtime = end_time - start_time
    print("Runtime:", runtime, "seconds")


    
    
