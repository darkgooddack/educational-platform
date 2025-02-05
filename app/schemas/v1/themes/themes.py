from typing import Optional, List
from ..base import BaseInputSchema, CommonBaseSchema, ListResponseSchema

class ThemeBase(CommonBaseSchema):
    name: str
    description: str
    parent_id: Optional[int] = None

class ThemeCreateSchema(BaseInputSchema):
    name: str
    description: str
    parent_id: Optional[int] = None

class ThemeSchema(ThemeBase):
    id: int

class ThemeListResponse(ListResponseSchema[ThemeSchema]):
    items: List[ThemeSchema]