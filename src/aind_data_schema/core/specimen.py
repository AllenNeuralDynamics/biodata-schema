'''schema for specimen metadata'''

from pydantic import Field, SkipValidation

from aind_data_schema.base import DataCoreModel, Discriminated
from aind_data_schema.components.specimens import CellLine

class Specimen(DataCoreModel):
    """Description of a subject of data collection"""

    _DESCRIBED_BY_URL = DataCoreModel._DESCRIBED_BY_BASE_URL.default + "aind_data_schema/core/subject.py"
    describedBy: str = Field(default=_DESCRIBED_BY_URL, json_schema_extra={"const": _DESCRIBED_BY_URL})
    schema_version: SkipValidation[Literal["0.0.1"]] = Field(default="0.0.1")
    specimen_id: str = Field(
        ...,
        description="Unique identifier for the specimen of data acquisition",
        title="Specimen ID",
    )

    specimen_details: Discriminated[CellLine] = Field(
        ..., title="Specimen Details"
    )

    notes: Optional[str] = Field(default=None, title="Notes")
