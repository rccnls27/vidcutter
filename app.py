from flask import Flask, request, send_file
import subprocess
import os
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # Limit uploads to 2GB

@app.route('/', methods=['GET'])
def home():
    return "VidCutter API is running! Use POST /trim with 'video' file and 'trim_time' param."

@app.route('/trim', methods=['POST'])
def trim_video():
    if 'video' not in request.files:
        return 'No video file', 400
    
    file = request.files['video']
    trim_time = request.form.get('trim_time')
    if not trim_time:
        return 'No trim_time provided', 400
    
    # Save uploaded file temporarily
    input_path = tempfile.mktemp(suffix='.webm')
    file.save(input_path)
    
    # Trim with FFmpeg (re-encode for arbitrary timestamps)
    output_path = tempfile.mktemp(suffix='.webm')
    try:
        subprocess.run([
            'ffmpeg', '-i', input_path, '-to', trim_time,
            '-c:v', 'libvpx', '-c:a', 'libopus', '-crf', '10', '-b:v', '2M',
            output_path
        ], check=True, capture_output=True, text=True)  # Capture output for debugging
    except subprocess.CalledProcessError as e:
        os.remove(input_path)
        return f'FFmpeg error: {e.stderr}', 500
    
    # Send trimmed file back
    response = send_file(output_path, mimetype='video/webm', as_attachment=True, download_name='trimmed.webm')
    
    # Cleanup
    os.remove(input_path)
    os.remove(output_path)
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
