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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_images():
    try:
        files = request.files.getlist('files')
        quality = int(request.form.get('quality', 75))  # Default quality to 75 if not provided
        resolution = int(request.form.get('resolution', 100))  # Default resolution to 100% if not provided

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
