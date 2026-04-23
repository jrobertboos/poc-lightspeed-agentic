"""Dynamic Pydantic model generation from configuration."""

from typing import Any

from pydantic import Field, create_model

from src.config.models import OutputTypeConfig

TYPE_MAP: dict[str, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


def _parse_type(type_str: str) -> type:
    """Parse a type string into a Python type.

    Supports: str, int, float, bool, list[T], optional[T]
    """
    type_str = type_str.strip()
    lower = type_str.lower()

    if lower in TYPE_MAP:
        return TYPE_MAP[lower]

    if lower.startswith("list[") and lower.endswith("]"):
        inner = type_str[5:-1]
        inner_type = _parse_type(inner)
        return list[inner_type]  # type: ignore[valid-type]

    if lower.startswith("optional[") and lower.endswith("]"):
        inner = type_str[9:-1]
        inner_type = _parse_type(inner)
        return inner_type | None  # type: ignore[return-value]

    return str


def build_output_type(config: OutputTypeConfig) -> type:
    """Build a Pydantic model from an OutputTypeConfig."""
    field_definitions: dict[str, Any] = {}

    for field in config.fields:
        field_type = _parse_type(field.type)

        if not field.required:
            field_type = field_type | None  # type: ignore[assignment]

        if field.description:
            default = ... if field.required else None
            field_definitions[field.name] = (field_type, Field(default, description=field.description))
        else:
            if field.required:
                field_definitions[field.name] = (field_type, ...)
            else:
                field_definitions[field.name] = (field_type, None)

    model = create_model(
        config.name,
        __doc__=config.description,
        **field_definitions,
    )

    return model
