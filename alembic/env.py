from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.models import Base  # Burada 'models' projenin ana model dosyanın ismi

# Alembic yapılandırma dosyasını alıyoruz
config = context.config

# Veritabanı bağlantı bilgileri
db_user = 'postgres'
db_pass = '9bDUt05IAmlGSXITBsvF'
db_host = 'coin-db.cbiu28e8ee33.eu-central-1.rds.amazonaws.com'
db_port = '5432'
db_name = 'postgres'

DATABASE_URL = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

# Alembic'teki sqlalchemy.url parametresini güncelliyoruz
config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata

# Logları yapılandırıyoruz
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Bağlantı işlemi için fonksiyonlar
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Çalışma modu
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
