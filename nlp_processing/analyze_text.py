from transformers import pipeline
# from textstat import textstat

def analyze_text(df):

    # df['complexity'] = df['text'].apply(flesch_reading_ease)
    df['wpm'] = df.apply(calcualte_wpm, axis=1)
    return df


# def flesch_reading_ease(text):
    score = textstat.flesch_reading_ease(text)
    return score

def calcualte_wpm(row):
    num_words = len(row['text'].split())
    duration_in_minute = (row['timestamp'][1] - row['timestamp'][0]) / 60
    # prevent division by 0
    duration_in_minute = max(duration_in_minute, 0.1)
    wpm = num_words / duration_in_minute
    return round(wpm, 2)


