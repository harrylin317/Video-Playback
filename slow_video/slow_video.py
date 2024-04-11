import subprocess
import os
import pandas as pd
import traceback
import moviepy.editor as mp
import ast
import tempfile
import ffmpeg
class SlowVideo:
    @staticmethod
    def fill_segments(input_file, segments):
        video = mp.VideoFileClip(input_file)
        duration = video.duration
        video.close()

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
        return segments
    
    def slow(self, input_file, output_file, segments):
        try:
            # Create a list to hold all the ffmpeg commands
            ffmpeg_commands = ["ffmpeg", "-y", "-hwaccel", "cuda", "-hwaccel_output_format", "cuda", "-i", input_file, "-filter_complex"]

            # Create a list to hold all the filter_complex arguments
            filter_complex_args = []

            # Loop through each segment
            for i, (start, stop, speed) in enumerate(segments):
                # Add the commands to trim and slow down the video and audio for each segment
                filter_complex_args.extend([
                    f"[0:v]trim={start}:{stop},setpts={speed}*(PTS-STARTPTS)[v{i}];",
                    f"[0:a]atrim={start}:{stop},asetpts=PTS-STARTPTS,atempo=1/{speed}[a{i}];"
                ])

            # Add the command to concatenate all the segments
            filter_complex_args.append("".join(f"[v{i}][a{i}]" for i in range(len(segments))) + f"concat=n={len(segments)}:v=1:a=1")

            # Add the filter_complex arguments to the ffmpeg commands
            ffmpeg_commands.append("".join(filter_complex_args))
            
            # Add the rest of the ffmpeg commands
            # ffmpeg_commands.extend(["-preset", "superfast", "-profile:v", "baseline", output_file])
            ffmpeg_commands.extend(["-c:v", "h264_nvenc", output_file])
            # ffmpeg_commands.append(output_file)

            # Run the ffmpeg command
            subprocess.run(ffmpeg_commands)

            return 0
        except Exception as e:
            print(f"Error occurred when slowing video: {e}")
            traceback.print_exc()
            return -1

        
            
    # def slow_down_video(self, input_file, output_file, segments):
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
            crossfade_duration = 1  # duration of crossfade in seconds

            for i, segment in enumerate(segments):
                start_time, end_time, slow_ratio = segment
                if slow_ratio == 1:
                    filter_complex_script += f"[0:v]trim=start={start_time}:end={end_time},setpts=PTS-STARTPTS[v{i}]; [0:a]atrim=start={start_time}:end={end_time},asetpts=PTS-STARTPTS[a{i}]; "
                else:    
                    filter_complex_script += f"[0:v]trim=start={start_time}:end={end_time},setpts={slow_ratio}*(PTS-STARTPTS)[v{i}]; [0:a]atrim=start={start_time}:end={end_time},asetpts={slow_ratio}*(PTS-STARTPTS),atempo=1/{slow_ratio}[a{i}]; "
            # Add crossfade between audio segments
            for i in range(len(segments) - 1):
                filter_complex_script += f"[a{i}][a{i+1}]acrossfade=d={crossfade_duration}[a{i+1}c]; "


            # filter_complex_script += "".join(f"[v{i}][a{i}]" for i in range(len(segments))) + "concat=n={} :v=1 :a=1 [out]".format(len(segments))
            filter_complex_script += "".join(f"[v{i}][a{i}c]" for i in range(len(segments))) + f"concat=n={len(segments)}:v=1:a=1[out]"

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
            print(f"Error occurred when slowing video: {e}")
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
                # print(segments)
                # print(len(segments))
                # status = self.slow_down_video(video_path, output_path, segments)
                status = self.slow(video_path, output_path, segments)
                return status
            else:
                print('Dataframe file does not exists.')
                return -1
        else:
            print('Skip video processing')
            return 0


