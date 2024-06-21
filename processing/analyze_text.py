# from textstat import textstat
import pandas as pd
import json
import os
import traceback
import moviepy.editor as mp
import re
import syllables


class AnalyzeText:
    @staticmethod
    def calculate_wpm(row, threshold_wpm):
        num_words = len(row['text'].split())
        duration_in_minute = (row['timestamp'][1] - row['timestamp'][0]) / 60
        # prevent division by 0
        if duration_in_minute <= 0:
            return threshold_wpm
        wpm = num_words / duration_in_minute
        return round(wpm, 2)
       
    @staticmethod
    def calculate_spm(row, threshold_spm):
        word_list = row['text'].split()
        duration_in_minutes = (row['timestamp'][1] - row['timestamp'][0]) / 60
        # prevent division by 0
        if duration_in_minutes <= 0:
            return threshold_spm
        total_syllables = 0
        for word in word_list:
            total_syllables += syllables.estimate(word)       
            
        spm = total_syllables / duration_in_minutes
        return round(spm, 2)
    
    @staticmethod
    def calculate_slow_ratio(row, threshold_wpm, threshold_spm):
        wpm = row['wpm']
        spm = row['spm']
        wpm_ratio = threshold_wpm / wpm if wpm > threshold_wpm else 1
        spm_ratio = threshold_spm / spm if spm > threshold_spm else 1
        average_ratio = round((wpm_ratio + spm_ratio) / 2, 2)
        return average_ratio
    
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
    
    @staticmethod
    def add_row(df, timestamp, sentence, word_timestamp_list):
        new_row = pd.DataFrame({'timestamp': [timestamp], 'text': [sentence], 'word_timestamp_list': [word_timestamp_list]})
        df = pd.concat([df, new_row], ignore_index=True)
        return df

    @staticmethod
    def handle_abnormal_words(i, end_index, word_info, words):
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
        return word_info

    @staticmethod
    def convert_to_webvtt_timestamp(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)

        return f"{hours:02}:{minutes:02}:{secs:02}.{milliseconds:03}"
    
    @staticmethod
    def convert_time_span_to_webvtt(timestamp):
        start_time = AnalyzeText.convert_to_webvtt_timestamp(timestamp[0])
        end_time = AnalyzeText.convert_to_webvtt_timestamp(timestamp[1])
        return f"{start_time} --> {end_time}"

    def create_webvtt(self, df, webvtt_path):
        try:
            print('Generating subtitles...')
            timestamps = df['timestamp'].tolist()
            sentences = df['text'].tolist()
            total_len = len(sentences)

            line_counter = 0
            webvtt_content = "WEBVTT\n\n"
            for i, (timestamp, sentence) in enumerate(zip(timestamps, sentences)):
                line_counter += 1
                if line_counter == 1:
                    webvtt_content += timestamp + '\n'
                    webvtt_content += sentence + '\n'
                elif line_counter == 2:
                    webvtt_content += sentence + '\n'
                    line_counter = 0
                elif line_counter != 2 and i == total_len - 1:
                    print('hye')
                


            

            with open(webvtt_path, 'w') as file:
                file.write(webvtt_content)
            return 0
        except Exception as e:
            print(f"Error occurred when generating subtitles: {e}")
            traceback.print_exc()
            return -1
    
    def analyze_text(self, df, df_path, threshold_wpm, threshold_spm, video_path, segments_path):
        try:
            print('Analyzing text...')
            df['wpm'] = df.apply(self.calculate_wpm, threshold_wpm=threshold_wpm, axis=1)
            df['spm'] = df.apply(self.calculate_spm, threshold_spm=threshold_spm, axis=1)
            # calculate slow ratio. Equals 1 if not need slowing
            df['slow_ratio'] = df.apply(self.calculate_slow_ratio, threshold_wpm=threshold_wpm, threshold_spm=threshold_spm, axis=1)
            # df['slow_ratio'] = df['wpm'].apply(lambda wpm: round((threshold_wpm/wpm), 2) if wpm > threshold_wpm else 1)
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
    
    def combine_subtitle(self, sub_path, transcript):
        try:
            print('Combining words for subtitles...')
            words = transcript
            df = pd.DataFrame(columns=['timestamp', 'text', 'word_timestamp_list']) 
            end_index = len(words) - 1
            word_list = []
            word_timestamp_list = []
            start_time = None
            split_index = None
            second_line = False
            word_count = 0
            char_count = 0
            max_char = 40
            chars_to_check = {',', '?', '.'}
        

            for i, word_info in enumerate(words):
                # handle the case for numbers e.g. '1980' with no start or end timestamps                
                if 'start' not in word_info:
                    word_info = self.handle_abnormal_words(i, end_index, word_info, words)                

                word = word_info['word']

                # end sentence if new word char exceeds maximum char count
                if len(word) + char_count > max_char:
                    # if not the second line of the subtitle, simply add a '/' to signify cut location, and reset character count                    
                    if not second_line:
                        word_list[-1] = word_list[-1] + '/'       
                        char_count = 0
                        split_index = None
                        second_line = True
                    # if current line is the second line of subtitle, then cut the sentence and continue one the second segment 
                    # (produces empty second segment if no split index is found)
                    else:
                        if split_index == None:
                            split_index = word_count - 1
                                           
                        cut_sentence = ' '.join(word_list[:split_index + 1])
                        cut_timestamp_list = word_timestamp_list[:split_index + 1]     
                        end_time = cut_timestamp_list[split_index]['end']

                        df = self.add_row(df, (start_time, end_time), cut_sentence, cut_timestamp_list)

                        word_list = word_list[split_index + 1:]
                        word_timestamp_list = word_timestamp_list[split_index + 1:] 
                        char_count = sum(len(w) for w in word_list)
                        word_count = len(word_list)
                        if word_count == 0:
                            start_time = None
                        else:
                            start_time = word_timestamp_list[0]['start']                     
                        split_index = None
                        second_line = False
                                       
                # add word to current sentence (list of words)
                word_list.append(word)
                word_timestamp_list.append(word_info)
                word_count += 1
                char_count += len(word)

                if start_time == None:
                    start_time = word_info['start']

                # if the word includes any punctuations, keep track of it's location in the 
                # current word list, update it if another one has been found
                if any(char in chars_to_check for char in word):
                    split_index = word_count - 1
                    
                if i == end_index:
                    sentence = ' '.join(word_list)                    
                    end_time = word_timestamp_list[-1]['end']
                    df = self.add_row(df, (start_time, end_time), sentence, word_timestamp_list)

            df['timestamp'] = df['timestamp'].apply(self.convert_time_span_to_webvtt)
            df.to_csv(sub_path, index=False)
            return df, 0

        except Exception as e:
            print(f"Error occurred when combining subtitles: {e}")
            traceback.print_exc()
            return None, -1

    def combine_words(self, transcript, max_words):
        try:
            print('Combining words from transcript...')
            words = transcript
            df = pd.DataFrame(columns=['timestamp', 'text', 'word_timestamp_list'])
            end_index = len(words) - 1
            word_list = []
            word_timestamp_list = []
            start_time = None
            word_count = 0
            split_index = None
            chars_to_check = {',', '?', '.'}

            for i, word_info in enumerate(words):
                # handle the case for numbers e.g. '1980' with no start or end timestamps                
                if 'start' not in word_info:
                    word_info = self.handle_abnormal_words(i, end_index, word_info, words)

                if start_time == None:
                    start_time = word_info['start']

                # add word to current sentence (list of words)
                word = word_info['word']
                word_list.append(word)
                word_timestamp_list.append(word_info)
                word_count += 1

                # if the word includes any punctuations, keep track of it's location in the 
                # current word list, update it if another one has been found
                if any(char in chars_to_check for char in word):
                    split_index = word_count - 1
                    
                # if the max word limit is reached or already reached, and if at least
                # one punctuation has been found, then end the sentence and start a new one
                if word_count >= max_words and split_index != None:                    
                    sentence = ' '.join(word_list[:split_index + 1])                
                    end_time = word_timestamp_list[split_index]['end']

                    df = self.add_row(df, (start_time, end_time), sentence, word_timestamp_list[:split_index + 1])

                    word_list = word_list[split_index + 1:]
                    word_count = len(word_list)
                    word_timestamp_list = word_timestamp_list[split_index + 1:]                    


                    # fix this, split index might not need to be reset?
                    split_index = None

                    # if after the split, there is still remaining words, update the starting time
                    # to that one in order to start a new sentence
                    if word_count != 0:
                        start_time = word_timestamp_list[0]['start']
                    else:
                        start_time = None
                elif i == end_index:
                    sentence = ' '.join(word_list)                    
                    end_time = word_timestamp_list[-1]['end']
                    df = self.add_row(df, (start_time, end_time), sentence, word_timestamp_list)
            return df, 0
        except Exception as e:
            print(f"Error occurred when combining words: {e}")
            traceback.print_exc()
            return None, -1
    
    def process(self, args):
        if args['run_analyze_text']:
            df_path = args['df_path']
            sub_path = args['sub_path']
            webvtt_path = args['webvtt_path']
            transcript_path = args['transcript_path']
            threshold_wpm = args['threshold_wpm']
            threshold_spm = args['threshold_spm']
            max_words = args['split_max']
            video_path = args['video_path']
            segments_path = args['segments_path']

            if os.path.exists(transcript_path):
                with open(transcript_path, 'r') as f:
                    transcript = json.load(f)

                df, status = self.combine_words(transcript, max_words)
                if status != 0:
                    return -1
            
                status = self.analyze_text(df, df_path, threshold_wpm, threshold_spm, video_path, segments_path)
                if status != 0:
                    return -1

                sub, status = self.combine_subtitle(sub_path, transcript)
                if status != 0:
                    return -1
                
                status = self.create_webvtt(sub, webvtt_path)
                if status != 0:
                    return -1
                
                return 0
            else:
                print('Transcript file does not exist')
                return -1
        else:
            print('Skip analyzing text')
            return 0
