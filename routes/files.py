import os
import uuid
from core.router import Router
from core.response import Response
from app.middleware.auth import require_auth
from utils.multipart import parse_multipart
from utils.mime import detect_mime_type

router = Router()

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "video/mp4": ".mp4"
}


def ensure_upload_directory():
    """Ensure upload directory exists."""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)


@router.post('/upload-file')
@require_auth
def handle_file_upload(request):
    """Handle file upload.

    Requires authentication.

    Expects multipart/form-data with:
        - file: binary file data

    Returns:
        201 Created with file metadata
        400 Bad Request if validation fails
        413 Payload Too Large if file exceeds limit
    """
    try:
        content_type = None
        for name, value in request.headers.items():
            if name.lower() == 'content-type':
                content_type = value
                break

        if not content_type or not content_type.startswith('multipart/form-data'):
            response = Response.bad_request(b"Expected multipart/form-data")
            return response.to_bytes()

        boundary_parts = content_type.split('boundary=')
        if len(boundary_parts) < 2:
            response = Response.bad_request(b"Missing boundary in Content-Type")
            return response.to_bytes()

        boundary = boundary_parts[1].strip()

        multipart = parse_multipart(request)

        print(f"Found {len(multipart.parts)} parts")
        for part in multipart.parts:
            print(f"Part name: {part.name}, filename: {part.filename}")

        file_part = None
        for part in multipart.parts:
            if part.name == 'file' and part.filename:
                file_part = part
                break

        if not file_part:
            print("No file part found with name='file' and filename")
            response = Response.bad_request(b"No file provided")
            return response.to_bytes()

        if len(file_part.content) > MAX_FILE_SIZE:
            response = Response()
            response.status(413)
            response.text("File size exceeds 10MB limit")
            return response.to_bytes()

        detected_mime, detected_ext = detect_mime_type(file_part.content)

        if detected_mime not in ALLOWED_MIME_TYPES:
            response = Response.bad_request(
                f"File type not allowed. Only images (JPEG, PNG, GIF) and MP4 videos are permitted.".encode()
            )
            return response.to_bytes()

        ensure_upload_directory()

        file_id = str(uuid.uuid4())
        file_extension = ALLOWED_MIME_TYPES[detected_mime]
        filename = f"{file_id}{file_extension}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, 'wb') as f:
            f.write(file_part.content)

        file_metadata = {
            'id': file_id,
            'filename': filename,
            'original_filename': file_part.filename,
            'mime_type': detected_mime,
            'size': len(file_part.content),
            'url': f"/uploads/{filename}",
            'uploaded_by': request.user
        }

        response = Response()
        response.status(201)
        response.json(file_metadata)
        return response.to_bytes()

    except Exception as e:
        response = Response.server_error(f"File upload failed: {str(e)}".encode())
        return response.to_bytes()


@router.get('/uploads/{filename}')
def handle_file_download(request):
    """Serve uploaded files.

    Returns:
        200 OK with file content
        404 Not Found if file doesn't exist
    """
    try:
        filename = request.path_params.get('filename')

        if not filename:
            response = Response.not_found(b"File not found")
            return response.to_bytes()

        if '..' in filename or '/' in filename:
            response = Response.bad_request(b"Invalid filename")
            return response.to_bytes()

        filepath = os.path.join(UPLOAD_DIR, filename)

        if not os.path.exists(filepath):
            response = Response.not_found(b"File not found")
            return response.to_bytes()

        with open(filepath, 'rb') as f:
            file_content = f.read()

        mime_type, _ = detect_mime_type(file_content)

        response = Response()
        response.status(200)
        response.set_header("Content-Type", mime_type)
        response.set_header("Cache-Control", "public, max-age=31536000")
        response.body = file_content
        return response.to_bytes()

    except Exception as e:
        response = Response.server_error(f"File retrieval failed: {str(e)}".encode())
        return response.to_bytes()
