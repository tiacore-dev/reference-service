# pydantic_models/legal_entity_models.py

from typing import List
from uuid import UUID

from pydantic import BaseModel


class LegalEntityByIdsRequestSchema(BaseModel):
    ids: List[UUID]
