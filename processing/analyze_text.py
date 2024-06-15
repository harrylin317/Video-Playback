# from textstat import textstat
import pandas as pd
import json
import os
import traceback
import moviepy.editor as mp


class AnalyzeText:
    @staticmethod
    def calculate_wpm(row, threshold_wpm):
        num_words = len(row['text'].split())
        duration_in_minute = (row['timestamp'][1] - row['timestamp'][0]) / 60
        # prevent division by 0
        if duration_in_minute == 0:
            return threshold_wpm
        duration_in_minute = max(duration_in_minute, 0.001)
        wpm = num_words / duration_in_minute
        return round(wpm, 2)
    
    @staticmethod
    def combine_tuples(row):
        return (row['timestamp'][0], row['timestamp'][1], row['slow_ratio'])

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
            # if the slow_ratio is consecutively the same, combine them
            if segments[i+1][2] == segments[i][2]:
                segments[i] = (segments[i][0], segments[i+1][1], segments[i][2])
                segments.pop(i+1)
            # If time between segments is small, stretch the previous end to match the next timestamp's start
            elif segments[i+1][0] - segments[i][1] < 2:
                segments[i] = (segments[i][0], segments[i+1][0], segments[i][2])
            else:
                segments.insert(i+1, (segments[i][1], segments[i+1][0], 1))
            i += 1
        return segments
    
    def analyze_text(self, df, df_path, threshold_wpm, video_path, segments_path):
        try:
            print('Analyzing text...')
            df['wpm'] = df.apply(self.calculate_wpm, threshold_wpm=threshold_wpm, axis=1)
            # calculate slow ratio. Equals 1 if not need slowing
            df['slow_ratio'] = df['wpm'].apply(lambda wpm: round((threshold_wpm/wpm), 2) if wpm > threshold_wpm else 1)
            # df['slow_ratio'] = df['wpm'].apply(lambda wpm: min(round((wpm/threshold_wpm), 2), 2) if wpm > threshold_wpm else 1)
            df['time+slow'] = df.apply(lambda row : self.combine_tuples(row), axis=1)
            df.to_csv(df_path, index=False)

            segments = df['time+slow'].tolist()
            segments = self.fill_segments(video_path, segments)
            segments_dict = [dict(zip(("start", "end", "slow_ratio"), x)) for x in segments]
            with open(segments_path, "w") as outfile: 
                json.dump(segments_dict, outfile)
            
            print('Successfully analyzed text, Dataframe file created')
            return 0
        except Exception as e:
            print(f"Error occurred when analyzing text: {e}")
            traceback.print_exc()
            return -1
    
    def combine_words(self, transcript, split_max):
        try:
            print('Combining words from transcript...')
            words = transcript
            sentence = ""
            # char_count = 0
            word_timestamp_list = []
            record_start_time = words[0]['start']


            df = pd.DataFrame(columns=['timestamp', 'text', 'word_timestamp_list'])
            end_index = len(words) - 1
            for i, word_info in enumerate(words):

                # handle the case for numbers e.g. '1980' with no start or end timestamps
                
                if 'start' not in word_info:
                    if i == end_index:
                        word_info['start'] = words[i-1]['end']
                        word_info['end'] = words[i-1]['end'] + 3
                    # if next word is also an abonormal word
                    # keep searching for the next word and eventually find one that is a normal word
                    # Divide the timestamp between the two normal words to find a average timestamp and allocate them to the abnormal cases 
                    elif 'start' not in words[i+1]:
                        next_idx = i + 1
                        divide = 1
                        while 'start' not in words[next_idx]:
                            next_idx += 1
                            divide += 1
                        next_time = words[next_idx]['start']
                        prev_time = words[i-1]['end']
                        divided_interval = round((next_time - prev_time) / divide, 3)
                        end_time = prev_time + divided_interval
                        word_info['start'] = prev_time
                        word_info['end'] = end_time
                    #if abnormal word is the first word, give it a arbitrary 3 seconds of timeframe
                    elif i == 0:
                        word_info['start'] = max(0, words[i+1]['start'] - 3)
                        word_info['end'] = words[i+1]['start']
                    else:
                        word_info['start'] = words[i-1]['end']
                        word_info['end'] = words[i+1]['start']

                word = word_info['word']
                start_time = word_info['start']
                end_time = word_info['end']

                # add individual word and it's timestamp
                word_timestamp_list.append(word_info)

                # if last word was the end of sentence, initialize starting timestamp
                if record_start_time == None:
                    record_start_time = start_time
                
                # append word to sentence
                sentence = sentence + ' ' + word
                # char_count += len(word)
                
                # if there has been split_max words in the sentence, end the sentence
                # if word is the last word in the transcript, end the sentence as well
                # if char_count >= split_max or i == end_index:
                if (i + 1) % split_max == 0 or i == end_index:
                    
                    new_row = pd.DataFrame({'timestamp': [(record_start_time, end_time)], 'text': [sentence.strip()], 'word_timestamp_list': [word_timestamp_list]})
                    df = pd.concat([df, new_row], ignore_index=True)
                    sentence = ""
                    record_start_time = None
                    word_timestamp_list = []
                    # char_count = 0
                
            return df, 0
        except Exception as e:
            print(f"Error occurred when combining words: {e}")
            traceback.print_exc()
            return None, -1
    
    def process(self, args):
        if args['run_analyze_text']:
            df_path = args['df_path']
            transcript_path = args['transcript_path']
            threshold_wpm = args['threshold_wpm']
            split_max = args['split_max']
            video_path = args['video_path']
            segments_path = args['segments_path']

            if os.path.exists(transcript_path):
                with open(transcript_path, 'r') as f:
                    transcript = json.load(f)

                df, status = self.combine_words(transcript, split_max)
                if status != 0:
                    return -1

                status = self.analyze_text(df, df_path, threshold_wpm, video_path, segments_path)
                if status != 0:
                    return -1
                
                return 0
            else:
                print('Transcript file does not exist')
                return -1
        else:
            print('Skip analyzing text')
            return 0
