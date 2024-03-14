import pandas as pd
import ast
from moviepy.editor import VideoFileClip, concatenate_videoclips
import moviepy.video.fx.all as vfx
import os
import traceback

class ProcessVideo:
    @staticmethod
    def filter_timestamps(df, threshold_wpm):
        filtered_df = df[df['wpm'] > threshold_wpm]
        filtered_df['slow_ratio'] = threshold_wpm / filtered_df['wpm'] 

        # convert timestamp strings to tuples
        filtered_df['timestamp'] = filtered_df['timestamp'].apply(ast.literal_eval)

        return filtered_df
    
    def slow_video(self, df, video_path, output_path, threshold_wpm):
        try:
            print('Slowing video...')
            video = VideoFileClip(video_path)
            # filter df to only rows where wpm exceeds the threshold
            filtered_df = self.filter_timestamps(df, threshold_wpm)

            if len(filtered_df) == 0:
                print('No segments needs to be slowed down')
                return 0
            
            else:
                # get the timestamps and slow ratios as lists
                timestamps = filtered_df['timestamp'].tolist()
                slow_ratios = filtered_df['slow_ratio'].tolist()
                
                # print(timestamps, len(slow_ratios))
                # print(slow_ratios, len(slow_ratios))

                # initialize the first clip
                final_clips = []
                final_clips.append(video.subclip(0, timestamps[0][0]))

                # Initialize a variable to keep track of the added time when slowing down clips
                added_time = 0

                # loop through timestamps
                for i in range(len(timestamps)):

                    start_time, end_time = timestamps[i]
                    slow_ratio = slow_ratios[i]

                    # Slow down video during the time interval
                    slowed_clip = video.subclip(start_time, end_time).fx(vfx.speedx, slow_ratio)

                    # Add slowed clip to the final clips
                    final_clips.append(slowed_clip)

                    # If this is not the last timestamp, add the next clip up to the next start time
                    if i < len(timestamps) - 1:
                        next_start_time = timestamps[i+1][0] + added_time
                        final_clips.append(video.subclip(end_time, next_start_time))

                # After the last timestamp, add the rest of the clip
                # final_clips.append(video.subclip(end_time + added_time, None))
                final_clips.append(video.subclip(timestamps[-1][1], None))

                # Concatenate all clips back together
                final_clip = concatenate_videoclips(final_clips)

                # Write the result to a file
                final_clip.write_videofile(output_path, audio_codec='aac', threads=8, fps=24, logger=None, preset='ultrafast')
                print('Slowed video created successfully')
                return 0
        
        except Exception as e:
            print(f"Error occurred when slowing video: {e}")
            traceback.print_exc()
            return -1
            
    def process(self, args):
        if args['run_process_video']:
            df_path = args['df_path']
            video_path = args['video_path']
            output_path = args['output_path']
            threshold_wpm = args['threshold_wpm']

            if os.path.exists(df_path):
                df = pd.read_csv(df_path)
                status = self.slow_video(df, video_path, output_path, threshold_wpm)
                return status
            else:
                print('Dataframe file does not exists.')
                return -1
        else:
            print('Skip video processing')
            return 0



    