from dataclasses import dataclass

import pytz
from dataclasses_json import dataclass_json
from enum import Enum
from datetime import datetime


class BusStatus(Enum):
    STOP = "Arrived and Stop"
    WAITING = "Door open and Wait"
    DOOR_CLOSE = "Door close and get ready"
    GO = "Go and leaving"


@dataclass_json
@dataclass
class BusActivity:
    location: str
    activity: BusStatus
    time: datetime = datetime.now(tz=pytz.utc)

@dataclass_json
@dataclass
class Bus:
    plate_number: str
    bus_activities:  list[BusActivity]

