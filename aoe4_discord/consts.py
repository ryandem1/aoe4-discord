import enum


RELIC_EMOJI_ID_IN_EGGS = 1231159121718411316  # In eggs server


class Idiot(enum.StrEnum):
    JORDANIEL = "jordaniel"
    RYAN = "ryan"
    JARED = "jared"
    MASON = "mason"

    @classmethod
    def from_discord_username(cls, name: str) -> 'Idiot':
        return {
            "rybread5748": cls.RYAN,
            "_jorno": cls.JARED,
            "jordandem.": cls.JORDANIEL,
            "hoodie9569": cls.MASON
        }[name]

    @property
    def profile_id(self) -> int:
        return {
            self.JORDANIEL: 14762821,
            self.RYAN: 18933967,
            self.JARED: 9367305,
            self.MASON: 14773093,
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
