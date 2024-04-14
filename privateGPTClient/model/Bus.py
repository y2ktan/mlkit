from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
from datetime import datetime


class BusStatus(Enum):
    STOP = "Stop"
    WAITING = "Wait"
    GO = "Go"


@dataclass_json
@dataclass
class BusActivity:
    location: str
    activity: BusStatus
    time: datetime = datetime.now()

@dataclass_json
@dataclass
class Bus:
    plate_number: str
    bus_activities:  list[BusActivity]

