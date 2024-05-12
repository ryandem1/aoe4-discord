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


class Civ(enum.StrEnum):
    """Civilization for AOE 4"""
    ABBASID = "abbasid"
    AYYUBIDS = "ayyubids"
    BYZANTINES = "byzantines"
    CHINESE = "chinese"
    DELHI = "delhi"
    DELHI_SULTANATE = "delhi_sultanate"  # Through non /api routes
    ENGLISH = "english"
    FRENCH = "french"
    HRE = "hre"
    HOLY_ROMAN_EMPIRE = "holy_roman_empire"  # Through non /api routes
    JAPANESE = "japanese"
    JEANNEDARC = "jeannedarc"
    JEANNE_DARC = "jeanne_darc"   # Through non /api routes
    MALIANS = "malians"
    MONGOLS = "mongols"
    ORDEROFTHEDRAGON = "orderofthedragon"
    ORDER_OF_THE_DRAGON = "order_of_the_dragon"  # Through non /api routes
    OTTOMANS = "ottomans"
    RUS = "rus"
    ZHUXI = "zhuxi"
    ZHU_XIS_LEGACY = "zhu_xis_legacy"  # Through non /api routes


RELIGIOUS_MANTRAS = [
    "God is Love",
    "Thy will be done",
    "Trust in the Lord",
    "Peace be with you",
    "Blessed be the name of the Lord",
    "Praise the Lord",
    "Shine your light",
    "Let go and let God",
    "Hallelujah",
    "Faith over fear",
    "Grace upon grace",
    "Love thy neighbor",
    "Be still and know",
    "Seek ye first the kingdom of God",
    "God is my refuge",
    "Forgive and forget",
    "Be kind always",
    "Om Namah Shivaya",
    "Hare Krishna Hare Rama",
    "Aham Brahmasmi",
    "Sat Nam",
    "Om Mani Padme Hum",
    "Shalom",
    "Namaste",
    "Amen",
    "Inshallah",
    "Bismillah",
    "Allahu Akbar",
    "Subhan Allah",
    "Baruch Hashem",
    "Jai Shree Ram",
    "Guru Brahma Guru Vishnu Guru Devo Maheshwara",
    "Sarve Bhavantu Sukhinah",
    "Lokah Samastah Sukhino Bhavantu",
    "God is my strength",
    "I am blessed",
    "Let love guide you",
    "Trust in God's plan",
    "Divine light surrounds me",
    "Faith conquers all",
    "God's grace is enough",
    "Blessings abound",
    "Love is the answer",
    "Embrace the journey",
    "Peace within, peace without",
    "Gratitude unlocks blessings",
    "Surrender to divine will",
    "Healing begins with faith",
    "Every setback is a setup for a comeback",
    "Walk by faith, not by sight",
    "Strength through prayer",
    "الله أكبر",
    "שָׁלוֹם",
    "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ",
    "南無妙法蓮華經",
    "Aloha ke Akua",
    "ॐ शान्ति",
    "سبحان الله",
    "Ave Maria",
    "Κύριε ἐλέησον",
    "பகவான் சரணம்",
    "धन्यवाद",
    "Salamat po",
    "Asante sana",
    "Gracias a Dios",
    "Merci à Dieu",
    "Grazie a Dio",
    "Danke Gott",
    "Obrigado a Deus",
    "Слава Богу",
    "Praise God",
    "আল্লাহ বাড়ি জলে দিলেন",
    "જય શ્રી કૃષ્ણ",
    "हरी बोल",
    "ಜೈ ಶ್ರೀ ಕೃಷ್ಣ",
    "ഹരേ കൃഷ്ണ",
    "ଜୟ ଶ୍ରୀ କୃଷ୍ଣ",
    "ਜਪੁਜੀ ਸਾਹਿਬ",
    "ஹரே கிருஷ்ணா",
    "హరే కృష్ణా",
    "ราม เฉือนผี",
    "אללהו אכבר",
    "ကောင်းေအာင်",
    "गजाननं भूतगणादि सेवितं",
    "දෙවිවර මහාවේ",
    "ჰარი კრიშნა",
    "የእግዚአብሔር ቅዱስ",
    "आपकी कितनी कृपा है",
    "አምላክ ለውደድ",
    "იესო ქრისტე",
    "פְּרִי קְדֹשִׁים",
    "սուրբ թագաւոր",
]

