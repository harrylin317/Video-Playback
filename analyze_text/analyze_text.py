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
    
    # def flesch_reading_ease(text):
    #     score = textstat.flesch_reading_ease(text)
    #     return score

    def analyze_text(self, df, df_path, threshold_wpm):
        try:
            print('Analyzing text...')
            # df['complexity'] = df['text'].apply(flesch_reading_ease)
            df['wpm'] = df.apply(self.calculate_wpm, threshold_wpm=threshold_wpm, axis=1)
            df.to_csv(df_path, index=False)
            print('Successfully analyzed text, Dataframe file created')
            return 0
        except Exception as e:
            print(f"Error occurred when analyzing text: {e}")
            traceback.print_exc()
            return -1
    
    def combine_words(self, transcript):
        try:
            print('Combining words from transcript...')
            words = transcript
            sentence = ""
            start_time = words[0]['start']
            # sentence_end_chars = {'.', '!', '?'}

            df = pd.DataFrame(columns=['timestamp', 'text'])
            end_index = len(words) - 1
            for i, word_info in enumerate(words):
                # if last word was the end of sentence, initialize starting timestamp
                if start_time == None:
                    start_time = word_info['start']

                # append word to sentence
                word = word_info['word']
                sentence = sentence + ' ' + word

                # (removed) if word ends with '.', '!', '?' stop the sentence, add to df, start a new sentence
                # if there has been 15 words in the sentence, end the sentence
                # if word is the last word in the transcript, end the sentence as well
                # if word[-1] in sentence_end_chars or i == end_index:
                if (i + 1) % 15 == 0 or i == end_index:
                    end_time = word_info['end']
                    new_row = pd.DataFrame({'timestamp': [(start_time, end_time)], 'text': [sentence.strip()]})
                    df = pd.concat([df, new_row], ignore_index=True)
                    sentence = ""
                    start_time = None
                
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
            if os.path.exists(transcript_path):
                with open(transcript_path, 'r') as f:
                    transcript = json.load(f)

                df, status = self.combine_words(transcript)
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
