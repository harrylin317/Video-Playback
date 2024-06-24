import time
import os
import json
from processing.extract_audio import ExtractAudio
from processing.audio_to_text import AudioToText
from processing.analyze_text import AnalyzeText
from pipeline.pipeline import Pipeline
from flask import Flask, render_template, request, redirect, url_for, send_from_directory



app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'video_uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'wmv'}
app.config['OUTPUT_FOLDER'] = 'outputs/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def execute_pipeline(filename, segment_len, max_wpm, max_spm):
    # video_number = '2'

    app.config['OUTPUT_FOLDER'] = os.path.join('outputs/', f'output_{os.path.splitext(filename)[0]}/')
    print(f"filename {os.path.splitext(filename)[0]}") 
    print(f"output path {app.config['OUTPUT_FOLDER']}") 
    # app.config['OUTPUT_FOLDER'] = f'outputs/output_{video_number}/'

    if not os.path.exists(app.config['OUTPUT_FOLDER']):
        os.makedirs(app.config['OUTPUT_FOLDER'])

    args = {
        "video_path" : os.path.join(app.config['UPLOAD_FOLDER'], filename),
        # "video_path" : f"video_{video_number}.mp4",
        "audio_path" : os.path.join(app.config['OUTPUT_FOLDER'], "audio.wav"),
        "df_path" : os.path.join(app.config['OUTPUT_FOLDER'], "text.csv"),
        "sub_path" : os.path.join(app.config['OUTPUT_FOLDER'], "sub.csv"),
        "webvtt_path" : os.path.join(app.config['OUTPUT_FOLDER'], "subtitles.vtt"),
        "transcript_path" : os.path.join(app.config['OUTPUT_FOLDER'], "transcript.json"),
        "segments_path" : os.path.join(app.config['OUTPUT_FOLDER'], "segments.json"),
        "split_max" : segment_len,
        "threshold_wpm" : max_wpm,
        "threshold_spm" : max_spm,
        "run_extract_audio" : False,
        "run_audio_to_text": False,  
        "run_analyze_text": True   
    }
    start_time = time.time()
    # pipeline = Pipeline([ExtractAudio(), AudioToText(), AnalyzeText(), LaunchVideo()])
    pipeline = Pipeline([ExtractAudio(), AudioToText(), AnalyzeText()])
    status = pipeline.run(args)
    if status != 0:
        print('Exiting program...')
        exit()
    with open(args['segments_path']) as json_file:
        segments = json.load(json_file)

    print('All process finished')
    end_time = time.time()
    runtime = end_time - start_time
    print("Runtime:", runtime, "seconds")

    return segments

    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)  # Redirect if no file part in the request
    file = request.files['file']  # Get the file from request.files
    if file.filename == '':
        return redirect(request.url)  # Redirect if no file is selected
    if file and allowed_file(file.filename):
        filename = file.filename
        segment_len = request.form.get('hiddenSegmentValue')
        max_wpm = request.form.get('hiddenWpmValue')
        max_spm = request.form.get('hiddenSpmValue')
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('play_video', filename=filename, segment_len=segment_len, max_wpm=max_wpm, max_spm=max_spm))
    return redirect(request.url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/output_files/<filename>')
def output_files(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/play_video')
def play_video():
    filename = request.args.get('filename')
    segment_len = int(request.args.get('segment_len'))
    max_wpm = int(request.args.get('max_wpm'))
    max_spm = int(request.args.get('max_spm'))
    segments = execute_pipeline(filename, segment_len, max_wpm, max_spm)
    return render_template('play_video.html', filename=filename, segments=segments)

if __name__ == "__main__":
    app.run(debug=True)
    # execute_pipeline("video_1.mp4", 20, 170, 240)



       



    
    
