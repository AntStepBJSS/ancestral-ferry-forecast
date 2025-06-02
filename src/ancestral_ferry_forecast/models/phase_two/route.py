from pydantic import BaseModel

class Location(BaseModel):
    lat: float          # 50.7463
    lon: float          # -1.1808
    name: str           # Fishbourne
    un_locode: str      # GBRYD

class Route(BaseModel):
    route_name: str             # Portsmouth - Fishbourne
    start: Location
    end: Location
    notes: str                  # Sheltered in the Solent; vulnerable to strong SW or N winds.
    unsafe_wind_direction: str  # 170-200,350-20
    vessel_type: str            # RORO Ferry

