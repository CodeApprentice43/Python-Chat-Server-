from core.response import Response


def test_basic_response():
    response = Response()
    response.text("Hello World")
    result = response.to_bytes()

    assert b"HTTP/1.1 200 OK" in result
    assert b"Content-Type: text/plain; charset=utf-8" in result
    assert b"Content-Length: 11" in result
    assert b"X-Content-Type-Options: nosniff" in result
    assert b"Hello World" in result
    print("✓ test_basic_response passed")


def test_json_response():
    response = Response()
    response.json({"message": "Hello", "status": "ok"})
    result = response.to_bytes()

    assert b"HTTP/1.1 200 OK" in result
    assert b"Content-Type: application/json; charset=utf-8" in result
    assert b'"message": "Hello"' in result
    assert b'"status": "ok"' in result
    print("✓ test_json_response passed")


def test_html_response():
    response = Response()
    response.html("<h1>Hello</h1>")
    result = response.to_bytes()

    assert b"HTTP/1.1 200 OK" in result
    assert b"Content-Type: text/html; charset=utf-8" in result
    assert b"<h1>Hello</h1>" in result
    print("✓ test_html_response passed")


def test_status_change():
    response = Response()
    response.status(404)
    response.text("Not Found")
    result = response.to_bytes()

    assert b"HTTP/1.1 404 Not Found" in result
    assert b"Not Found" in result
    print("✓ test_status_change passed")


def test_custom_headers():
    response = Response()
    response.set_header("X-Custom-Header", "CustomValue")
    response.text("Test")
    result = response.to_bytes()

    assert b"X-Custom-Header: CustomValue" in result
    print("✓ test_custom_headers passed")


def test_set_cookie():
    response = Response()
    response.set_cookie("session", "abc123", http_only=True, secure=True, max_age=3600)
    response.text("Cookie Set")
    result = response.to_bytes()

    assert b"Set-Cookie: session=abc123" in result
    assert b"HttpOnly" in result
    assert b"Secure" in result
    assert b"Max-Age=3600" in result
    assert b"Path=/" in result
    print("✓ test_set_cookie passed")


def test_delete_cookie():
    response = Response()
    response.delete_cookie("session")
    response.text("Cookie Deleted")
    result = response.to_bytes()

    assert b"Set-Cookie: session=" in result
    assert b"Max-Age=0" in result
    print("✓ test_delete_cookie passed")


def test_multiple_cookies():
    response = Response()
    response.set_cookie("auth", "token1")
    response.set_cookie("theme", "dark")
    response.text("Multiple Cookies")
    result = response.to_bytes()

    assert b"Set-Cookie: auth=token1" in result
    assert b"Set-Cookie: theme=dark" in result
    print("✓ test_multiple_cookies passed")


def test_factory_ok():
    response = Response.ok(b"Success")
    result = response.to_bytes()

    assert b"HTTP/1.1 200 OK" in result
    assert b"Success" in result
    print("✓ test_factory_ok passed")


def test_factory_not_found():
    response = Response.not_found(b"Page Not Found")
    result = response.to_bytes()

    assert b"HTTP/1.1 404 Not Found" in result
    assert b"Page Not Found" in result
    print("✓ test_factory_not_found passed")


def test_factory_bad_request():
    response = Response.bad_request(b"Invalid Input")
    result = response.to_bytes()

    assert b"HTTP/1.1 400 Bad Request" in result
    assert b"Invalid Input" in result
    print("✓ test_factory_bad_request passed")


def test_factory_server_error():
    response = Response.server_error(b"Server Error")
    result = response.to_bytes()

    assert b"HTTP/1.1 500 Internal Server Error" in result
    assert b"Server Error" in result
    print("✓ test_factory_server_error passed")


def test_builder_chaining():
    response = Response().status(201).text("Created").set_header("Location", "/users/123")
    result = response.to_bytes()

    assert b"HTTP/1.1 201" in result
    assert b"Location: /users/123" in result
    assert b"Created" in result
    print("✓ test_builder_chaining passed")


def test_content_length_auto_set():
    response = Response()
    response.text("12345")
    result = response.to_bytes()

    assert b"Content-Length: 5" in result
    print("✓ test_content_length_auto_set passed")


def test_nosniff_header_always_set():
    response = Response()
    response.text("Test")
    result = response.to_bytes()

    assert b"X-Content-Type-Options: nosniff" in result
    print("✓ test_nosniff_header_always_set passed")


def test_empty_body():
    response = Response()
    result = response.to_bytes()

    assert b"HTTP/1.1 200 OK" in result
    assert b"Content-Length: 0" in result
    print("✓ test_empty_body passed")


def test_json_with_nested_data():
    response = Response()
    data = {
        "user": {"id": 1, "name": "Alice"},
        "messages": [{"id": 1, "text": "Hello"}]
    }
    response.json(data)
    result = response.to_bytes()

    assert b'"user"' in result
    assert b'"Alice"' in result
    assert b'"messages"' in result
    print("✓ test_json_with_nested_data passed")


def test_binary_body():
    response = Response(200, b"\x00\x01\x02\x03")
    result = response.to_bytes()

    assert b"\x00\x01\x02\x03" in result
    assert b"Content-Length: 4" in result
    print("✓ test_binary_body passed")


if __name__ == "__main__":
    print("Running Response Tests...\n")

    test_basic_response()
    test_json_response()
    test_html_response()
    test_status_change()
    test_custom_headers()
    test_set_cookie()
    test_delete_cookie()
    test_multiple_cookies()
    test_factory_ok()
    test_factory_not_found()
    test_factory_bad_request()
    test_factory_server_error()
    test_builder_chaining()
    test_content_length_auto_set()
    test_nosniff_header_always_set()
    test_empty_body()
    test_json_with_nested_data()
    test_binary_body()

    print("\n✅ All 18 tests passed!")
