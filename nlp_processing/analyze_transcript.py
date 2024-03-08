from transformers import pipeline
from textstat import textstat

def analyze_transcript(df):

    df['complexity'] = df['text'].apply(flesch_reading_ease)
    return df

    # chunks = transcript['chunks']
    # candidate_labels = ['very easy', 'easy', 'faily easy', 'standard', 'fairly difficult', 'difficult', 'very difficult']
    # classifier = pipeline('zero-shot-classification', model='roberta-large-mnli')
    # for chunk in chunks:
    #     # print(segment)
    #     print("[%s -> %s] %s" % (chunk['timestamp'][0], chunk['timestamp'][1], chunk['text']))
    #     prediction = classifier(chunk['text'], candidate_labels)
    #     scores = prediction['scores']
    #     max_index = scores.index(max(scores))
    #     print(prediction['labels'][max_index], scores[max_index])
    return

def flesch_reading_ease(text):
    score = textstat.flesch_reading_ease(text)
    return score

        

