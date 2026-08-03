from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models here so Alembic & SQLAlchemy can discover them
from app.modules.auth.models import *  # noqa
from app.modules.endpoints.models import *  # noqa
from app.modules.inventory.models import *  # noqa
from app.modules.commands.models import *  # noqa
from app.modules.alerts.models import *  # noqa
from app.modules.groups.models import *  # noqa
from app.modules.policies.models import *  # noqa
from app.modules.schedules.models import *  # noqa
from app.modules.notifications.models import *  # noqa
