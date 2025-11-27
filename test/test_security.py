from utils.security import escape_html


def test_escape_html_basic():
    result = escape_html("<script>alert('xss')</script>")
    expected = "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    assert result == expected
    print("✓ test_escape_html_basic passed")


def test_escape_html_ampersand():
    result = escape_html("Tom & Jerry")
    expected = "Tom &amp; Jerry"
    assert result == expected
    print("✓ test_escape_html_ampersand passed")


def test_escape_html_quotes():
    result = escape_html('He said "Hello"')
    expected = "He said &quot;Hello&quot;"
    assert result == expected
    print("✓ test_escape_html_quotes passed")


def test_escape_html_mixed():
    result = escape_html("<div>User's message: \"Hello & goodbye\"</div>")
    expected = "&lt;div&gt;User&#x27;s message: &quot;Hello &amp; goodbye&quot;&lt;/div&gt;"
    assert result == expected
    print("✓ test_escape_html_mixed passed")


def test_escape_html_safe_text():
    result = escape_html("Hello World 123")
    expected = "Hello World 123"
    assert result == expected
    print("✓ test_escape_html_safe_text passed")


def test_escape_html_empty():
    result = escape_html("")
    expected = ""
    assert result == expected
    print("✓ test_escape_html_empty passed")


def test_escape_html_img_tag():
    result = escape_html('<img src="x" onerror="alert(1)">')
    expected = '&lt;img src=&quot;x&quot; onerror=&quot;alert(1)&quot;&gt;'
    assert result == expected
    print("✓ test_escape_html_img_tag passed")


if __name__ == "__main__":
    print("Running Security Tests...\n")

    test_escape_html_basic()
    test_escape_html_ampersand()
    test_escape_html_quotes()
    test_escape_html_mixed()
    test_escape_html_safe_text()
    test_escape_html_empty()
    test_escape_html_img_tag()

    print("\n✅ All 7 security tests passed!")
