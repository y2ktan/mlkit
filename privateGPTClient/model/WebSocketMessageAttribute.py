from enum import Enum


class Role(Enum):
    SYSTEM = "system"
    BUS_DRIVER = "bus driver"
    SCHOOL_STAFF = "school staff"
    VIDEO_ASSISTANCE = "video"
    ALL = "all"