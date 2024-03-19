import subprocess
import os
import pandas as pd
import traceback
import moviepy.editor as mp
import ast
import tempfile

class SlowVideo:

    def slow_down_video(self, input_file, output_file, segments):
        try:
            # Get the duration of the video
            video = mp.VideoFileClip(input_file)
            duration = video.duration
            video.close()

            # Sort the segments by start time
            # segments.sort(key=lambda x: x[0])

            # Add beginning segment
            if segments[0][1] > 0:
                segments.insert(0, (0, segments[0][0], 1))
            
            # Add the remaining segments of the video
            if segments[-1][1] < duration:
                segments.append((segments[-1][1], duration, 1))

            # Add the segments in between the specified segments
            i = 0
            while i < len(segments) - 1:
                if segments[i][1] < segments[i+1][0]:
                    segments.insert(i+1, (segments[i][1], segments[i+1][0], 1))
                i += 1
            
            filter_complex_script = ""
            for i, segment in enumerate(segments):
                start_time, end_time, slow_ratio = segment
                if slow_ratio == 1:
                    filter_complex_script += f"[0:v]trim=start={start_time}:end={end_time},setpts=PTS-STARTPTS[v{i}]; [0:a]atrim=start={start_time}:end={end_time},asetpts=PTS-STARTPTS[a{i}]; "
                else:
                    filter_complex_script += f"[0:v]trim=start={start_time}:end={end_time},setpts={slow_ratio}*(PTS-STARTPTS)[v{i}]; [0:a]atrim=start={start_time}:end={end_time},asetpts={slow_ratio}*(PTS-STARTPTS),atempo=1/{slow_ratio}[a{i}]; "



            filter_complex_script += "".join(f"[v{i}][a{i}]" for i in range(len(segments))) + "concat=n={} :v=1 :a=1 [out]".format(len(segments))
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as f:
                temp_filename = f.name
                f.write(filter_complex_script.encode())

            command = f'ffmpeg -y -i {input_file} -filter_complex_script {temp_filename} -map "[out]" -acodec aac {output_file}'
            subprocess.call(command, shell=True)

            # Delete the temporary file
            os.unlink(temp_filename)

            return 0

        except Exception as e:
            print(f"Error occurred when converting audio to text: {e}")
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
                status = self.slow_down_video(video_path, output_path, segments)
                return status
            else:
                print('Dataframe file does not exists.')
                return -1
        else:
            print('Skip video processing')
            return 0


