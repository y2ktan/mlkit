from dataclasses import dataclass
from enum import Enum

import pytz
from dataclasses_json import dataclass_json, config
from datetime import datetime


class PassengerOnboardStatus(Enum):
    ENTERING = "embarked"
    BOARDING = "still present on the bus"
    EXITING = "disembarked"

@dataclass_json
@dataclass
class PassengerRoute:
    location: str
    passenger_status: PassengerOnboardStatus
    description: str
    time: datetime = datetime.now(tz=pytz.utc)

@dataclass_json
@dataclass
class Passenger:
    name: str
    final_destination: str
    passenger_activities: list[PassengerRoute]


