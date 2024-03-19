import pandas as pd
import ast
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, ColorClip
import moviepy.video.fx.all as vfx
import os
import traceback

class ProcessVideo:
    @staticmethod
    def create_caption(line_dict, 
                       framesize, 
                       font = "Arial",
                       color='white', 
                       highlight_color='yellow', 
                       stroke_color='black', 
                       stroke_width=1.5):
        
        line_start, line_end = line_dict['timestamp']
        full_duration = line_end - line_start

        word_clips = []
        xy_textclips_positions =[]

        x_pos = 0
        y_pos = 0
        line_width = 0  # Total width of words in the current line
        frame_width = framesize[0]
        frame_height = framesize[1]

        x_buffer = frame_width * 1/10

        max_line_width = frame_width - 2 * (x_buffer)

        fontsize = int(frame_height * 0.075) #7.5 percent of video height

        space_width = ""
        space_height = ""
        word_clip_space = TextClip(" ", font=font, fontsize=fontsize, color=color)
        for i, word_info in enumerate(line_dict['word_timestamp_list']):
            word, start, end = word_info['word'], word_info['start'], word_info['end']
            duration = end - start
            word_clip = TextClip(word, font=font, fontsize=fontsize, color=color, 
                                 stroke_color=stroke_color,stroke_width=stroke_width).set_start(line_start).set_duration(full_duration)
            word_clip_space = word_clip_space.set_start(line_start).set_duration(full_duration)
            # word_clip_space = TextClip(" ", font = font, fontsize=fontsize, color=color).set_start(start).set_duration(full_duration)
            word_width, word_height = word_clip.size
            space_width, space_height = word_clip_space.size

            if line_width + word_width + space_width <= max_line_width:
                # Store info of each word_clip created
                xy_textclips_positions.append({
                    "x_pos":x_pos,
                    "y_pos": y_pos,
                    "width" : word_width,
                    "height" : word_height,
                    "word": word,
                    "start": start,
                    "end": end,
                    "duration": duration
                })

                word_clip = word_clip.set_position((x_pos, y_pos))
                word_clip_space = word_clip_space.set_position((x_pos + word_width, y_pos))

                x_pos = x_pos + word_width + space_width
                line_width = line_width + word_width + space_width


            else:
                # Move to the next line
                x_pos = 0
                # x_pos = max_line_width / 2
                y_pos = y_pos + word_height + 10
                line_width = word_width + space_width

                # Store info of each word_clip created
                xy_textclips_positions.append({
                    "x_pos":x_pos,
                    "y_pos": y_pos,
                    "width" : word_width,
                    "height" : word_height,
                    "word": word,
                    "start": start,
                    "end": end,
                    "duration": duration
                })

                word_clip = word_clip.set_position((x_pos, y_pos))
                word_clip_space = word_clip_space.set_position((x_pos + word_width, y_pos))
                x_pos = word_width + space_width


            word_clips.append(word_clip)
            word_clips.append(word_clip_space)

        for highlight_word in xy_textclips_positions:
            word_clip_highlight = TextClip(highlight_word['word'], font=font, fontsize=fontsize, color=highlight_color, stroke_color=stroke_color, stroke_width=stroke_width).set_start(highlight_word['start']).set_duration(highlight_word['duration'])
            word_clip_highlight = word_clip_highlight.set_position((highlight_word['x_pos'], highlight_word['y_pos']))
            word_clips.append(word_clip_highlight)

        return word_clips, xy_textclips_positions
    
    @staticmethod
    def create_text_dict(df):
        df['word_timestamp_list'] = df['word_timestamp_list'].apply(ast.literal_eval)
        df['timestamp'] = df['timestamp'].apply(ast.literal_eval)
        lines_dict = df[['timestamp', 'word_timestamp_list', 'text']].to_dict('records')
        return lines_dict
    
    def slow_video(self, df, video_path, output_path):
        try:
            print('Slowing video...')
            input_video = VideoFileClip(video_path)
            lines_dict = self.create_text_dict(df)
            
            all_linelevel_splits=[]

            for i, line in enumerate(lines_dict):
                print('line:', i)
                start = line['timestamp'][0]
                end = line['timestamp'][1]
                out_clips, positions = self.create_caption(line, input_video.size)
                max_width = 0
                max_height = 0

                for position in positions:
                    x_pos, y_pos = position['x_pos'],position['y_pos']
                    width, height = position['width'],position['height']

                    max_width = max(max_width, x_pos + width)
                    max_height = max(max_height, y_pos + height)

                color_clip = ColorClip(size=(int(max_width*1.1), int(max_height*1.1)),
                                    color=(64, 64, 64))
                color_clip = color_clip.set_opacity(.6)
                color_clip = color_clip.set_start(start).set_duration(end-start)

                clip_to_overlay = CompositeVideoClip([color_clip] + out_clips)
                clip_to_overlay = clip_to_overlay.set_position("bottom")


                all_linelevel_splits.append(clip_to_overlay)


            subbed_video = CompositeVideoClip([input_video] + all_linelevel_splits)

            # Set the audio of the final video to be the same as the input video
            # subbed_video = subbed_video.set_audio(input_video.audio)

            # Save the final clip as a video file with the audio included
            # subbed_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", threads=8)
            
            # filter df to only rows where wpm exceeds the threshold
            filtered_df = df.loc[df['slow_ratio'] != 1, ['slow_ratio', 'timestamp']] 

            if len(filtered_df) == 0:
                print('No segments needs to be slowed down')            
            else:
                # get the timestamps and slow ratios as lists
                timestamps = filtered_df['timestamp'].tolist()
                slow_ratios = filtered_df['slow_ratio'].tolist()
                
                # print(timestamps, len(slow_ratios))
                # print(slow_ratios, len(slow_ratios))

                # initialize the first clip
                final_clips = []
                final_clips.append(subbed_video.subclip(0, timestamps[0][0]))

                # Initialize a variable to keep track of the added time when slowing down clips
                added_time = 0

                # loop through timestamps
                for i in range(len(timestamps)):

                    start_time, end_time = timestamps[i]
                    slow_ratio = slow_ratios[i]

                    # Slow down video during the time interval
                    slowed_clip = subbed_video.subclip(start_time, end_time).fx(vfx.speedx, slow_ratio)

                    # Add slowed clip to the final clips
                    final_clips.append(slowed_clip)

                    # If this is not the last timestamp, add the next clip up to the next start time
                    if i < len(timestamps) - 1:
                        next_start_time = timestamps[i+1][0] + added_time
                        final_clips.append(subbed_video.subclip(end_time, next_start_time))

                # After the last timestamp, add the rest of the clip
                # final_clips.append(video.subclip(end_time + added_time, None))
                final_clips.append(subbed_video.subclip(timestamps[-1][1], None))

                # Concatenate all clips back together
                final_clip = concatenate_videoclips(final_clips)

                # Write the result to a file
            # final_clip.write_videofile(output_path, audio_codec='aac', threads=10, fps=24, preset='ultrafast')
            final_clip.write_videofile(output_path, audio_codec='aac', threads=10, fps=24, preset='ultrafast')
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

            if os.path.exists(df_path):
                df = pd.read_csv(df_path)
                status = self.slow_video(df, video_path, output_path)
                return status
            else:
                print('Dataframe file does not exists.')
                return -1
        else:
            print('Skip video processing')
            return 0



    