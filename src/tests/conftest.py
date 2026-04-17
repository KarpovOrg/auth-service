import os

# Устанавливаем переменные среды ДО любого импорта из src,
# иначе Settings() упадёт — поле `app: AppConfig` обязательное.
os.environ.setdefault("AUTH_CONFIG__APP__APP_NAME", "auth-service-test")
os.environ.setdefault("AUTH_CONFIG__APP__DEBUG", "true")

