import pytest
from src.services.password import hash_password, verify_password

def test_hash_password_creates_different_hashes():
    password = "secret_password_123"
    
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    # Bcrypt использует соль, поэтому хэши для одного пароля должны быть разными
    assert hash1 != hash2
    assert hash1.startswith("$2b$")  # Стандартный префикс bcrypt
    assert hash2.startswith("$2b$")

def test_verify_password_success():
    password = "correct_password"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True

def test_verify_password_failure():
    password = "correct_password"
    wrong_password = "wrong_password"
    hashed = hash_password(password)
    
    assert verify_password(wrong_password, hashed) is False

@pytest.mark.parametrize("empty_input", ["", " ", "\n"])
def test_password_with_empty_strings(empty_input):
    # Проверяем, что сервис адекватно обрабатывает пустые или странные строки
    hashed = hash_password(empty_input)
    assert verify_password(empty_input, hashed) is True

def test_verify_password_invalid_hash_format():
    # Проверяем поведение при передаче некорректного хэша
    # Bcrypt выбросит ValueError, если строка не является валидным хэшем
    with pytest.raises(ValueError):
        verify_password("password", "not_a_bcrypt_hash")
