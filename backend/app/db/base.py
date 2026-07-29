from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models here so Alembic can discover them
from app.modules.auth.models import *  # noqa
from app.modules.endpoints.models import *  # noqa
from app.modules.inventory.models import *  # noqa
