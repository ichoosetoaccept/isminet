"""Base models for UniFi Network API responses."""

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Generic,
    TypeVar,
    get_args,
    get_origin,
    cast,
)
from collections import Counter
from datetime import datetime

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

# Track error occurrences for correlation
_error_counter: Counter[str] = Counter()
_error_timestamps: Dict[str, List[datetime]] = {}


def _track_error(error_type: str, model: str) -> None:
    """Track error occurrence for correlation."""
    error_key = f"{model}:{error_type}"
    _error_counter[error_key] += 1
    if error_key not in _error_timestamps:
        _error_timestamps[error_key] = []
    _error_timestamps[error_key].append(datetime.now())

    # Log if we see repeated errors
    if _error_counter[error_key] >= 3:
        recent_errors = [
            ts
            for ts in _error_timestamps[error_key]
            if (datetime.now() - ts).total_seconds() < 300
        ]
        if len(recent_errors) >= 3:
            logger.warning(
                event="recurring_errors_detected",
                error_type=error_type,
                model=f"{model}:{error_type}",
                count=_error_counter[error_key],
                recent_count=len(recent_errors),
                first_seen=_error_timestamps[error_key][0].isoformat(),
                last_seen=_error_timestamps[error_key][-1].isoformat(),
            )


def _get_troubleshooting_hint(error_type: str, context: Dict[str, Any]) -> str:
    """Get troubleshooting hint for common errors."""
    if error_type == "value_error":
        if "field required" in str(context.get("error", "")):
            return "Make sure all required fields are provided in the request"
        if "not a valid" in str(context.get("error", "")):
            return f"Check the data type of field '{context.get('field', 'unknown')}'"
    elif error_type == "value_out_of_range":
        return f"Value must be between {context.get('min_val', '?')} and {context.get('max_val', '?')}"
    elif error_type == "type_error":
        return "Check that the data types match the model specification"
    elif error_type == "value_negative":
        return "Value must be greater than or equal to 0"
    elif error_type == "value_not_negative":
        return "Value must be less than 0"
    elif error_type == "index_error":
        return f"Index {context.get('index', '?')} is out of range for sequence of length {context.get('length', '?')}"
    return "Check the API documentation for correct field formats and constraints"


class UnifiBaseModel(BaseModel):
    """Base model for all UniFi Network API models."""

    model_config = ConfigDict(
        extra="ignore", str_strip_whitespace=True, validate_assignment=True
    )

    def __init__(self, **data: Any) -> None:
        """Initialize the model and log initialization details."""
        try:
            super().__init__(**data)
            logger.info(
                event="model_initialized",
                model=self.__class__.__name__,
                provided_fields=list(data.keys()),
            )
        except ValidationError as e:
            error_details = []
            for err in e.errors():
                error_type = err["type"]
                error_context = {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "error": err["msg"],
                    **err.get("ctx", {}),
                }
                hint = _get_troubleshooting_hint(error_type, error_context)
                error_details.append(
                    {
                        "type": error_type,
                        "loc": list(err["loc"]),
                        "msg": err["msg"],
                        "input": err["input"],
                        "ctx": err.get("ctx", {}),
                        "hint": hint,
                    }
                )
                _track_error(error_type, self.__class__.__name__)

            logger.error(
                event="model_validation_failed",
                model=self.__class__.__name__,
                error=str(e),
                error_type=e.__class__.__name__,
                validation_errors=error_details,
                provided_fields=list(data.keys()),
            )
            raise

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Dump the model to a dictionary and log the serialization."""
        try:
            data = super().model_dump(**kwargs)
            logger.info(
                event="model_serialized",
                model=self.__class__.__name__,
                included_fields=list(data.keys()),
                **{
                    k: v
                    for k, v in kwargs.items()
                    if isinstance(v, (bool, int, float, str))
                },
            )
            return data
        except Exception as e:
            logger.error(
                event="model_serialization_failed",
                model=self.__class__.__name__,
                error=str(e),
                error_type=e.__class__.__name__,
                **{
                    k: v
                    for k, v in kwargs.items()
                    if isinstance(v, (bool, int, float, str))
                },
            )
            raise

    def get_process(self, index: int) -> Any:
        """Get a process by index with error handling."""
        try:
            if not hasattr(self, "processes"):
                raise TypeError(f"{self.__class__.__name__} has no processes")
            processes = cast(List[Any], getattr(self, "processes"))
            return processes[index]
        except IndexError as e:
            processes = cast(List[Any], getattr(self, "processes", []))
            logger.error(
                event="index_out_of_range",
                model=self.__class__.__name__,
                error=str(e),
                error_type=e.__class__.__name__,
                index=index,
                data_length=len(processes),
                hint=_get_troubleshooting_hint(
                    "index_error", {"index": index, "length": len(processes)}
                ),
            )
            raise


class ValidationMixin(UnifiBaseModel):
    """Common validation patterns."""

    @classmethod
    def validate_range(
        cls, v: Optional[int], min_val: int, max_val: int, field_name: str
    ) -> Optional[int]:
        """Validate integer is within range."""
        if v is not None and not min_val <= v <= max_val:
            error_type = "value_out_of_range"
            _track_error(error_type, cls.__name__)
            logger.error(
                event=error_type,
                field=field_name,
                value=v,
                min_val=min_val,
                max_val=max_val,
                hint=_get_troubleshooting_hint(
                    error_type, {"min_val": min_val, "max_val": max_val}
                ),
            )
            raise PydanticCustomError(
                error_type,
                f"Value must be between {min_val} and {max_val}",
                {"min_val": min_val, "max_val": max_val},
            )
        return v

    @classmethod
    def validate_non_negative(cls, v: Optional[int]) -> Optional[int]:
        """Validate integer is non-negative."""
        if v is not None and v < 0:
            error_type = "value_negative"
            _track_error(error_type, cls.__name__)
            logger.error(
                event=error_type,
                value=v,
                model=cls.__name__,
                hint=_get_troubleshooting_hint(error_type, {"value": v}),
            )
            raise PydanticCustomError(
                error_type,
                "Value must be non-negative",
                {},
            )
        logger.debug(
            event="validated_non_negative",
            value=v,
            model=cls.__name__,
        )
        return v

    @classmethod
    def validate_percentage(cls, v: Optional[float]) -> Optional[float]:
        """Validate value is a valid percentage (0-100)."""
        if v is not None and not 0 <= v <= 100:
            error_type = "value_out_of_range"
            _track_error(error_type, cls.__name__)
            logger.error(
                event=error_type,
                value=v,
                model=cls.__name__,
                hint=_get_troubleshooting_hint(
                    error_type,
                    {
                        "min_val": 0,
                        "max_val": 100,
                    },
                ),
            )
            raise PydanticCustomError(
                error_type,
                "Percentage must be between 0 and 100",
                {},
            )
        logger.debug(
            event="validated_percentage",
            value=v,
            model=cls.__name__,
        )
        return v

    @classmethod
    def validate_negative(cls, v: Optional[int]) -> Optional[int]:
        """Validate integer is negative."""
        if v is not None and v >= 0:
            error_type = "value_not_negative"
            _track_error(error_type, cls.__name__)
            logger.error(
                event=error_type,
                value=v,
                model=cls.__name__,
                hint=_get_troubleshooting_hint(error_type, {"value": v}),
            )
            raise PydanticCustomError(
                error_type,
                "Value must be negative",
                {},
            )
        logger.debug(
            event="validated_negative",
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
            error_type = "invalid_response_code"
            _track_error(error_type, cls.__name__)
            logger.error(
                event=error_type,
                code=v,
                model=cls.__name__,
                hint="Response code must be 'ok' for successful operations",
            )
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
            error_type = "invalid_response_status"
            _track_error(error_type, cls.__name__)
            logger.error(
                event=error_type,
                code=v.rc,
                message=v.msg,
                model=cls.__name__,
                hint="Check the response message for details about the error",
            )
            raise ValueError("Invalid response status")
        return v

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: List[T]) -> List[T]:
        """Validate data field."""
        if not v:
            error_type = "empty_data_list"
            _track_error(error_type, cls.__name__)
            logger.error(
                event=error_type,
                model=cls.__name__,
                hint="The API response must contain at least one item",
            )
            raise ValueError("List should have at least 1 item")
        return v

    def __getitem__(self, index: int) -> T:
        """Get item from data list by index."""
        try:
            if not isinstance(self.data, list):
                error_type = "invalid_data_type"
                _track_error(error_type, self.__class__.__name__)
                logger.error(
                    event=error_type,
                    expected_type="list",
                    actual_type=type(self.data).__name__,
                    model=self.__class__.__name__,
                    hint="The data field must be a list of items",
                )
                raise TypeError("Data field must be a list")
            return self.data[index]
        except IndexError:
            error_type = "index_out_of_range"
            _track_error(error_type, self.__class__.__name__)
            logger.error(
                event=error_type,
                index=index,
                data_length=len(self.data),
                model=self.__class__.__name__,
                hint=f"Index {index} is out of range for data list of length {len(self.data)}",
            )
            raise IndexError("Data index out of range")

    def __getattr__(self, name: str) -> Any:
        """Get attribute from data list."""
        try:
            if name == "data":
                error_type = "missing_data_attribute"
                _track_error(error_type, self.__class__.__name__)
                logger.error(
                    event=error_type,
                    model=self.__class__.__name__,
                    hint="The data attribute is missing from the response",
                )
                raise AttributeError(
                    f"{type(self).__name__!r} object has no attribute {name!r}"
                )
            if not isinstance(self.data, list):
                error_type = "invalid_data_type"
                _track_error(error_type, self.__class__.__name__)
                logger.error(
                    event=error_type,
                    expected_type="list",
                    actual_type=type(self.data).__name__,
                    model=self.__class__.__name__,
                    hint="The data field must be a list of items",
                )
                raise TypeError("Data field must be a list")
            if not self.data:
                error_type = "empty_data_list"
                _track_error(error_type, self.__class__.__name__)
                logger.error(
                    event=error_type,
                    model=self.__class__.__name__,
                    hint="Cannot access attributes on an empty data list",
                )
                raise IndexError("Data list is empty")
            if name.startswith("data["):
                try:
                    index = int(name[5:-1])  # Extract index from "data[X]"
                    return self[index]
                except (ValueError, IndexError) as e:
                    error_type = "invalid_data_access"
                    _track_error(error_type, self.__class__.__name__)
                    logger.error(
                        event=error_type,
                        access_pattern=name,
                        error=str(e),
                        model=self.__class__.__name__,
                        hint="Invalid data access pattern. Use data[n] where n is a valid index",
                    )
                    raise AttributeError(
                        f"{type(self).__name__!r} object has no attribute {name!r}"
                    ) from e
            return getattr(self.data[0], name)
        except Exception as e:
            error_type = "attribute_access_error"
            _track_error(error_type, self.__class__.__name__)
            logger.error(
                event=error_type,
                attribute=name,
                error=str(e),
                error_type=e.__class__.__name__,
                model=self.__class__.__name__,
                hint="Failed to access attribute. Check if the attribute exists and the data list is not empty",
            )
            raise

    @classmethod
    def get_data_type(cls) -> type:
        """Get the type of the data field."""
        try:
            for base in cls.__orig_bases__:  # type: ignore
                if get_origin(base) is BaseResponse:
                    args = get_args(base)
                    if args:
                        return args[0]
            error_type = "invalid_response_type"
            _track_error(error_type, cls.__name__)
            logger.error(
                event=error_type,
                model=cls.__name__,
                hint="The response class must specify a data type parameter",
            )
            raise TypeError("Could not determine data type for BaseResponse")
        except Exception as e:
            error_type = "type_resolution_error"
            _track_error(error_type, cls.__name__)
            logger.error(
                event=error_type,
                error=str(e),
                error_type=e.__class__.__name__,
                model=cls.__name__,
                hint="Failed to resolve response data type. Check class definition",
            )
            raise
