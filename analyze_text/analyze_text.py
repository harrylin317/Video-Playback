# from textstat import textstat
import pandas as pd
import json
import os
import traceback

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

    def analyze_text(self, df, df_path, threshold_wpm):
        try:
            print('Analyzing text...')
            df['wpm'] = df.apply(self.calculate_wpm, threshold_wpm=threshold_wpm, axis=1)
            # calculate slow ratio. Equals 1 if not need slowing
            # df['slow_ratio'] = df['wpm'].apply(lambda wpm: (threshold_wpm/wpm) if wpm > threshold_wpm else 1)
            df['slow_ratio'] = df['wpm'].apply(lambda wpm: round((wpm/threshold_wpm), 2) if wpm > threshold_wpm else 1)
            df['time+slow'] = df.apply(lambda row : self.combine_tuples(row), axis=1)
            df.to_csv(df_path, index=False)
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
            if os.path.exists(transcript_path):
                with open(transcript_path, 'r') as f:
                    transcript = json.load(f)

                df, status = self.combine_words(transcript, split_max)
                if status != 0:
                    return -1

                status = self.analyze_text(df, df_path, threshold_wpm)
                if status != 0:
                    return -1
                
                return 0
            else:
                print('Transcript file does not exist')
                return -1
        else:
            print('Skip analyzing text')
            return 0
