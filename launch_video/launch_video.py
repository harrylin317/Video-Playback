import os
import pandas as pd
import traceback
import moviepy.editor as mp
import ast
from flask import Flask, render_template, send_from_directory, request

class LaunchVideo:
    @staticmethod
    def fill_segments(vid, segments):
        video = mp.VideoFileClip(vid)
        duration = video.duration
        video.close()

        # Add beginning segments
        if segments[0][0] > 0:
            segments.insert(0, (0, segments[0][0], 1))
        
        # Add the remaining segments of the video
        if segments[-1][1] < duration:
            segments.append((segments[-1][1], duration, 1))

        # Add the segments in between the segments
        i = 0
        while i < len(segments) - 1:
            # If time between segments is small, stretch the previous end to match the next timestamp's start
            if segments[i+1][0] - segments[i][1] <= 0.5:
                segments[i] = (segments[i][0], segments[i+1][0], segments[i][2])
            else:
                segments.insert(i+1, (segments[i][1], segments[i+1][0], 1))
            i += 1
        return segments
    
   
    
    @staticmethod
    def launch_web(video_path, segments):
        try:
            app = Flask(__name__, static_folder='../static', static_url_path='/static')
            @app.route('/')
            def index():
                return render_template('index.html', segments=segments, video_filename=video_path)
            
            # Run Flask app synchronously
            app.run(debug=True, use_reloader=False)
            return 0
        except Exception as e:
            print(f"An error occurred while launching the web server: {e}")
            traceback.print_exc()
            return -1




    def process(self, args):
        if args['run_process_video']:
            df_path = args['df_path']
            video_path = args['video_path']
            output_path = args['output_path']

            if os.path.exists(df_path):
                df = pd.read_csv(df_path)
                segments = df['time+slow'].apply(ast.literal_eval).tolist()
                segments = self.fill_segments(video_path, segments)
                status = self.launch_web(video_path, segments)
                return status
            else:
                print('Dataframe file does not exists.')
                return -1
        else:
            print('Skip video processing')
            return 0


