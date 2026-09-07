from alembic import context

# Migration wiring will be added when the SQLAlchemy metadata is defined.

target_metadata = None


def run_migrations_offline():
    context.configure(url=context.config.get_main_option('sqlalchemy.url'), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    run_migrations_offline()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
