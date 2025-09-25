from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

engine = create_engine(settings.database_conn_str)

# from sqlalchemy.pool import NullPool

# engine = create_engine(
#     settings.database_conn_str,
#     poolclass=NullPool,  # Avoid using stale connections in serverless
#     connect_args={"sslmode": "require"}
# )

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()

