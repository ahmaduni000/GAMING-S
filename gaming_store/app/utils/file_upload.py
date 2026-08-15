import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_unique_filename(filename):
    """Generate a unique filename using UUID."""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    unique_name = f"{uuid.uuid4().hex}_{uuid.uuid4().hex[:8]}.{ext}"
    return unique_name


def save_upload(file, subfolder, allowed_extensions=ALLOWED_IMAGE_EXTENSIONS, max_size=MAX_IMAGE_SIZE):
    """Save an uploaded file and return the relative path."""
    if not file or file.filename == '':
        return None

    if not allowed_file(file.filename, allowed_extensions):
        raise ValueError(f'File type not allowed. Allowed: {", ".join(allowed_extensions)}')

    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > max_size:
        raise ValueError(f'File too large. Maximum size: {max_size // (1024 * 1024)}MB')

    filename = generate_unique_filename(secure_filename(file.filename))
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    return f'uploads/{subfolder}/{filename}'


def delete_upload(filepath):
    """Delete an uploaded file."""
    if not filepath or filepath == 'default.png' or filepath.startswith('http'):
        return False
    full_path = os.path.join(current_app.static_folder, filepath)
    if os.path.exists(full_path):
        os.remove(full_path)
        return True
    return False


def get_image_url(path):
    """Get full image URL."""
    if not path:
        return '/static/images/default_product.png'
    if path.startswith('http'):
        return path
    return f'/static/{path}'
