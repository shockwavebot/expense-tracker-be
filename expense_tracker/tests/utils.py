# expense_tracker/tests/utils.py
import logging
from typing import Any, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


def create_test_model(model_cls: Type[T], **kwargs: Any) -> T:
    """Helper function to create test models with default values."""
    try:
        return model_cls(**kwargs)
    except Exception as e:
        logger.error(f"Failed to create test model {
                     model_cls.__name__}: {str(e)}")
        raise


def setup_test_logging():
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
