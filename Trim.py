from flask import Flask, request, send_file
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Path to store uploaded videos temporarily
UPLOAD_FOLDER = 'uploads'
TRIMMED_FOLDER = 'trimmed_videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRIMMED_FOLDER, exist_ok=True)

# Limit file size (optional)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit


@app.route('/trim_video', methods=['POST'])
def trim_video():
    if 'video' not in request.files:
        return 'No video file uploaded', 400

    video = request.files['video']
    start_time = request.form['start']
    end_time = request.form['end']

    # Secure the filename and save the file temporarily
    video_filename = secure_filename(video.filename)
    video_path = os.path.join(UPLOAD_FOLDER, video_filename)
    video.save(video_path)

    # Define output file path
    output_filename = f"trimmed_{video_filename}"
    output_path = os.path.join(TRIMMED_FOLDER, output_filename)

    # Use FFmpeg to trim the video
    command = [
        'ffmpeg',
        '-i', video_path,
        '-ss', start_time,
        '-to', end_time,
        '-c', 'copy',
        output_path
    ]

    # Run the FFmpeg command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        return f"Error processing video: {str(e)}", 500

    # Return the trimmed video file
    return send_file(output_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
