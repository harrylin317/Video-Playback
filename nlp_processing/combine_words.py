import pandas as pd

def combine_words(transcript):
    words = transcript['chunks']
    sentence = ""
    start_time = words[0]['timestamp'][0]
    sentence_end_chars = {'.', '!', '?'}

    df = pd.DataFrame(columns=['timestamp', 'text'])
    end_index = len(words) - 1
    for i, word_info in enumerate(words):
        # if last word was the end of sentence, initialize starting timestamp
        if start_time == None:
            start_time = word_info['timestamp'][0]

        # append word to sentence
        word = word_info['text']
        sentence += word

        # if word ends with '.', '!', '?' stop the sentence, add to df, start a new sentence
        # if word is the last word in the transcript, end the sentence as well
        if word[-1] in sentence_end_chars or i == end_index:
            end_time = word_info['timestamp'][1]
            new_row = pd.DataFrame({'timestamp': [(start_time, end_time)], 'text': [sentence.strip()]})
            df = pd.concat([df, new_row], ignore_index=True)
            sentence = ""
            start_time = None
        
    # df.to_csv(df_path, index=False)
    return df

# def convert_to_csv(transcript, transcript_path):
#     df = pd.DataFrame(columns=['timestamp', 'text'])
#     chunks = transcript['chunks']
#     for chunk in chunks:
#         new_row = pd.DataFrame({'timestamp': [chunk['timestamp']], 'text': [chunk['text']]})
#         df = pd.concat([df, new_row], ignore_index=True)
#     df.to_csv(transcript_path, index=False)