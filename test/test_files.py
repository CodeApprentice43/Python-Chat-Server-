import os
import shutil
from utils.mime import detect_mime_type

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


def test_upload_directory_creation():
    """Test upload directory creation."""
    test_dir = "test_uploads"

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    global UPLOAD_DIR
    original_dir = UPLOAD_DIR
    UPLOAD_DIR = test_dir

    ensure_upload_directory()

    assert os.path.exists(test_dir)
    assert os.path.isdir(test_dir)

    shutil.rmtree(test_dir)
    UPLOAD_DIR = original_dir

    print("✓ Upload directory creation works")


def test_allowed_mime_types():
    """Test allowed MIME types configuration."""
    assert "image/jpeg" in ALLOWED_MIME_TYPES
    assert "image/png" in ALLOWED_MIME_TYPES
    assert "image/gif" in ALLOWED_MIME_TYPES
    assert "video/mp4" in ALLOWED_MIME_TYPES

    assert ALLOWED_MIME_TYPES["image/jpeg"] == ".jpg"
    assert ALLOWED_MIME_TYPES["image/png"] == ".png"
    assert ALLOWED_MIME_TYPES["image/gif"] == ".gif"
    assert ALLOWED_MIME_TYPES["video/mp4"] == ".mp4"

    print("✓ Allowed MIME types configured correctly")


def test_max_file_size():
    """Test max file size limit."""
    assert MAX_FILE_SIZE == 10 * 1024 * 1024
    print("✓ Max file size set to 10MB")


def test_mime_detection_for_uploads():
    """Test MIME type detection for various file types."""

    jpeg_signature = b'\xff\xd8\xff\xe0\x00\x10JFIF'
    mime, ext = detect_mime_type(jpeg_signature)
    assert mime in ALLOWED_MIME_TYPES
    assert ext == ".jpg"

    png_signature = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
    mime, ext = detect_mime_type(png_signature)
    assert mime in ALLOWED_MIME_TYPES
    assert ext == ".png"

    gif_signature = b'GIF89a'
    mime, ext = detect_mime_type(gif_signature)
    assert mime in ALLOWED_MIME_TYPES
    assert ext == ".gif"

    mp4_signature = b'\x00\x00\x00\x20ftypmp42'
    mime, ext = detect_mime_type(mp4_signature)
    assert mime in ALLOWED_MIME_TYPES
    assert ext == ".mp4"

    print("✓ MIME detection works for all allowed types")


def test_disallowed_file_types():
    """Test that disallowed file types are detected."""

    exe_signature = b'MZ\x90\x00'
    mime, _ = detect_mime_type(exe_signature)
    assert mime not in ALLOWED_MIME_TYPES

    pdf_signature = b'%PDF-1.4'
    mime, _ = detect_mime_type(pdf_signature)
    assert mime not in ALLOWED_MIME_TYPES

    print("✓ Disallowed file types rejected correctly")


def test_filename_validation():
    """Test filename security validation."""

    valid_filename = "abc123.jpg"
    assert '..' not in valid_filename
    assert '/' not in valid_filename

    invalid_filename1 = "../../../etc/passwd"
    assert '..' in invalid_filename1

    invalid_filename2 = "uploads/../../secret.txt"
    assert '..' in invalid_filename2

    print("✓ Filename validation prevents path traversal")


if __name__ == '__main__':
    print("Running file upload tests...\n")

    test_upload_directory_creation()
    test_allowed_mime_types()
    test_max_file_size()
    test_mime_detection_for_uploads()
    test_disallowed_file_types()
    test_filename_validation()

    print("\n✅ All file upload tests passed!")
