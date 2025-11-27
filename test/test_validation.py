from utils.validation import validate_password


def test_valid_password():
    assert validate_password("Pass123!") == True
    print("✓ test_valid_password passed")


def test_valid_password_all_special_chars():
    assert validate_password("Aa1!@#$%") == True
    assert validate_password("Bb2^&()-") == True
    assert validate_password("Cc3_=567") == True
    print("✓ test_valid_password_all_special_chars passed")


def test_too_short():
    assert validate_password("Pass12!") == False
    print("✓ test_too_short passed")


def test_no_uppercase():
    assert validate_password("pass123!") == False
    print("✓ test_no_uppercase passed")


def test_no_lowercase():
    assert validate_password("PASS123!") == False
    print("✓ test_no_lowercase passed")


def test_no_digit():
    assert validate_password("Password!") == False
    print("✓ test_no_digit passed")


def test_no_special_char():
    assert validate_password("Password123") == False
    print("✓ test_no_special_char passed")


def test_invalid_special_char_space():
    assert validate_password("Pass 123!") == False
    print("✓ test_invalid_special_char_space passed")


def test_invalid_special_char_semicolon():
    assert validate_password("Pass;123!") == False
    print("✓ test_invalid_special_char_semicolon passed")


def test_invalid_special_char_asterisk():
    assert validate_password("Pass*123!") == False
    print("✓ test_invalid_special_char_asterisk passed")


def test_exactly_8_chars():
    assert validate_password("Aa1!bcde") == True
    print("✓ test_exactly_8_chars passed")


def test_long_valid_password():
    assert validate_password("MyV3ry$ecur3P@ssw0rd!") == True
    print("✓ test_long_valid_password passed")


def test_all_requirements_minimal():
    assert validate_password("Aa1!bcde") == True
    print("✓ test_all_requirements_minimal passed")


def test_empty_password():
    assert validate_password("") == False
    print("✓ test_empty_password passed")


def test_only_lowercase():
    assert validate_password("abcdefgh") == False
    print("✓ test_only_lowercase passed")


def test_only_uppercase():
    assert validate_password("ABCDEFGH") == False
    print("✓ test_only_uppercase passed")


def test_only_digits():
    assert validate_password("12345678") == False
    print("✓ test_only_digits passed")


def test_only_special():
    assert validate_password("!@#$%^&(") == False
    print("✓ test_only_special passed")


if __name__ == "__main__":
    print("Running Password Validation Tests...\n")

    test_valid_password()
    test_valid_password_all_special_chars()
    test_too_short()
    test_no_uppercase()
    test_no_lowercase()
    test_no_digit()
    test_no_special_char()
    test_invalid_special_char_space()
    test_invalid_special_char_semicolon()
    test_invalid_special_char_asterisk()
    test_exactly_8_chars()
    test_long_valid_password()
    test_all_requirements_minimal()
    test_empty_password()
    test_only_lowercase()
    test_only_uppercase()
    test_only_digits()
    test_only_special()

    print("\n✅ All 18 validation tests passed!")
