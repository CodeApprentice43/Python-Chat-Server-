from core.request import Request
from utils.multipart import parse_multipart


def test_simple_text_fields():
    raw_request = b'POST /upload HTTP/1.1\r\n' \
                  b'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary\r\n' \
                  b'\r\n' \
                  b'------WebKitFormBoundary\r\n' \
                  b'Content-Disposition: form-data; name="username"\r\n' \
                  b'\r\n' \
                  b'john_doe\r\n' \
                  b'------WebKitFormBoundary\r\n' \
                  b'Content-Disposition: form-data; name="email"\r\n' \
                  b'\r\n' \
                  b'john@example.com\r\n' \
                  b'------WebKitFormBoundary--\r\n'

    request = Request(raw_request)
    multipart = parse_multipart(request)

    assert len(multipart.parts) == 2
    assert multipart.parts[0].name == "username"
    assert multipart.parts[0].content.strip() == b"john_doe"
    assert multipart.parts[1].name == "email"
    assert multipart.parts[1].content.strip() == b"john@example.com"
    print("✓ test_simple_text_fields passed")


def test_file_upload():
    raw_request = b'POST /upload HTTP/1.1\r\n' \
                  b'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary\r\n' \
                  b'\r\n' \
                  b'------WebKitFormBoundary\r\n' \
                  b'Content-Disposition: form-data; name="file"; filename="test.txt"\r\n' \
                  b'Content-Type: text/plain\r\n' \
                  b'\r\n' \
                  b'File contents here\r\n' \
                  b'------WebKitFormBoundary--\r\n'

    request = Request(raw_request)
    multipart = parse_multipart(request)

    assert len(multipart.parts) == 1
    assert multipart.parts[0].name == "file"
    assert multipart.parts[0].filename == "test.txt"
    assert multipart.parts[0].content.strip() == b"File contents here"
    print("✓ test_file_upload passed")


def test_mixed_fields_and_file():
    raw_request = b'POST /upload HTTP/1.1\r\n' \
                  b'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary\r\n' \
                  b'\r\n' \
                  b'------WebKitFormBoundary\r\n' \
                  b'Content-Disposition: form-data; name="description"\r\n' \
                  b'\r\n' \
                  b'My photo\r\n' \
                  b'------WebKitFormBoundary\r\n' \
                  b'Content-Disposition: form-data; name="photo"; filename="photo.jpg"\r\n' \
                  b'Content-Type: image/jpeg\r\n' \
                  b'\r\n' \
                  b'\xff\xd8\xff\xe0\x00\x10JFIF\r\n' \
                  b'------WebKitFormBoundary--\r\n'

    request = Request(raw_request)
    multipart = parse_multipart(request)

    assert len(multipart.parts) == 2
    assert multipart.parts[0].name == "description"
    assert multipart.parts[0].filename is None
    assert multipart.parts[1].name == "photo"
    assert multipart.parts[1].filename == "photo.jpg"
    assert multipart.parts[1].headers.get('Content-Type') == "image/jpeg"
    print("✓ test_mixed_fields_and_file passed")


def test_boundary_extraction():
    raw_request = b'POST /upload HTTP/1.1\r\n' \
                  b'Content-Type: multipart/form-data; boundary=MyCustomBoundary123\r\n' \
                  b'\r\n' \
                  b'--MyCustomBoundary123\r\n' \
                  b'Content-Disposition: form-data; name="field"\r\n' \
                  b'\r\n' \
                  b'value\r\n' \
                  b'--MyCustomBoundary123--\r\n'

    request = Request(raw_request)
    multipart = parse_multipart(request)

    assert multipart.boundary == "MyCustomBoundary123"
    print("✓ test_boundary_extraction passed")


def test_multiple_files():
    raw_request = b'POST /upload HTTP/1.1\r\n' \
                  b'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary\r\n' \
                  b'\r\n' \
                  b'------WebKitFormBoundary\r\n' \
                  b'Content-Disposition: form-data; name="file1"; filename="doc1.txt"\r\n' \
                  b'Content-Type: text/plain\r\n' \
                  b'\r\n' \
                  b'Document 1\r\n' \
                  b'------WebKitFormBoundary\r\n' \
                  b'Content-Disposition: form-data; name="file2"; filename="doc2.txt"\r\n' \
                  b'Content-Type: text/plain\r\n' \
                  b'\r\n' \
                  b'Document 2\r\n' \
                  b'------WebKitFormBoundary--\r\n'

    request = Request(raw_request)
    multipart = parse_multipart(request)

    assert len(multipart.parts) == 2
    assert multipart.parts[0].filename == "doc1.txt"
    assert multipart.parts[1].filename == "doc2.txt"
    print("✓ test_multiple_files passed")


if __name__ == "__main__":
    print("Running Multipart Parser Tests...\n")

    test_simple_text_fields()
    test_file_upload()
    test_mixed_fields_and_file()
    test_boundary_extraction()
    test_multiple_files()

    print("\n✅ All 5 multipart tests passed!")
