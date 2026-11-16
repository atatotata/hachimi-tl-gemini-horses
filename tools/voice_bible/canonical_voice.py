"""Canonical voice/name policy for the Umamusume EN translation project.

Sources of truth, in priority order:
  1. Global EN master DB (text_data / character_system_text) -- authoritative wording.
  2. UmaTL (hachimi-tl-en-sd) -- used where Global has no row.
  3. House coinage -- documented here when neither exists.

NPC personal names are given-name-first ("Kiyoko Hoshina"), per user decision
2026-10-28. Global itself uses given-first for every NPC it ships:
Tazuna Hayakawa, Director Akikawa, Etsuko Otonashi, Riko Kashimoto, Mei Satake*,
Ryoka Tsurugi* (*no Global row; UmaTL cat6 form).
"""

# --- shipped-text corrections: our current string -> canonical string ---------
# Ordered; longer / more specific strings first. Applied to every JSON under
# localized_data (story timelines, dicts) and to the voice bible.
NAME_FIXES = [
    # 理事長 Akikawa: Global never says "Chairwoman"; plates are "Director Akikawa",
    # bare address is "Director" (210 "Director Akikawa", 269 "Director", 0 "Chairwoman").
    ("Chairwoman Akikawa", "Director Akikawa"),
    ("Chairman Akikawa", "Director Akikawa"),
    ("Chairwoman Yayoi Akikawa", "Director Yayoi Akikawa"),

    # 保科健子 (furigana ホシナキヨコ, cat182). Our repo shipped four given names:
    # Takeshi (462 plates), Keiko (71), Kenko, Takeko. UmaTL cat6: Hoshina Kiyoko.
    ("Takeshi Hoshina", "Kiyoko Hoshina"),
    ("Keiko Hoshina", "Kiyoko Hoshina"),
    ("Kenko Hoshina", "Kiyoko Hoshina"),
    ("Hoshina Kiyoko", "Kiyoko Hoshina"),
    ("Hoshina Keiko", "Kiyoko Hoshina"),
    ("Takeko-san", "Kiyoko-san"),
    ("Bond with Takeko:", "Bond with Kiyoko:"),
    ("Takeshi-san", "Kiyoko-san"),
    ("hold it in, Takeshi.", "hold it in, Kiyoko."),
    ("Keiko-san", "Kiyoko-san"),

    # 都留岐涼花: 涼花 read すずか by mistake -> "Tsurugi Suzuka" (22 plates).
    ("Tsurugi Suzuka", "Ryoka Tsurugi"),
    ("Suzuka Tsurugi", "Ryoka Tsurugi"),
    ("Tsurugi Ryoka", "Ryoka Tsurugi"),

    # 佐岳メイ / 駿川たづな / 樫本理子 -- given-name-first.
    ("Satake Mei", "Mei Satake"),
    ("Hayakawa Tazuna", "Tazuna Hayakawa"),
    ("Kashimoto Riko", "Riko Kashimoto"),

    # リガントーナ is "Rigantona" (repo cat6, UmaTL); "Rigauntona" was a misreading.
    ("Rigauntona", "Rigantona"),
]

# Strings that must never be touched by NAME_FIXES even though they contain a
# replaced token.
NAME_KEEP = [
    "Takeshi-kun",        # bean farmer's son, 83/0279 -- unrelated character
    "Keiko (NPC)",        # generic NPC trainer label
    "Keiko Watanabe",
    "Takeshi Iwasaki",    # staff credits
    "Takeshi Masuda",
    "Keiko Hoshina, proprietress",  # handled by NAME_FIXES only if given name changes
]

# --- trainer-address policy ---------------------------------------------------
# 2026-11 policy (supersedes the 2026-10 flatten-to-"Trainer" pass): keep the JP
# flavour. The romaji stem トレ is carried as the literal "Tore-", followed by the
# honorific the horsegirl actually uses in JP:
#   トレーナーさん/さま/様/ちゃん/くん/君/殿/先輩
#       -> Tore-san / Tore-sama / Tore-chan / Tore-kun / Tore-dono / Tore-senpai
#   トレぴ/トレぴっぴ/トレぽよ/トレちゃん -> Tore-pi / Tore-pipi / Tore-poyo / Tore-chan
# Plain トレーナー with no honorific stays "Trainer"; 我が君/我が王/主 keep the
# knight register ("my liege" / "my King" / "my lord"). Applied 2026-11-16 to
# localized_data/character_system_text_dict.json (643 rows, 72 characters) and
# mirrored into uma_voice_bible.json trainer_term.
TRAINER_TERMS = {
    "default": "Tore-san",
    # 1065 Daitaku Helios -- gyaru nicknames. トレぴ -> "Tore-pi",
    # トレぴっぴ -> "Tore-pipi", トレぽよ -> "Tore-poyo"; ちゃんヘリ -> "Heliboss"
    # (her DJ persona). NB: her shipped cst rows still carry Global's "T-Rain"
    # (Global text_data 232/347, 232/575, 185/1065); "T-Rain" is not a "Trainer"
    # token, so the 2026-11 pass left it in place -- retranslate to use Tore-pi.
    "1065": {"term": "Tore-pi", "self": "Heliboss", "dim": "Tore-pipi"},
    # 1080 Transcend -- トレちゃん (20 JP lines) -> "Tore-chan".
    # (Old repo splits: Trai-chan 96, Trainy 89, Trainer-chan 53, Trainie 25,
    # Trainer 12, Trainey 4, Trainy-poo 4, dropped 19 -- all now Tore-chan.)
    "1080": {"term": "Tore-chan"},
    # 1121 Durandal -- knight register carried by "my liege" / "my King".
    #   我が王   -> "my King"   (36 lines; chapter titles already say My King)
    #   我が君   -> "my liege"  (64 lines; dominant existing form)
    #   主/主君  -> "my lord"
    #   トレーナー殿 -> "Tore-dono"
    "1121": {"term": "Tore-dono", "liege": "my liege", "king": "my King", "lord": "my lord"},
    # Characters whose applied form in cst is not the Tore-san default.
    "1004": {"term": "Tore-kun"},    # トレーナー君 (base costume; alt 101xx rows トレーナーちゃん)
    "1015": {"term": "Tore-kun"},    # トレーナー君 (El Condor Pasa; "fair Tore-kun")
    "1017": {"term": "Tore-kun"},    # トレーナー君
    "1023": {"term": "Tore-kun"},    # トレーナー君
    "1032": {"term": "Tore-kun"},    # トレーナーくん
    "1132": {"term": "Tore-kun"},    # トレーナーくん (alt 921xx/901xx rows トレーナーちゃん)
    "1024": {"term": "Tore-chan"},   # トレーナーちゃん
    "1072": {"term": "Tore-dono"},   # トレーナー殿 (Yaeno; 殿 kept, not dropped)
    "1074": {"term": "Tore-sama"},   # トレーナーさま
}

# --- voice evidence notes ------------------------------------------------------
# Per-character register facts mined from JP character_system_text + our EN,
# with Global cross-checks. These feed the LLM enrichment prompt so archetypes
# are grounded in dialogue instead of just the name + trait.
# Tags the miner over-fires on (validated by hand against JP lines, 2026-10-28):
# 1015/1039/1049 have no Kansai markers (1015 uses おる as archaic; 1049's まう was
# まァ and それな was それなり; 1039 is unrefined Tokyo speech). 1138's っしょ was a
# single line. Rebuild drops these even though voice_evidence.json still reports them.
TAG_DENY = {
    "1015": {"kansai-dialect"},
    "1039": {"kansai-dialect"},
    "1049": {"kansai-dialect"},
    "1138": {"gyaru-slang"},
}

# --- honorific normalisation --------------------------------------------------
# 2026-11 policy: JP honorifics on トレーナー are carried into EN as
# "Tore-" + honorific. This list canonicalises our own older spellings so a
# rebuild / normalize pass lands back on the shipped forms instead of flattening
# them to "Trainer". Plain "Trainer" (JP トレーナー with no honorific) is NOT
# touched -- it is the correct rendering for those rows.
HONORIFIC_FIXES = [
    ("Trainer-san's", "Tore-san's"),
    ("Trainer-sama's", "Tore-sama's"),
    ("Trainer-chan's", "Tore-chan's"),
    ("Trainer-kun's", "Tore-kun's"),
    ("Trainer-dono's", "Tore-dono's"),
    ("Trainer-senpai's", "Tore-senpai's"),
    ("Trainer-san", "Tore-san"),
    ("Trainer-sama", "Tore-sama"),
    ("Trainer-chan", "Tore-chan"),
    ("Trainer-kun", "Tore-kun"),
    ("Trainer-dono", "Tore-dono"),
    ("Trainer-senpai", "Tore-senpai"),
    # spacing/casing slips from older coinages
    ("Tore san", "Tore-san"),
    ("Tore sama", "Tore-sama"),
    ("Tore chan", "Tore-chan"),
    ("Tore kun", "Tore-kun"),
    ("Tore dono", "Tore-dono"),
]

# Speaker-scoped nickname normalisation (only inside that character's own blocks,
# so Vivlos' intentional "Trainy" and Loves Only You's lines are untouched).
SPEAKER_VOICE = {
    "Daitaku Helios": [
        ("Trainy-Peeey", "Tore-pi"), ("Trainy-Pi", "Tore-pi"), ("Trainy-pi", "Tore-pi"),
        ("Trainy-P", "Tore-pi"), ("Trainy-poo", "Tore-poyo"), ("Trainy-poyo", "Tore-poyo"),
        ("Trainynotes", "Tore-pinotes"), ("Trainy", "Tore-pi"),
        ("Trai-pippi", "Tore-pipi"), ("Trai-piii", "Tore-pi"), ("Trai-pi", "Tore-pi"),
        ("Trainer-pi", "Tore-pi"), ("Train-pi", "Tore-pi"),
        ("Trainie", "Tore-pi"), ("Trainey", "Tore-pi"),
        ("Heli-chan", "Heliboss"), ("Chan-Heli", "Heliboss"),
    ],
    "Transcend": [
        ("Trai-chan", "Tore-chan"), ("Trainy-poo", "Tore-chan"),
        ("Trainie", "Tore-chan"), ("Trainey", "Tore-chan"), ("Trainy", "Tore-chan"),
    ],
    # 我が君 -> my liege, 我が王 -> my King; bare "my lord" (主/主君) stays.
    "Durandal": [
        ("my Liege", "my liege"), ("My Liege", "My liege"),
        ("my Lord", "my liege"), ("My Lord", "My liege"),
        ("my king", "my King"), ("My king", "My King"),
    ],
    "Azuma": [("Trainer-sama", "my lord")],
}

VOICE_NOTES = {
    "1001": "Hokkaido dialect (なまら/したっけ); 私; calls trainer トレーナーさん.",
    "1007": "Chaotic trickster; theatrical register, non-sequiturs.",
    "1030": "Timid, self-deprecating; calls trainer お兄さま -> Global 'Big Brother' (34/37).",
    "1032": "Mad-scientist register; モルモット -> Global 'guinea pig' (8/8); ふぅン/したまえ.",
    "1052": "Endless optimism, loud; third-person ウララ -> mostly 'I' in Global (5/8 kept).",
    "1065": "Gyaru/party-girl slang; トレぴ 'Tore-pi', トレぴっぴ 'Tore-pipi', トレぽよ 'Tore-poyo'; ちゃんヘリ 'Heliboss'; third-person エル/ウチ.",
    "1080": "Casual info-broker; トレちゃん 'Tore-chan'; sly, clipped delivery.",
    "1121": "Knightly archaic register; 我が君 'my liege', 我が王 'my King', 主/主君 'my lord', トレーナー殿 'Tore-dono'.",
    "1072": "Hot-blooded martial artist; トレーナー殿 kept as 'Tore-dono' ('Face Tore-dono, bow!').",
    "1039": "Kansai dialect (ほんま/やけど/足らへん) -- current bible tags miss this.",
    "1049": "Kansai dialect; ウチ first person.",
    "1016": "Third-person カレン; calls trainer お兄ちゃん -> Global 'Big Bro' (27/48).",
    "1017": "Third-person ファル子; ですわ-ish idol register.",
    "1020": "Aristocratic ですわ (100 hits); refined, proud.",
    "1053": "ですわ (157 hits); princess affectation; 'Chairman' for committee roles only.",
    "1028": "Katakana English (85 hits, 50x cast average); ワタシ first person.",
    "1015": "Katakana English (87 hits, 64x cast average); lucha-libre hero register; third-person エル 74/245.",
    "1012": "Edokko register (お前さん, 〜だぜ); rough, big-sister tone.",
    "1004": "Third-person テイオー (28/305); ボク first person; カイチョー -> Global 'Prez' (16/16).",
    "9002": "Director Akikawa (Global); never 'Chairwoman'.",
    "9003": "Etsuko Otonashi; plates mostly 'Reporter Otonashi' (Global).",
    "9050": "Kiyoko Hoshina, Yukoma Ryokan proprietress; warm, motherly.",
    "9052": "Azuma, twelve-year priestess; archaic ritual register ('I shall lend my aid').",
}
