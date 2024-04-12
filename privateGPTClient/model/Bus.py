from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
from datetime import datetime


class BusMovement(Enum):
    STOP = "Reached and Waiting"
    GO = "Leaving"

@dataclass_json
@dataclass
class BusActivity:
    location: str
    activity: BusMovement
    time: datetime = datetime.now()

@dataclass_json
@dataclass
class Bus:
    plate_number: str
    bus_activities:  list[BusActivity]

