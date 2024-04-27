from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import pytz
from dataclasses_json import dataclass_json

class IncidentLevel(Enum):
   THREAT = "ALERT: Critical Situation Detected"
   LOW_THREAT_INFO = "Unusual Situation Detected"

@dataclass_json
@dataclass
class Incident:
   location: str = ""
   plate_number: str = ""
   details:str = ""
   status: IncidentLevel = IncidentLevel.LOW_THREAT_INFO
   time: datetime = datetime.now(tz=pytz.utc)