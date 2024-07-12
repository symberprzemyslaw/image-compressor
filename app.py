from flask import Flask, request, send_file, render_template
from PIL import Image
import os
import io
import zipfile
import traceback

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
COMPRESSED_FOLDER = 'compressed/'

# Ensure upload and compressed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

MAX_FILES = 100
MAX_SIZE = 0.5 * 1024 * 1024 * 1024  # 0.5 GB in bytes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compress', methods=['GET', 'POST'])
def compress_images():
    try:
        files = request.files.getlist('files')
        quality = int(request.form.get('quality', 30))  # Default quality to 30 if not provided
        resolution = int(request.form.get('resolution', 50))  # Default resolution to 50% if not provided

        if len(files) > MAX_FILES:
            return 'Too many files. Maximum allowed is 100.', 400

        total_size = sum(file.content_length for file in files)
        if total_size > MAX_SIZE:
            return 'Total file size exceeds the limit of 0.5 GB.', 400

        compressed_io = io.BytesIO()
        with zipfile.ZipFile(compressed_io, 'w') as zf:
            for file in files:
                original_file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(original_file_path)

                # Open and compress the image
                img = Image.open(original_file_path)
                img = img.resize((int(img.width * (resolution / 100)), int(img.height * (resolution / 100))), Image.LANCZOS)
                output_io = io.BytesIO()
                img.save(output_io, 'JPEG', quality=quality)
                output_io.seek(0)

                # Add the compressed image to the zip file
                zf.writestr('compressed_' + file.filename, output_io.read())

                # Clean up the uploaded file
                os.remove(original_file_path)

        compressed_io.seek(0)
        return send_file(compressed_io, mimetype='application/zip', as_attachment=True, download_name='compressed_images.zip')

    except Exception as e:
        traceback.print_exc()  # Log the exception traceback
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
