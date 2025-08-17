from flask import Flask, request, send_file
import subprocess
import os
import tempfile

app = Flask(__name__)

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
    
    # Trim with FFmpeg (stream copy for speed)
    output_path = tempfile.mktemp(suffix='.webm')
    try:
        subprocess.run([
            'ffmpeg', '-i', input_path, '-to', trim_time, '-c', 'copy', output_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        os.remove(input_path)
        return f'FFmpeg error: {e}', 500
    
    # Send trimmed file back
    response = send_file(output_path, mimetype='video/webm', as_attachment=True, download_name='trimmed.webm')
    
    # Cleanup
    os.remove(input_path)
    os.remove(output_path)
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
