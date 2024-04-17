import enum


class Idiot(enum.StrEnum):
    JORDANIEL = "jordaniel"
    RYAN = "ryan"
    JARED = "jared"

    @property
    def profile_id(self) -> int:
        return {
            self.JORDANIEL: 14762821,
            self.RYAN: 18933967,
            self.JARED: 9367305
        }[self]


class Elo(enum.StrEnum):
    """Game mode for AOE 4"""
    rm_solo = "rm_solo"
    rm_team = "rm_team"
    rm_1v1 = "rm_1v1_elo"
    rm_2v2 = "rm_2v2_elo"
    rm_3v3 = "rm_3v3_elo"
    rm_4v4 = "rm_4v4_elo"
    qm_1v1 = "qm_1v1_elo"
    qm_2v2 = "qm_2v2_elo"
    qm_3v3 = "qm_3v3_elo"
    qm_4v4 = "qm_4v4_elo"
