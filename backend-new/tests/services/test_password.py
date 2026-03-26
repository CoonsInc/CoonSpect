import pytest
from src.services.password import PasswordService

@pytest.fixture
def password_service() -> PasswordService:
    return PasswordService()

def test_hash_password_success(password_service: PasswordService) -> None:
    """Проверка, что пароль хешируется и не сохраняется в открытом виде."""
    password = "my_super_secret_123"
    hashed = password_service.hash_password(password)
    
    assert hashed != password
    assert len(hashed) > 20  # Хеши bcrypt обычно длинные
    # Проверяем, что это валидный bcrypt хеш (начинается с $2b$)
    assert hashed.startswith("$2b$")

def test_verify_password_correct(password_service: PasswordService) -> None:
    """Проверка успешной верификации правильного пароля."""
    password = "correct_password"
    hashed = password_service.hash_password(password)
    
    assert password_service.verify_password(password, hashed) is True

def test_verify_password_incorrect(password_service: PasswordService) -> None:
    """Проверка, что неверный пароль не проходит верификацию."""
    password = "secret"
    other_password = "wrong"
    hashed = password_service.hash_password(password)
    
    assert password_service.verify_password(other_password, hashed) is False

def test_hash_password_empty_raises_error(password_service: PasswordService) -> None:
    """Проверка выброса исключения при пустом пароле."""
    with pytest.raises(ValueError) as exc:
        password_service.hash_password("")
    
    assert str(exc.value) == "Password cannot be empty"

def test_verify_invalid_hash_format(password_service: PasswordService) -> None:
    """Проверка устойчивости к битому формату хеша."""
    # Передаем строку, которая точно не является bcrypt-хешем
    assert password_service.verify_password("any", "not_a_hash") is False
    assert password_service.verify_password("any", "") is False