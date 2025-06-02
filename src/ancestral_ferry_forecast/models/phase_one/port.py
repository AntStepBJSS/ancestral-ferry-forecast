from pydantic import BaseModel

class Port(BaseModel):
    port_name: str
    latitude: float
    longitude: float
    notes: str
    unsafe_wind_direction: str
