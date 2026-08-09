import logging
from pydantic import ValidationError
from agent.collectors.security.models import SecurityInventoryData

logger = logging.getLogger(__name__)

def validate_security_data(data: SecurityInventoryData) -> bool:
    try:
        # Pydantic validates on instantiation, so if it's an instance, it's valid
        if not isinstance(data, SecurityInventoryData):
            return False
        return True
    except ValidationError as e:
        logger.error(f"Security validation failed: {e}")
        return False
