from enum import StrEnum


class ActivityType(StrEnum):
    HABIT = "habit"
    TASK = "task"
    MEASUREMENT = "measurement"
    LEARNING = "learning"
    TRAINING = "training"
    CUSTOM = "custom"


class ActivityStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
