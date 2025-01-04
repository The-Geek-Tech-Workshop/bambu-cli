# Thank you https://github.com/greghesp/ha-bambulab/blob/main/custom_components/bambu_lab/pybambu/const.py
from enum import Enum


SPEED_PROFILE = {
    1: "silent",
    2: "standard",
    3: "sport",
    4: "ludicrous"
}


class SpeedProfile(Enum):
    SILENT = 1
    STANDARD = 2
    SPORT = 3
    LUDICROUS = 4

    def __str__(self):
        return SPEED_PROFILE[self.value]

    @staticmethod
    def from_str(speed_profile: str):
        for key, value in SPEED_PROFILE.items():
            if value == speed_profile:
                return SpeedProfiles(key)
        return None
