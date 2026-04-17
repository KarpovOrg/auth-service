from pydantic import BaseModel

from constants import DeviceType


class SessionCreate(BaseModel):
    device_type: DeviceType
    user_id: int
