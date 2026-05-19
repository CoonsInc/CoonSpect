import bcrypt


class PasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширует пароль с использованием bcrypt."""
        if not password:
            raise ValueError("Password cannot be empty")

        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет соответствие пароля хешу."""
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except (ValueError, TypeError):
            # Если хеш поврежден или имеет неверный формат
            return False


# Зависимость для FastAPI
def get_password_service() -> PasswordService:
    return PasswordService()
