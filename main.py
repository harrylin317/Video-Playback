import time
import os
import json
from processing.extract_audio import ExtractAudio
from processing.audio_to_text import AudioToText
from processing.analyze_text import AnalyzeText
from pipeline.pipeline import Pipeline
from processing.launch_video import LaunchVideo
from flask import Flask, render_template, request, redirect, url_for, send_from_directory



app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'video_uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'wmv'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def execute_pipeline(filename, segment_len, max_wpm):
    # video_number = '2'

    save_path = f'outputs/output_{os.path.splitext(filename)[0]}/'
    # save_path = f'outputs/output_{video_number}/'

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    args = {
        "video_path" : os.path.join(app.config['UPLOAD_FOLDER'], filename),
        # "video_path" : f"video_{video_number}.mp4",
        "audio_path" : os.path.join(save_path, "audio.wav"),
        "df_path" : os.path.join(save_path, "text.csv"),
        "transcript_path" : os.path.join(save_path, "transcript.json"),
        "output_path" : os.path.join(save_path, "output.mp4"),
        "segments_path" : os.path.join(save_path, "segments.json"),
        "split_max" : segment_len,
        "threshold_wpm" : max_wpm,
        "run_extract_audio" : False,
        "run_audio_to_text": False,  
        "run_analyze_text": True   
        # "run_process_video": False,
        # "run_video_player" : False 
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
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('show_video', filename=filename, segment_len=segment_len, max_wpm=max_wpm))
    return redirect(request.url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/show_video')
def show_video():
    filename = request.args.get('filename')
    segment_len = int(request.args.get('segment_len'))
    max_wpm = int(request.args.get('max_wpm'))
    segments = execute_pipeline(filename, segment_len, max_wpm)
    # return render_template('show_video.html', filename=filename, segments=segments)
    return render_template('play_video.html', filename=filename, segments=segments)

if __name__ == "__main__":
    app.run(debug=True)
    #execute_pipeline()



       



    
    
