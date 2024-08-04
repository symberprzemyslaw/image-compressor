from flask import Flask, request, send_file, render_template
from PIL import Image
import os
import zipfile
import tempfile
import traceback
import logging

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
COMPRESSED_FOLDER = 'compressed/'

# Ensure upload and compressed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

MAX_FILES = 100
MAX_SIZE = 0.5 * 1024 * 1024 * 1024  # 0.5 GB in bytes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compress', methods=['GET', 'POST'])
def compress_images():
    try:
        files = request.files.getlist('files')
        quality = int(request.form.get('quality', 30))  # Default quality to 30 if not provided
        resolution = int(request.form.get('resolution', 50))  # Default resolution to 50% if not provided

        logger.info(f'Received {len(files)} files for compression with quality={quality} and resolution={resolution}%')

        if len(files) > MAX_FILES:
            logger.error('Too many files. Maximum allowed is 100.')
            return 'Too many files. Maximum allowed is 100.', 400

        total_size = sum(file.content_length for file in files)
        logger.info(f'Total upload size: {total_size} bytes')

        if total_size > MAX_SIZE:
            logger.error('Total file size exceeds the limit of 0.5 GB.')
            return 'Total file size exceeds the limit of 0.5 GB.', 400

        # Use a temporary directory to store compressed files
        with tempfile.TemporaryDirectory() as tmpdirname:
            compressed_zip_path = os.path.join(tmpdirname, 'compressed_images.zip')

            with zipfile.ZipFile(compressed_zip_path, 'w') as zf:
                for file in files:
                    original_file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                    file.save(original_file_path)
                    logger.info(f'File saved to {original_file_path}')

                    try:
                        # Open and compress the image
                        img = Image.open(original_file_path)
                        img = img.resize((int(img.width * (resolution / 100)), int(img.height * (resolution / 100))), Image.LANCZOS)
                        compressed_file_path = os.path.join(tmpdirname, 'compressed_' + file.filename)
                        img.save(compressed_file_path, 'JPEG', quality=quality)

                        # Add the compressed image to the zip file
                        zf.write(compressed_file_path, 'compressed_' + file.filename)
                        logger.info(f'File {file.filename} compressed and added to zip')

                    except Exception as img_ex:
                        logger.error(f'Error processing image {file.filename}: {img_ex}')
                        continue  # Skip this file and continue with the next one

                    # Clean up the uploaded file
                    os.remove(original_file_path)
                    logger.info(f'Original file {original_file_path} removed')

            return send_file(compressed_zip_path, mimetype='application/zip', as_attachment=True, download_name='compressed_images.zip')

    except Exception as e:
        logger.error(f'Exception in /compress: {e}')
        traceback.print_exc()  # Log the exception traceback
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
