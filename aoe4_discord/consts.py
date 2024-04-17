import enum


class Idiot(enum.StrEnum):
    JORDANIEL = "JORDANIEL"
    RYAN = "RYAN"
    JARED = "JARED"

    @property
    def profile_id(self) -> int:
        return {
            self.JORDANIEL: 14762821,
            self.RYAN: 18933967,
            self.JARED: 9367305
        }[self]


class GameMode(enum.StrEnum):
    """Game mode for AOE 4"""
    rm_solo = "rm_solo"
    rm_team = "rm_team"
    rm_1v1 = "rm_1v1"
    rm_2v2 = "rm_2v2"
    rm_3v3 = "rm_3v3"
    rm_4v4 = "rm_4v4"
    qm_1v1 = "qm_1v1"
    qm_2v2 = "qm_2v2"
    qm_3v3 = "qm_3v3"
    qm_4v4 = "qm_4v4"
