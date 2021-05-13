from enum import IntEnum


class AppointmentStatus (IntEnum):
    OPEN = 0
    ONHOLD = 1
    SCHEDULED = 2
    COMPLETED = 3
    MISSED = 4