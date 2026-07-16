from typing import Optional, Union

from pydantic import RootModel

FieldValue = Optional[Union[str, list[str]]]


class ExtractedDocument(RootModel[dict[str, FieldValue]]):
    """Schema-free container: field_name -> value, where value can be
    a single string (e.g. name, email) or a list of strings (e.g.
    skills, education entries, work experience entries)."""
    pass