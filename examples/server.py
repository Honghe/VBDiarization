# -*- coding: utf-8 -*-
import json
import logging
import os

from flask import Flask, request, send_from_directory, Response
from flask_autoindex import AutoIndex
from tinytag import TinyTag

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
AutoIndex(app, browse_root=os.path.curdir)

UPLOAD_FOLDER = 'upload'
app_path = os.path.dirname(os.path.abspath(__file__))
UPLOAD_PATH = os.path.join(app_path, UPLOAD_FOLDER)

os.makedirs(UPLOAD_PATH, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH

num_speakers = 4

def vad(task_path, uploaded_files_name, vad_path):
    tag = TinyTag.get(os.path.join(task_path, uploaded_files_name))
    os.makedirs(vad_path, exist_ok=True)
    with open(os.path.join(vad_path, os.path.splitext(uploaded_files_name)[0] + '.txt'), 'w') as f:
        f.write('0 {}'.format(tag.duration))


def create_list_scp(list_filepath, uploaded_files_name, num_speakers):
    with open(list_filepath, 'w') as f:
        f.write('{} {}'.format(os.path.splitext(uploaded_files_name)[0], num_speakers))


def diarization_task(task_path, task_id, uploaded_files_name, num_speakers):
    vad_path = os.path.join('vad', task_id)
    vad(task_path, uploaded_files_name, vad_path)
    list_filepath = 'lists/{}'.format(os.path.splitext(uploaded_files_name)[0])
    create_list_scp(list_filepath, uploaded_files_name, num_speakers)
    myCmd = '''python diarization.py -c ../configs/vbdiar.yml \
    -l {} \
    --audio-dir {} \
    --vad-dir {} \
    --mode diarization \
    --out-emb-dir embeddings \
    -vad-suffix .txt \
    --out-rttm-dir rttm'''.format(list_filepath, task_path, vad_path)
    logger.info(myCmd)
    out = os.popen(myCmd).read()
    logger.info(out)


def callback(arg):
    logger.info('callback {}'.format(arg))


def error_callback(arg):
    logger.info('error_callback')
    logger.error(arg)

def rttm2json(rttm):
    Json = []
    for line in rttm.split('\n'):
        if not line == '':
            result = line.split(' ')
            temp = {
                'start': float(result[3]),
                'end': round(float(result[3]) + float(result[4]), 3),
                'who': int(result[-2][-1])
            }
            Json.append(temp)

    return json.dumps(Json)


@app.route('/rttm/<path:path>', methods=['GET'])
def static_rttm(path):
    # return send_file(os.path.join('rttm', path), mimetype='text/plain')
    return send_from_directory(directory='rttm', filename=path, mimetype='text/plain')


@app.route("/index", methods=['POST', 'GET'])
def nlp_upload():
    logger.info('request form {}'.format(request.form))
    # request files ImmutableMultiDict([('file', <FileStorage: '1553152914016.mp3' ('application/octet-stream')>),
    # ('step', <FileStorage: 'data_step_1553152914016.json' ('application/octet-stream')>)])
    logger.info('request files {}'.format(request.files))
    if request.method == 'POST':
        num_speakers = int(request.form['speaker_numbers'])
        logger.info('num_speakers {}'.format(num_speakers))
        uploaded_files_name = {}
        for file_key in request.files:
            file = request.files[file_key]
            if file:
                filename = file.filename
                uploaded_files_name[file_key] = filename
                file_basename = os.path.splitext(filename)[0]
                task_path = os.path.join(app.config['UPLOAD_FOLDER'], file_basename)
                os.makedirs(task_path, exist_ok=True)
                uploaded_file_path = os.path.join(task_path, filename)
                file.save(uploaded_file_path)
                logger.info('save file: {}'.format(
                    json.dumps({'filename': filename, 'task_id': file_basename, 'path': task_path},
                               ensure_ascii=False)))

        diarization_task(task_path, file_basename, filename, num_speakers)

        rttm_file_name = os.path.splitext(filename)[0] + '.rttm'
        with open(os.path.join('rttm', rttm_file_name)) as f:
            rttm = f.read()
        return Response(rttm2json(rttm),
                        mimetype='application/json'
                        )
        # not work
        # redirect(os.path.join('rttm', os.path.splitext(filename)[0] + '.rttm'))

    return '''
    <!doctype html>
    <title>Speaker Diarization</title>
    <h1>Speaker Diarization</h1>
    <p>Note: only support wav file with 16k samplerate & 16bits width.</p>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file><br/><br/>
      <label>speaker_number:</label>
      <input type=text name=speaker_numbers value="4"><br/><br/>
      <input type=submit value='Upload&Diarization'>
    </form>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001, threaded=True)
