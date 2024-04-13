from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from dataclasses_json import dataclass_json


class CarMovement(Enum):
    NEARBY = "Nearby"
    STOP = "Stop"
    GONE = "Gone"


@dataclass_json
@dataclass
class ObjectDetection:
    location: str
    plate_number: str
    status: CarMovement
    time: datetime = datetime.now()

    def update_object_detection_events_from_json(self, bus_data_list_json):
        pass

