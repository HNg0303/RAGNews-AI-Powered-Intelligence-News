from core.config import setting

username = setting.postgres_user
password = setting.postgres_password
host = setting.postgres_server
port = setting.postgres_port
database = setting.postgres_db

DATABASE_URL = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
# Sync URL for Alembic migrations
DATABASE_URL_SYNC = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")