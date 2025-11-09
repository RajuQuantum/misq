"""Lightweight subset of Pydantic used for offline execution."""

from __future__ import annotations

from dataclasses import dataclass
from types import ModuleType
from typing import Any, Dict, Iterable, List, Tuple, Type, TypeVar, get_args, get_origin


class ValidationError(Exception):
    """Exception raised when required fields are missing."""


@dataclass
class FieldInfo:
    default: Any = ...
    alias: str | None = None


def Field(default: Any = ..., alias: str | None = None) -> FieldInfo:
    return FieldInfo(default=default, alias=alias)


T = TypeVar("T", bound="BaseModel")


class _Validator:
    def __init__(self, fields: Tuple[str, ...], func):
        self.fields = fields
        self.func = func


def validator(*fields: str):
    def decorator(func):
        return _Validator(fields, func)

    return decorator


def _convert_value(annotation, value):
    origin = get_origin(annotation)
    if origin in (list, List, Iterable):
        inner = (get_args(annotation) or (Any,))[0]
        return [_convert_value(inner, item) for item in value]
    if origin in (dict, Dict):
        key_type, value_type = get_args(annotation) or (Any, Any)
        return {
            _convert_value(key_type, key): _convert_value(value_type, item)
            for key, item in value.items()
        }
    if origin is None and getattr(annotation, "__origin__", None) in (list, List):
        inner = annotation.__args__[0]
        return [_convert_value(inner, item) for item in value]
    if origin is None and getattr(annotation, "__origin__", None) in (dict, Dict):
        key_type, value_type = annotation.__args__
        return {
            _convert_value(key_type, key): _convert_value(value_type, item)
            for key, item in value.items()
        }
    if origin is None and getattr(annotation, "__args__", None):
        for option in annotation.__args__:
            if option is type(None):  # noqa: E721
                continue
            try:
                return _convert_value(option, value)
            except Exception:
                continue
        return value
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        if isinstance(value, annotation):
            return value
        return annotation(**value)
    return value


class BaseModelMeta(type):
    def __new__(mcls, name, bases, namespace):
        validators: Dict[str, List] = {}
        for attr, value in list(namespace.items()):
            if isinstance(value, _Validator):
                for field in value.fields:
                    validators.setdefault(field, []).append(value.func)
                namespace.pop(attr)
        cls = super().__new__(mcls, name, bases, namespace)
        cls.__validators__ = validators
        cls.__field_info__ = {}
        annotations = getattr(cls, "__annotations__", {})
        aliases = {}
        for field, annotation in annotations.items():
            default = getattr(cls, field, ...)
            if isinstance(default, FieldInfo):
                cls.__field_info__[field] = default
                if default.alias:
                    aliases[default.alias] = field
                if default.default is not ...:
                    setattr(cls, field, default.default)
                else:
                    delattr(cls, field)
            else:
                cls.__field_info__[field] = FieldInfo(default=default if default is not None else ...)
        cls.__aliases__ = aliases
        return cls


class BaseModel(metaclass=BaseModelMeta):
    __validators__: Dict[str, List]
    __field_info__: Dict[str, FieldInfo]
    __aliases__: Dict[str, str]

    class Config:
        allow_population_by_field_name = False

    def __init__(self, **data: Any):
        processed: Dict[str, Any] = {}
        annotations = getattr(self.__class__, "__annotations__", {})
        for field, annotation in annotations.items():
            info = self.__field_info__.get(field, FieldInfo())
            alias = info.alias
            if field in data:
                value = data[field]
            elif alias and alias in data:
                value = data[alias]
            elif info.default is not ...:
                value = info.default
            else:
                raise ValidationError(f"Missing field: {field}")
            value = _convert_value(annotation, value)
            processed[field] = value
        for field, funcs in self.__validators__.items():
            if field in processed:
                for func in funcs:
                    processed[field] = func(self.__class__, processed[field])
        self.__dict__.update(processed)

    def dict(self, by_alias: bool = False) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for field in self.__annotations__:
            info = self.__field_info__.get(field)
            key = info.alias if by_alias and info and info.alias else field
            result[key] = _export(getattr(self, field))
        return result

    @classmethod
    def parse_obj(cls: Type[T], data: Dict[str, Any]) -> T:
        return cls(**data)


def _export(value):
    if isinstance(value, BaseModel):
        return value.dict()
    if isinstance(value, list):
        return [_export(item) for item in value]
    if isinstance(value, dict):
        return {key: _export(item) for key, item in value.items()}
    return value


def build_pydantic_module() -> ModuleType:
    module = ModuleType("pydantic")
    module.BaseModel = BaseModel
    module.Field = Field
    module.validator = validator
    module.ValidationError = ValidationError
    return module
