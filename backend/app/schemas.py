from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from uuid import UUID

class LoginReq(BaseModel):
    username: str
    password: str

class ItemCreate(BaseModel):
    name: str
    base_unit_id: UUID
    case_size: Optional[float] = None
    allow_partials: bool = True
    par_level: Optional[float] = None
    low_threshold: Optional[float] = None
    default_location_id: Optional[UUID] = None
    active: bool = True

class ItemUpdate(ItemCreate):
    pass

class ItemOut(BaseModel):
    id: UUID
    name: str
    base_unit_id: UUID
    case_size: Optional[float]
    allow_partials: bool
    par_level: Optional[float]
    low_threshold: Optional[float]
    default_location_id: Optional[UUID]
    active: bool

class UnitOut(BaseModel):
    id: UUID
    name: str
    active: bool

class LocationOut(BaseModel):
    id: UUID
    name: str
    active: bool

EventType = Literal["COUNT_SET","TRUCK_ADD","WASTE_SUB","TRANSFER_OUT_SUB","TRANSFER_IN_ADD","ADJUSTMENT","ADJUSTMENT"]

class SyncEventIn(BaseModel):
    client_event_id: UUID
    event_type: Literal["COUNT_SET","TRUCK_ADD","WASTE_SUB","TRANSFER_OUT_SUB","TRANSFER_IN_ADD","ADJUSTMENT"]
    item_id: UUID
    delta_base_units: float
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    ref_type: Optional[str] = None
    ref_id: Optional[UUID] = None

class SyncPushReq(BaseModel):
    device_id: str = Field(min_length=1, max_length=128)
    events: List[SyncEventIn]

class SyncPullRes(BaseModel):
    events: list[dict]

class AppSettingsOut(BaseModel):
    store_number: str
    store_label: str
    intersection: str
