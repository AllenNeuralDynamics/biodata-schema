""""Specimen models"""

from datetime import date as date_type
from datetime import time
from enum import Enum
from typing import Annotated, List, Optional

from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.species import Species, SpeciesModel, Strain
from pydantic import Field, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo


class CellLine(DataModel):
    """Description of a cultured cell line"""

    cell_line_name: str = Field(..., title="Cell line name")
    cell_line_type: PIDName = Field(..., title="Cell line type", description="Uses Cell Line Ontology")
    protein: PIDName = Field(..., title="Protein labeled", description="Protein uses UniProt registry")
    gene: PIDName = Field(..., title="Gene targeted", description="Gene uses NCBI taxonomy")
    cell_structure: str = Field(..., title="Cell structure protein found in") #TODO: ontology or enum in model?
    fluorescent_protein: PIDName = Field(..., title="Fluorescent protein", desciption="Uses FPbase")
    clone_number: Optional[int] = Field(default=None, title="Clone number")
