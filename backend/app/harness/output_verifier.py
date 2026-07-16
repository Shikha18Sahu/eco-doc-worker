from typing import Any

from pydantic import BaseModel, ValidationError


class OutputVerificationError(Exception):
    pass


class OutputVerifier:
    """Validates an agent's raw output against its expected Pydantic schema
    before the Harness allows the workflow to proceed."""

    @staticmethod
    def verify(output: dict[str, Any], schema: type[BaseModel]) -> BaseModel:
        try:
            return schema.model_validate(output)
        except ValidationError as e:
            raise OutputVerificationError(str(e)) from e