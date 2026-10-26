import sqlite3
import json
import re
import os

MASTER_DB_PATH = r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\UmamusumePrettyDerby_Jpn_Data\Persistent\master\master.mdb"
TEXT_DATA_DICT_PATH = r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\gemini_horses\localized_data\text_data_dict.json"
CST_DICT_PATH = r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\gemini_horses\localized_data\character_system_text_dict.json"
OUTPUT_PATH = r"G:\Games\steamapps\common\UmamusumePrettyDerby_Jpn\gemini_horses\tools\master_translate\master_untranslated.json"

JP_REGEX = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')

# Archetype dictionary for character voice guidance
ARCHETYPES = {
    1001: "Special Week: earnest, sweet, rural Hokkaido country-girl, polite watashi, energetic",
    1002: "Silence Suzuka: quiet, introspective kuudere, focused on running beyond the speed of sound",
    1003: "Tokai Teio: energetic boyish bokukko, prodigy, playful, refers to herself as Teio-sama",
    1004: "Maruzensky: 80s retro supercar big sister, bubbly, slangy Showa-era phrases, sporty",
    1005: "Fuji Kiseki: dashing gentlemanly prince/takarazuka style, charming, calls others boku/my pony",
    1006: "Oguri Cap: quiet glutton, sincere, blunt, humble legendary champion from Kasamatsu",
    1007: "Gold Ship: chaotic wild prankster, absurd nonsense humor, fourth-wall breaks, calls herself Golshi-sama",
    1008: "Vodka: cool rebellious tomboy biker/rocker, rough ore-style speech, pure-hearted inside",
    1009: "Daiwa Scarlet: proud tsundere honor student, competitive perfectionist, prickly but devoted",
    1010: "Taiki Shuttle: bright American cowgirl, enthusiastic broken English/Japanese, friendly gunner",
    1011: "Grass Wonder: calm graceful Yamato Nadeshiko, polite exterior with a fiery warrior spirit",
    1012: "Hishi Amazon: dependable big sister dormitory leader, rough-and-ready chivalrous tomboy",
    1013: "Mejiro McQueen: refined noble ojou-sama, elegant desu-wa speech, secretly obsessed with sweets",
    1014: "El Condor Pasa: fiery luchadora mask wrestler, bilingual Spanish/Japanese, lively and dramatic",
    1015: "TM Opera O: flamboyant theatrical opera king, bombastic self-absorbed narcissist, poetic genius",
    1016: "Narita Brian: stoic solitary lone wolf, fierce shadow roll champion, blunt masculine tone",
    1017: "Symboli Rudolf: majestic student council Emperor, philosophical puns, authoritative and paternal",
    1018: "Air Groove: strict cold Empress vice-president, hates foolishness, perfectionist duty-bound",
    1019: "Agnes Digital: hyperactive hardcore idol otaku, swoons over other umamusume, fan girl scream",
    1020: "Seiun Sky: laid-back lazy trickster, easygoing fishing enthusiast, sharp tactical mind",
    1021: "Tamamo Cross: fiery Osaka/Kansai dialect lightning girl, quick-witted working class tsukkomi",
    1022: "Fine Motion: sheltered Irish princess, gentle refined wonder, loves ramen and commoner food",
    1023: "Biwa Hayahide: analytical intellectual theorist, sensitive about her large head/hair",
    1024: "Mayano Top Gun: sweet flirty youngest sister, playful child-genius, calls trainer Captain",
    1025: "Manhattan Cafe: eerie gothic mystic, soft-spoken, converses with 'the shadow friend'",
    1026: "Mihono Bourbon: emotionless cyborg/mecha precision, speaks in formal computerized parameters",
    1027: "Mejiro Ryan: cheerful musclehead athletic tomboy, earnest, striving to be pretty too",
    1028: "Hishi Akebono: gentle giant chef girl, enormous appetite, bakes big meals for everyone",
    1029: "Yukino Bijin: pure Iwate Tohoku dialect country bumpkin, striving to be a glamorous city girl",
    1030: "Rice Shower: fragile timid sweet girl, easily tearful, refers to herself as Rice, heroic will",
    1031: "Ines Fujin: hardworking cheerful big sister, breadwinner for her siblings, energetic",
    1032: "Agnes Tachyon: mad scientist, eccentric experimentalist, fufufu laugh, calls trainer guinea pig",
    1033: "Admire Vega: solitary guilt-ridden star-gazer, distant, stoic, haunted by her lost twin",
    1034: "Inari One: fiery Edo downtown festival spirit, explosive traditional slang, righteous",
    1035: "Winning Ticket: overwhelmingly emotional crybaby, wears heart on sleeve, screams passion",
    1036: "Air Shakur: cynical foul-mouthed logic hacker, calculations-driven, tsundere genius",
    1037: "Eishin Flash: ultra-punctual German perfectionist, rigid schedule keeper, methodical",
    1038: "Curren Chan: charming influencer / modern idol, calculated cuteness, calls trainer Onii-chan/Onee-chan",
    1039: "Kawakami Princess: powerhouse tomboy obsessed with being an elegant anime princess",
    1040: "Gold City: blunt fashionable gyaru model, irritated by being judged only for looks",
    1041: "Sakura Bakushin O: screaming oblivious class rep, sprint-obsessed speed demon, Bakushin!",
    1042: "Seeking the Pearl: glamorous world-traveling diva, cosmopolitan flair, turns impossible to pearl",
    1043: "Shinko Windy: naughty biting gremlin, refers to herself as Windy-chan, impish troublemaker",
    1044: "Sweep Tosho: spoiled bratty witch apprentice, refuses training, stubborn but affectionate",
    1045: "Super Creek: overwhelmingly motherly, dotes on everyone, gentle pampering aura",
    1046: "Smart Falcon: hyper-enthusiastic top dirt umadol, cute idol facade, hardest worker",
    1047: "Zenno Rob Roy: quiet imaginative bookworm, heroic quest seeker, humble librarian vibe",
    1048: "Tosen Jordan: trendy modern gal/gyaru, airhead slang, nail-art lover, surprisingly loyal",
    1049: "Nakayama Festa: high-stakes outlaw gambler, lives on the razor edge, cool fatalist",
    1050: "Narita Taishin: prickly defensive kuudere, chip on her shoulder about small height, fierce",
    1051: "Nishino Flower: sweet gentle considerate young flower, polite, blooming talent",
    1052: "Haru Urara: relentlessly cheerful eternal optimist, zero wins, pure innocent sunshine",
    1053: "Bamboo Memory: burning hot-blooded disciplinary committee head, shouts about justice",
    1054: "Biko Pegasus: fiery superhero fan, energetic tokusatsu enthusiast, righteous kid",
    1055: "Marvelous Sunday: ultra-bubbly chaotic cheerleader of miracles, Marvelous☆ fever!",
    1056: "Matikanefukukitaru: eccentric superstition / fortune-telling maniac, shirikobadama!",
    1057: "Mr. C.B.: free-spirited carefree wanderer, follows the wind, charismatic champion",
    1058: "Meisho Doto: clumsy unlucky anxious klutz, perpetually apologetic, secretly monstrous power",
    1059: "Mejiro Dober: shy distrusting maiden, guarded against men, loves shoujo manga",
    1060: "Nice Nature: self-deprecating cynical girl-next-door, happy with 3rd place, secretly passionate",
    1061: "King Halo: haughty aristocratic high-class lady, stubborn pride, never gives up",
    1062: "Matikanetannhauser: lovable goofy klutz, 'Mambo~', nosebleeds, cheerful underdog",
    1063: "Ikuno Dictus: calm calculating iron lady, precise data analyst, quietly caring",
    1064: "Mejiro Palmer: easygoing runaway gal, escaped high-society pressure, party girl",
    1065: "Daitaku Helios: hyper party-animal gyaru, incomprehensible slang, loves Palmer and Ruby",
    1066: "Twin Turbo: full-throttle runaway rocket engine, childish pure speed, zero brakes",
    1067: "Satono Diamond: wealthy noble young lady, determined to break family jinxes",
    1068: "Kitasan Black: energetic festive festival girl, generous, neighborhood darling, bright",
    1069: "Sakura Chiyono O: earnest hardworking diary keeper, striving to reach Maruzensky's level",
    1070: "Sirius Symboli: charismatic rebellious alpha delinquent, arrogant, protective predator",
    1071: "Mejiro Ardan: delicate fragile glass-legged noblewoman, bittersweet elegance",
    1072: "Yaeno Muteki: disciplined martial artist, fiery bushido spirit, traditional kendo speech",
    1073: "Tsurumaru Tsuyoshi: sickly but infinitely passionate tri-crown dreamer, full throttle",
    1074: "Mejiro Bright: slow-paced gentle ditz noble lady, unflappable relaxed rhythm",
    1075: "Daring Tact: pure modest modern heroine, deep love for nature and the turf",
    1076: "Sakura Laurel: radiant spring cherry blossom, cheerful resilience through illness",
    1077: "Narita Top Road: squeaky-clean model honor student, earnest, admired by all",
    1078: "Yamanin Zephyr: poetic gentle breeze philosopher, reveres the wind and gentle running",
    1079: "Furioso: quiet respectful provincial exchange student, stoic dirt fighter",
    1080: "Transcend: tech-savvy digital informant, pragmatic, modern slang",
    1081: "Espoir City: feisty rebellious punk dirt runner, bark without bite, streetwise",
    1082: "North Flight: sparkling fashionista trendsetter, runway queen of the mile",
    1083: "Symboli Kris S: silent stoic mission executor, robotic efficiency, deep quiet honor",
    1084: "Tanino Gimlet: eccentric chuunibyou aesthetic god of destruction, fences-kicker, dramatic",
    1085: "Daiichi Ruby: regal untouchable high-nobility flower, icy elegance, duty to lineage",
    1086: "Mejiro Ramonu: enigmatic untouchable femme fatale, supreme tiara queen, passionate aloofness",
    1087: "Aston Machan: ethereal uncanny surreal doll girl, fears being forgotten, speaks in riddle",
    1088: "Satono Crown: charismatic turf magician, suave European-styled strategist",
    1089: "Cheval Grand: shy insecure middle child, harbored deep ambition to surpass her sisters",
    1090: "Verxina: proud competitive high-society diva, fiery second-place rival",
    1091: "Vivlos: naturally spoiled playful youngest sister, uses charm effortlessly, sweet",
    1092: "Dantsu Flame: round cute pushover, easily swept up in rivals' momentum, relatable",
    1093: "K.S. Miracle: gentle selfless angel, living on borrowed time, dedicated to miracles",
    1094: "Jungle Pocket: wild charismatic turf delinquent, roar of the beast, untamed roar",
    1095: "Believe: steadfast unyielding craftsman, disciplined sprint specialist",
    1096: "No Reason: carefree wanderer chasing dreams without reason, honest and free",
    1097: "Still in Love: intensely obsessive, burning thirst for devotion, sultry yet fragile",
    1098: "Copano Rickey: bright cheerful feng-shui advisor, bubbly Lucky-Lucky girl☆",
    1099: "Hokko Tarumae: pragmatic realist local idol, passionate Tomakomai city ambassador",
    1100: "Wonder Acute: wise grandmotherly veteran, calm, gentle, unyielding backbone",
    1101: "Samson Big: plucky small giant, keeps challenging stronger foes with huge heart",
    1102: "Sounds of Earth: romantic musical maestro, speaks of turf as a grand symphony",
    1103: "Royce and Royce: quirky tactical thinker, analytical pursuit of greatness from unique angles",
    1104: "Katsuragi Ace: bold lively trail-blazer, running with high ambition and swagger",
    1105: "Neo Universe: surreal cosmic philosopher, speaks in strange cosmic terminology",
    1106: "Hishi Miracle: lazy relaxed average-joe, zero ambition until forced, plain normal girl",
    1107: "Tap Dance City: romantic swashbuckling adventurer, Broadway dancer swagger",
    1108: "Duramente: intense high-bloodline prodigy, strict, explosive passion beneath stone face",
    1109: "Rhein Kraft: sunny sweet maiden chasing the tiara dream, bright and gentle",
    1110: "Cesario: dignified disciplined mentor and loving holy mother figure",
    1111: "Air Messiah: dutiful daughter carrying mother's legacy, earnest and composed",
    1112: "Daring Heart: dazzling queen of hearts, proud and competitive sparkler",
    1113: "Fusaichi Pandora: limitless hope and marshmallow heart, sweet and bubbly warmth♡",
    1114: "Buena Vista: universally adored earnest darling, humble champion",
    1115: "Orfevre: tyrannical turf sovereign, arrogant, golden despot of terror and majesty",
    1116: "Gentildonna: iron-willed powerhouse noblewoman, overwhelming physical grace and might",
    1117: "Win Variation: unbreakable underdog, undaunted by endless defeats against monsters",
    1118: "Admire Groove: solitary blue-silver flower, quiet and proud",
    1119: "Dream Journey: polite gentle mask concealing terrifying vicious beast within",
    1120: "Calstone Light O: pure linear bullet, talks only about straight lines and maximum speed",
    1121: "Durandal: loyal holy knight blade, poetic and devoted protector of honor",
    1124: "Bubble Gum Fellow: energetic point-man vanguard, bursting with fighting spirit",
    1126: "Sakura Chitose O: relaxed enlightened hermit sage, serene and easygoing",
    1127: "Fenomeno: stern tough-faced police officer, strong sense of justice and duty",
    1128: "Blast Onepiece: gentle giant forming deep unbreakable bonds with humans",
    1129: "Almond Eye: ultra-competitive supreme challenger, never tolerates losing, cute perfection",
    1130: "Lucky Lilac: proud noble blossom, radiant and dignified",
    1131: "Gran Alegria: cheerful radiant mile queen, bursting with pure running joy",
    1132: "Loves Only You: energetic international streamer, bubbling with love for everyone",
    1133: "Chrono Genesis: calm steadfast harbinger of a new era, cool elegance",
    1134: "Curren Bouquetd'or: lovely graceful bouquet, polite and endlessly supportive",
    1135: "Stay Gold: free-wheeling globe-trotting vagabond, wild and uncontainable",
    1136: "Red Desire: unyielding pure saint of the turf, blazing spirit",
    1137: "Kiseki: passionate dramatic creator, visionary pacing",
    1138: "Forever Young: ultra-cool charismatic modern gyaru, dazzling star",
    1139: "Casino Drive: suave visionary project leader, overseas swagger",
    1140: "Marche Lorraine: shy puppet girl observing the world from shadows",
    1141: "Epiphaneia: runaway train of destiny, emotional and explosive power",
    1142: "Logotype: cheerful energetic classic champion, fiery pride and bright smile",
    1143: "Victoire Pisa: warm messenger of hope connecting hearts across nations",
    1144: "Rose Kingdom: gentle graceful noble prince, refined, polite and elegant demeanor with a warm heart",
    1145: "Rulership: calculating ruler of the board, clever and composed",
    1146: "Efforia: noble lady sprinting alongside fate, dutiful and gentle",
    1148: "Titleholder: steadfast courageous frontrunner, calm unyielding determination",
    1149: "Phalaenopsis: elegant pure orchid beauty, graceful, refined pride and gentle warmth",
    2001: "Happy Meek: quiet mysterious rival, soft-spoken and earnest",
    9001: "Tazuna Hayakawa: polite Tracen Academy secretary, kind and informative",
    9002: "Chairwoman Akikawa: bombastic passionate academy chairwoman, shouts with fervor",
    9004: "Trainer Kiryuin: eager earnest rookie trainer, dedicated and sincere",
    9006: "Riko Kashimoto: strict no-nonsense administrator, hidden warmth",
    9008: "Light Hello: bubbly bright event producer, enthusiastic planner"
}

def safe_decode(b):
    if isinstance(b, str):
        return b
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("utf-8", errors="replace")

def get_context_type(cat):
    if cat in [28, 29, 32]:
        return "RACE_NAME"
    elif cat in [47]:
        return "SKILL_NAME"
    elif cat in [75, 76]:
        return "NAME_TITLE"
    elif cat in [77, 78]:
        return "NAME"
    elif cat in [88, 498]:
        return "STORY_NARRATION"
    elif cat in [401, 496]:
        return "LORE"
    elif cat in [139]:
        return "RITUAL"
    elif cat in [128]:
        return "LYRICS"
    elif cat in [48]:
        return "SKILL_DESC"
    elif cat in [67]:
        return "MISSION"
    elif cat in [181]:
        return "STORY_TITLE"
    elif cat in [204, 231]:
        return "PRESS_QUESTION"
    elif cat in [205, 232]:
        return "RACE_INTERVIEW"
    elif cat in [228, 229, 230]:
        return "FAN_OR_RESULT_COMMENT"
    elif cat in [429, 434]:
        return "SHORT_LABEL"
    elif cat in [464, 465]:
        return "EVENT_NAME"
    elif cat in [6, 7, 88, 92, 144, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173]:
        return "CHARACTER_LORE"
    else:
        return "UI_TEXT"

def main():
    print(f"Connecting to master.mdb: {MASTER_DB_PATH}")
    conn = sqlite3.connect(MASTER_DB_PATH)
    conn.text_factory = bytes
    cursor = conn.cursor()

    # Load existing translations
    with open(TEXT_DATA_DICT_PATH, "r", encoding="utf-8") as f:
        td_dict = json.load(f)
    with open(CST_DICT_PATH, "r", encoding="utf-8") as f:
        cst_dict = json.load(f)

    # Build character names map from category 6
    cursor.execute("SELECT `index`, text FROM text_data WHERE category = 6")
    char_names_jp = {idx: safe_decode(text) for idx, text in cursor.fetchall()}
    char_names_en = {}
    if "6" in td_dict:
        for idx_str, name in td_dict["6"].items():
            char_names_en[int(idx_str)] = name

    # New NPC in the 2026-10-24 scenario. No Global name exists yet.
    char_names_en[9052] = "Azuma"
    jp_to_en = {}
    for idx, jp_name in char_names_jp.items():
        en_name = char_names_en.get(idx)
        if en_name:
            jp_to_en[jp_name] = en_name
    jp_to_en["吾妻"] = "Azuma"

    entries = []

    # 1. Process character_system_text
    cursor.execute("SELECT character_id, voice_id, text FROM character_system_text")
    cst_rows = cursor.fetchall()
    cst_untrans = 0
    for cid, vid, raw_text in cst_rows:
        cid_str = str(cid)
        vid_str = str(vid)
        if cid_str in cst_dict and vid_str in cst_dict[cid_str] \
                and str(cst_dict[cid_str][vid_str]).strip():
            continue
        text = safe_decode(raw_text)
        if JP_REGEX.search(text):
            cst_untrans += 1
            spk_name = char_names_en.get(cid, char_names_jp.get(cid, f"Chara_{cid}"))
            arch = ARCHETYPES.get(cid, "Umamusume girl, earnest and spirited")
            entries.append({
                "id": f"cst_{cid}_{vid}",
                "type": "cst",
                "character_id": cid,
                "voice_id": vid,
                "speaker_name": spk_name,
                "speaker_archetype": arch,
                "context": "CHARACTER_VOICE",
                "jp": text
            })

    print(f"Untranslated character_system_text rows: {cst_untrans}")

    # 2. Process text_data
    cursor.execute("SELECT category, `index`, text FROM text_data")
    td_rows = cursor.fetchall()
    td_untrans = 0
    cat_counts = {}

    for cat, idx, raw_text in td_rows:
        cat_str = str(cat)
        idx_str = str(idx)
        if cat_str in td_dict and idx_str in td_dict[cat_str] \
                and str(td_dict[cat_str][idx_str]).strip():
            continue
        text = safe_decode(raw_text)
        if JP_REGEX.search(text):
            td_untrans += 1
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
            ctx = get_context_type(cat)

            entry = {
                "id": f"td_{cat}_{idx}",
                "type": "text_data",
                "category": cat,
                "index": idx,
                "context": ctx,
                "jp": text
            }

            if cat in [75, 76, 77, 78]:
                if cat in [77, 78]:
                    raw_name = text.strip()
                elif "]" in text:
                    raw_name = text.split("]", 1)[1].strip()
                else:
                    raw_name = ""
                hint = jp_to_en.get(raw_name)
                if hint:
                    entry["name_hint"] = f"{raw_name} -> {hint}"

            # If it's a character-specific category, attach speaker info
            if cat in [88, 144, 163] and idx in char_names_en:
                entry["speaker_name"] = char_names_en[idx]
                entry["speaker_archetype"] = ARCHETYPES.get(idx, "")
            elif cat in [205, 232]:
                # Generic post-race horsegirl response
                entry["speaker_archetype"] = "Horsegirl post-race winner/runner-up comment, spirited and polite"

            entries.append(entry)

    print(f"Untranslated text_data rows: {td_untrans}")
    print(f"Total untranslated entries to translate: {len(entries)}")

    output_data = {
        "total": len(entries),
        "cst_count": cst_untrans,
        "td_count": td_untrans,
        "category_breakdown": cat_counts,
        "entries": entries
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully saved dump to {OUTPUT_PATH} ({os.path.getsize(OUTPUT_PATH) / 1024 / 1024:.2f} MB)")

if __name__ == "__main__":
    main()
