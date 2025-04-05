from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
from video_processor import VideoProcessor

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Initialize video processor with your API key
ROBOFLOW_API_KEY = "M7ETWiWTqM9MM7LKVIaZ"  
video_processor = VideoProcessor(ROBOFLOW_API_KEY)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        upload_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{filename}")
        processed_filename = f"processed_{unique_id}_{filename}"
        processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
        
        # Save uploaded file
        file.save(upload_path)
        
        try:
            # Process the video
            video_processor.process_video(upload_path, processed_path)
            
            return jsonify({
                'message': 'Video processed successfully',
                'processed_video_url': f'/processed/{processed_filename}'
            })
        except Exception as e:
            return jsonify({'error': f'Video processing failed: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)