"""Base models for UniFi Network API responses."""

from typing import Any, Dict, List, Optional, Generic, TypeVar, get_args, get_origin

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    Field,
)
from pydantic.error_wrappers import ValidationError
from pydantic_core import PydanticCustomError

from isminet.logging import get_logger

T = TypeVar("T")
logger = get_logger(__name__)


class UnifiBaseModel(BaseModel):
    """Base model for all UniFi Network API models."""

    model_config = ConfigDict(
        extra="ignore", str_strip_whitespace=True, validate_assignment=True
    )

    def __init__(self, **data: Any) -> None:
        """Initialize model with logging."""
        try:
            super().__init__(**data)
            logger.debug(
                "model_initialized",
                model=self.__class__.__name__,
                fields=list(self.model_fields.keys()),
                provided_fields=list(data.keys()),
            )
        except ValidationError as e:
            logger.error(
                "model_validation_failed",
                model=self.__class__.__name__,
                error=str(e),
                error_type=type(e).__name__,
                validation_errors=e.errors(),
                provided_fields=list(data.keys()),
            )
            raise

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Log model serialization and return dumped data."""
        result = super().model_dump(**kwargs)
        logger.debug(
            "model_serialized",
            model=self.__class__.__name__,
            included_fields=list(result.keys()),
            exclude_unset=kwargs.get("exclude_unset", False),
            exclude_defaults=kwargs.get("exclude_defaults", False),
            exclude_none=kwargs.get("exclude_none", False),
        )
        return result


class ValidationMixin(UnifiBaseModel):
    """Common validation patterns."""

    @classmethod
    def validate_range(
        cls, v: Optional[int], min_val: int, max_val: int, field_name: str
    ) -> Optional[int]:
        """Validate integer is within range."""
        if v is not None and not min_val <= v <= max_val:
            logger.error(
                "value_out_of_range",
                field=field_name,
                value=v,
                min_val=min_val,
                max_val=max_val,
                model=cls.__name__,
            )
            raise PydanticCustomError(
                "value_out_of_range",
                "{field_name} must be between {min_val} and {max_val}",
                {"field_name": field_name, "min_val": min_val, "max_val": max_val},
            )
        logger.debug(
            "validated_range",
            field=field_name,
            value=v,
            min_val=min_val,
            max_val=max_val,
            model=cls.__name__,
        )
        return v

    @classmethod
    def validate_non_negative(cls, v: Optional[int]) -> Optional[int]:
        """Validate integer is non-negative."""
        if v is not None and v < 0:
            logger.error(
                "value_negative",
                value=v,
                model=cls.__name__,
            )
            raise PydanticCustomError(
                "value_negative",
                "Value must be non-negative",
                {},
            )
        logger.debug(
            "validated_non_negative",
            value=v,
            model=cls.__name__,
        )
        return v

    @classmethod
    def validate_percentage(cls, v: Optional[float]) -> Optional[float]:
        """Validate value is a valid percentage (0-100)."""
        if v is not None and not 0 <= v <= 100:
            logger.error(
                "percentage_out_of_range",
                value=v,
                model=cls.__name__,
            )
            raise PydanticCustomError(
                "value_out_of_range",
                "Percentage must be between 0 and 100",
                {},
            )
        logger.debug(
            "validated_percentage",
            value=v,
            model=cls.__name__,
        )
        return v

    @classmethod
    def validate_negative(cls, v: Optional[int]) -> Optional[int]:
        """Validate integer is negative."""
        if v is not None and v >= 0:
            logger.error(
                "value_not_negative",
                value=v,
                model=cls.__name__,
            )
            raise PydanticCustomError(
                "value_not_negative",
                "Value must be negative",
                {},
            )
        logger.debug(
            "validated_negative",
            value=v,
            model=cls.__name__,
        )
        return v


class Meta(UnifiBaseModel):
    """Meta information for UniFi Network API responses."""

    rc: str = Field(description="Response code")
    msg: Optional[str] = Field(None, description="Response message")

    @field_validator("rc")
    @classmethod
    def validate_rc(cls, v: str) -> str:
        """Validate response code."""
        if v != "ok":
            raise ValueError("Response code must be 'ok'")
        return v


class BaseResponse(UnifiBaseModel, Generic[T]):
    """Base response model for UniFi API responses."""

    meta: Meta
    data: List[T]

    @field_validator("meta")
    @classmethod
    def validate_meta(cls, v: Meta) -> Meta:
        """Validate meta field."""
        if v.rc != "ok":
            raise ValueError("Invalid response status")
        return v

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: List[T]) -> List[T]:
        """Validate data field."""
        if not v:
            raise ValueError("List should have at least 1 item")
        return v

    def __getitem__(self, index: int) -> T:
        """Get item from data list by index."""
        if not isinstance(self.data, list):
            raise TypeError("Data field must be a list")
        try:
            return self.data[index]
        except IndexError:
            raise IndexError("Data index out of range")

    def __getattr__(self, name: str) -> Any:
        """Get attribute from data list."""
        if name == "data":
            raise AttributeError(
                f"{type(self).__name__!r} object has no attribute {name!r}"
            )
        if not isinstance(self.data, list):
            raise TypeError("Data field must be a list")
        if not self.data:
            raise IndexError("Data list is empty")
        if name.startswith("data["):
            # Parse array access
            try:
                index = int(name[5:-1])  # Extract index from "data[X]"
                return self[index]
            except (ValueError, IndexError) as e:
                raise AttributeError(
                    f"{type(self).__name__!r} object has no attribute {name!r}"
                ) from e
        return getattr(self.data[0], name)

    @classmethod
    def get_data_type(cls) -> type:
        """Get the type of the data field."""
        for base in cls.__orig_bases__:  # type: ignore
            if get_origin(base) is BaseResponse:
                args = get_args(base)
                if args:
                    return args[0]
        raise TypeError("Could not determine data type for BaseResponse")
