import subprocess
import os
import pandas as pd
import traceback
import moviepy.editor as mp
import ast
import tempfile
import re
class SlowVideo:
    @staticmethod
    def fill_segments(split_videos, all_segments):
        new_segments = []
        for vid, segments in zip(split_videos, all_segments):
            video = mp.VideoFileClip(vid)
            duration = video.duration
            video.close()

            # Add beginning segment
            if segments[0][0] > 0:
                segments.insert(0, (0, segments[0][0], 1))
            
            # Add the remaining segments of the video
            if segments[-1][1] < duration:
                segments.append((segments[-1][1], duration, 1))

            # Add the segments in between the segments
            i = 0
            while i < len(segments) - 1:
                # If time between segment is small, stretch the previous end to match the next timestamp's start
                if segments[i+1][0] - segments[i][1] <= 0.5:
                    segments[i] = (segments[i][0], segments[i+1][0], segments[i][2])
                else:
                    segments.insert(i+1, (segments[i][1], segments[i+1][0], 1))
                i += 1
            new_segments.append(segments)
        return new_segments
    
    @staticmethod
    def split_video(input_file, interval=3):
        base_name = os.path.splitext(input_file)[0]

        # Split the video into 3-minute segments
        split_cmd = f"ffmpeg -y -i {input_file} -c copy -map 0 -segment_time 00:0{interval}:00 -f segment -reset_timestamps 1 {base_name}%03d.mp4"
        subprocess.run(split_cmd, shell=True)

        # Get the list of segments
        segments = os.listdir('.')
        segments = [seg for seg in segments if re.match(f"{base_name}\d{{3}}\.mp4", seg)]
        print(segments)
        return segments


    @staticmethod
    def split_timestamp(split_videos, segments):
        all_segments = []
        new_segment = []
        # Get each video segment length
        vid_durations = []
        for vid in split_videos:
            video = mp.VideoFileClip(vid)
            duration = video.duration
            video.close()
            vid_durations.append(duration)
        # print(vid_durations)

        # Accumulates values of video length
        accumulator = 0
        for start, end, speed in segments:
            # Subtract by the accumulator to maintain offset from previous video segment length, 
            # keeping it between range 0 and the max video length for that segment (roughly 3 minute)
            start -= accumulator
            end -= accumulator
            # Check if reach next video segment
            if end > vid_durations[0]:
                # Add the last segment timestamp
                new_segment.append((round(start,3), vid_durations[0], speed))
                all_segments.append(new_segment)
                new_segment = []
                
                # Add the first timestamp in the new segment
                start = 0
                end -= vid_durations[0]
                # Update accumulator by adding the next video length
                accumulator += vid_durations.pop(0)
            # Add segment that has adjusted for the offset
            new_segment.append((round(start,3), round(end,3), speed))

        all_segments.append(new_segment)
        return all_segments
     

    def slow(self, output_file, split_videos, all_segments):
        try:
            temp_files = []
            for vid, segments in zip(split_videos, all_segments):
                temp_file = 'processed_' + vid
                temp_files.append(temp_file)
                # Create a list to hold all the ffmpeg commands
                ffmpeg_commands = ["ffmpeg", "-y", "-hwaccel", "cuda", "-hwaccel_output_format", "cuda", "-i", vid, "-filter_complex"]

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
                ffmpeg_commands.extend(["-c:v", "h264_nvenc", temp_file])

                # Run the ffmpeg command
                subprocess.run(ffmpeg_commands)

            if len(split_videos) > 1:
                # Concatenate the processed segments
                with open('file_list.txt', 'w') as f:
                    for temp in temp_files:
                        f.write(f"file '{temp}'\n")

                concat_cmd = f"ffmpeg -y -f concat -safe 0 -i file_list.txt -c copy {output_file}"
                subprocess.run(concat_cmd, shell=True)
                os.remove('file_list.txt')
            
            #remove temp files
            for temp in temp_files:
                os.remove(temp)
            for vid in split_videos:
                os.remove(vid)
            

            return 0
        except Exception as e:
            print(f"Error occurred when slowing video: {e}")
            traceback.print_exc()
            return -1

        
            
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
                split_videos = self.split_video(video_path, 3)
                segments = df['time+slow'].apply(ast.literal_eval).tolist()
                segments = self.split_timestamp(split_videos, segments)
                segments = self.fill_segments(split_videos, segments)
                # print(segments)
                # status = self.slow_down_video(video_path, output_path, segments)
                status = self.slow(output_path, split_videos, segments)
                return status
                return 0
            else:
                print('Dataframe file does not exists.')
                return -1
        else:
            print('Skip video processing')
            return 0


