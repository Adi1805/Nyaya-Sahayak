
import re
from bns_enrichment_data import BNS_ENRICHMENT
SECTION_TITLES = {
    "3": "Acts done by several persons in furtherance of common intention",
    "4": "Joint criminal liability",
    "45": "Abetment of an offence",
    "47": "Abetment in India of offences outside India",
    "61": "Criminal Conspiracy",
    "63": "Rape",
    "64": "Punishment for rape in certain cases",
    "65": "Rape on woman under twelve years of age",
    "66": "Rape on woman under sixteen years of age",
    "74": "Assault or criminal force to woman with intent to outrage modesty",
    "75": "Sexual harassment",
    "76": "Assault or use of criminal force with intent to disrobe",
    "77": "Voyeurism",
    "78": "Stalking",
    "79": "Word, gesture or act intended to insult modesty of a woman",
    "80": "Dowry death",
    "85": "Husband or relative subjecting woman to cruelty",
    "86": "Abetment of suicide of woman",
    "101": "Culpable homicide",
    "103": "Murder",
    "104": "Punishment for murder",
    "105": "Culpable homicide not amounting to murder",
    "106": "Causing death by negligence",
    "109": "Attempt to murder",
    "110": "Attempt to commit culpable homicide",
    "115": "Voluntarily causing hurt",
    "116": "Voluntarily causing grievous hurt",
    "117": "Voluntarily causing grievous hurt by dangerous weapons or means",
    "118": "Voluntarily causing hurt or grievous hurt by dangerous weapons or means",
    "119": "Voluntarily causing hurt to extort property or constrain to illegal act",
    "121": "Voluntarily causing hurt to extort confession or compel restoration of property",
    "123": "Causing hurt by means of poison etc with intent to commit offence",
    "125": "Act endangering life or personal safety of others",
    "126": "Wrongful restraint",
    "127": "Wrongful confinement",
    "128": "Wrongful confinement for three or more days",
    "129": "Wrongful confinement for ten or more days",
    "130": "Wrongful confinement to extort property or constrain to illegal act",
    "131": "Wrongful confinement to extort confession or compel restoration of property",
    "135": "Assault or criminal force",
    "137": "Kidnapping",
    "138": "Kidnapping from lawful guardianship",
    "139": "Kidnapping or abducting to compel for marriage etc",
    "140": "Kidnapping or abducting in order to murder or for ransom",
    "141": "Kidnapping or abducting to cause grievous hurt, slavery etc",
    "143": "Wrongfully concealing or keeping in confinement a kidnapped person",
    "281": "Rash driving or riding on a public way",
    "298": "Injuring or defiling place of worship with intent to insult religion",
    "299": "Deliberate and malicious acts intended to outrage religious feelings",
    "303": "Theft",
    "304": "Snatching",
    "305": "Theft in dwelling house or means of transportation or place of worship",
    "307": "Theft after preparation for causing death, hurt or restraint",
    "308": "Extortion",
    "309": "Robbery",
    "310": "Dacoity",
    "311": "Robbery or dacoity with attempt to cause death or grievous hurt",
    "314": "Dishonest misappropriation of property",
    "316": "Criminal breach of trust",
    "318": "Cheating",
    "319": "Cheating by personation",
    "320": "Cheating and dishonestly inducing delivery of property",
    "323": "Dishonestly receiving stolen property",
    "326": "Mischief by fire or explosive substance",
    "329": "Criminal trespass",
    "331": "House-trespass",
    "332": "House-trespass to commit offence",
    "333": "House-breaking",
    "336": "Forgery",
    "338": "Forgery for purpose of harming reputation",
    "340": "Forgery for purpose of cheating",
    "344": "Falsification of accounts",
    "351": "Criminal intimidation",
    "352": "Intentional insult to provoke breach of peace",
}
SUBSECTION_MAP = {
    "common_intention_multiple": {
        "base": "3", "display": "3(5)",
        "note": "Subsection (5): When a criminal act is done by several persons in furtherance of the common intention of all, each person is liable for the act as if it were done by him alone."
    },
    "criminal_conspiracy": {
        "base": "61", "display": "61(2)",
        "note": "Subsection (2): When two or more persons agree to do or cause to be done an illegal act, or a legal act by illegal means, such agreement is designated a criminal conspiracy."
    },
    "hurt_simple": {
        "base": "115", "display": "115(2)",
        "note": "Subsection (2): Whoever voluntarily causes hurt shall be punished with imprisonment up to one year, or fine up to ten thousand rupees, or both."
    },
    "extortion_death_threat": {
        "base": "308", "display": "308(4)",
        "note": "Subsection (4): If extortion is committed by putting any person in fear of death or of grievous hurt to that person or to any other, the punishment is imprisonment up to ten years and fine."
    },
    "intimidation_death_threat": {
        "base": "351", "display": "351(3)",
        "note": "Subsection (3): If the threat is to cause death or grievous hurt, or to cause destruction of property by fire, or to cause an offence punishable with death or imprisonment for life or for a term which may extend to seven years, punishment is up to seven years imprisonment, or fine, or both."
    },
    "negligent_death": {
        "base": "106", "display": "106(1)",
        "note": "Subsection (1): Whoever causes death of any person by doing any rash or negligent act not amounting to culpable homicide, shall be punished with imprisonment up to five years and fine."
    },
    "attempt_murder": {
        "base": "109", "display": "109(1)",
        "note": "Subsection (1): Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder."
    },
}
SPECIAL_ACTS_DB = {
    "arms_act_25_27": {
        "section_number": "Sections 25 & 27, Arms Act 1959",
        "chapter_name": "Arms Act, 1959 (Special Statute)",
        "short_title": "Illegal Possession & Use of Firearms",
        "punishment": "Sec 25: Min. 1 year, up to 3 years and fine; Sec 27: Min. 3 years, up to 7 years and fine (use in commission of offence)",
        "ipc_equivalent": "Arms Act 1959",
        "cognizable": "Cognizable",
        "bailable": "Non-bailable",
    },
    "it_act_66c": {
        "section_number": "Section 66C, IT Act 2000",
        "chapter_name": "Information Technology Act, 2000 (Special Statute)",
        "short_title": "Identity Theft Using Computer Resource",
        "punishment": "Up to 3 years imprisonment and fine up to Rs. 1 lakh",
        "ipc_equivalent": "IT Act 2000",
        "cognizable": "Cognizable",
        "bailable": "Bailable",
    },
    "it_act_66d": {
        "section_number": "Section 66D, IT Act 2000",
        "chapter_name": "Information Technology Act, 2000 (Special Statute)",
        "short_title": "Cheating by Personation Using Computer Resource",
        "punishment": "Up to 3 years imprisonment and fine up to Rs. 1 lakh",
        "ipc_equivalent": "IT Act 2000",
        "cognizable": "Cognizable",
        "bailable": "Bailable",
    },
    "ndps_act": {
        "section_number": "NDPS Act, 1985",
        "chapter_name": "Narcotic Drugs and Psychotropic Substances Act, 1985 (Special Statute)",
        "short_title": "Drug Trafficking & Possession",
        "punishment": "Small qty: up to 1 year; Commercial qty: 10-20 years rigorous imprisonment and fine",
        "ipc_equivalent": "NDPS Act",
        "cognizable": "Cognizable",
        "bailable": "Non-bailable",
    },
    "pocso_act": {
        "section_number": "POCSO Act, 2012",
        "chapter_name": "Protection of Children from Sexual Offences Act, 2012 (Special Statute)",
        "short_title": "Sexual Offences Against Children",
        "punishment": "3 years to life imprisonment depending on offence gravity",
        "ipc_equivalent": "POCSO Act",
        "cognizable": "Cognizable",
        "bailable": "Non-bailable",
    },
    "sc_st_act": {
        "section_number": "SC/ST (PoA) Act, 1989",
        "chapter_name": "SC/ST (Prevention of Atrocities) Act, 1989 (Special Statute)",
        "short_title": "Atrocities Against SC/ST Communities",
        "punishment": "6 months to 5 years imprisonment and fine",
        "ipc_equivalent": "SC/ST Act",
        "cognizable": "Cognizable",
        "bailable": "Non-bailable",
    },
    "dp_act": {
        "section_number": "Dowry Prohibition Act, 1961",
        "chapter_name": "Dowry Prohibition Act, 1961 (Special Statute)",
        "short_title": "Demanding or Giving Dowry",
        "punishment": "Min. 5 years and fine of Rs. 15,000 or dowry amount (whichever is more)",
        "ipc_equivalent": "Dowry Prohibition Act",
        "cognizable": "Cognizable",
        "bailable": "Non-bailable",
    },
    "mv_act_184": {
        "section_number": "Section 184, MV Act 1988",
        "chapter_name": "Motor Vehicles Act, 1988 (Special Statute)",
        "short_title": "Dangerous & Negligent Driving",
        "punishment": "First offence: up to 6 months or fine up to Rs. 1,000; Repeat: up to 2 years or fine up to Rs. 2,000",
        "ipc_equivalent": "MV Act",
        "cognizable": "Cognizable",
        "bailable": "Bailable",
    },
}
def _has_any(text, keywords):
    text_lower = text.lower()
    for kw in keywords:
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        if re.search(pattern, text_lower):
            return True
    return False
def _build_section_entry(sec_id, subsection_key=None, reason=""):
    meta = BNS_ENRICHMENT.get(sec_id, {})
    title = SECTION_TITLES.get(sec_id, f"BNS Section {sec_id}")
    display_section = sec_id
    subsection_note = ""
    if subsection_key and subsection_key in SUBSECTION_MAP:
        sub_info = SUBSECTION_MAP[subsection_key]
        display_section = sub_info["display"]
        subsection_note = sub_info["note"]
    doc_text = (
        f"Section {display_section}: {title}. "
        f"{subsection_note} "
        f"IPC Equivalent: {meta.get('ipc_eq', 'Unknown')}. "
        f"Punishment: {meta.get('punishment', 'Unknown')}. "
        f"Keywords: {meta.get('keywords', '')}."
    )
    return {
        "section_id": sec_id,
        "display_section": display_section,
        "title": title,
        "doc": doc_text,
        "meta": {
            "section": sec_id,
            "title": title,
            "chapter": meta.get("chapter", "Unknown"),
            "ipc_eq": meta.get("ipc_eq", "Unknown"),
            "punishment": meta.get("punishment", "Unknown"),
            "cognizable": meta.get("cognizable", "Unknown"),
            "bailable": meta.get("bailable", "Unknown"),
        },
        "reason": reason,
    }
def detect_crime_patterns(narrative, extracted_facts):
    facts_text = " ".join([
        str(extracted_facts.get(k, ""))
        for k in ["legal_concepts", "weapons", "injuries", "motive",
                   "case_title", "accused", "stolen_items", "complainant", "location"]
    ])
    full_text = f"{narrative} {facts_text}"
    injected = {}
    special = []
    guidance = []
    extra_queries = []
    forbidden = set()
    kidnap_kw = [
        "kidnap", "abduct", "abduction", "hostage", "ransom",
        "agwa", "utha liya", "bahrain", "fidya",
        "taken away forcibly", "held captive", "snatched away",
        "demand money for release", "forcibly taken", "captive"
    ]
    ransom_kw = [
        "ransom", "fidya", "demand money", "lakh", "crore",
        "pay up", "paisa", "transfer", "UPI", "50 lakh",
        "money for release"
    ]
    confine_kw = [
        "confined", "locked", "tied", "imprisoned", "detained",
        "held captive", "warehouse", "godown", "basement",
        "tied hands", "rope", "nylon", "chain", "handcuff",
        "bound", "captive", "holding", "confine", "confinement",
        "not allowed to leave", "prevented from leaving",
        "qaid", "band kamra", "rassi", "hathkadi",
        "hands tied", "legs tied", "blindfolded"
    ]
    group_kw = [
        "gang", "group of", "conspiracy", "planned", "mastermind",
        "alias", "together", "accomplice", "associate", "co-accused",
        "ring", "network", "organised", "organized", "henchmen",
        "goons", "associates", "saath", "milkar", "saazish",
        "planning", "hatched", "plotted", "orchestrated"
    ]
    firearm_kw = [
        "gun", "pistol", "katta", "firearm", "revolver", "rifle",
        "barrel", "trigger", "bullet", "ammunition", "cartridge",
        "country-made", "country made", "bandook", "tamancha",
        "desi katta", "shot", "fired", "gunpoint"
    ]
    weapon_kw = [
        "knife", "sword", "axe", "iron rod", "bat", "dagger",
        "sharp weapon", "blunt weapon", "machete", "lathi",
        "rod", "hockey stick", "chaaku", "talwar", "kulhadi",
        "acid", "tezaab", "chemical", "weapon"
    ]
    assault_kw = [
        "beat", "hit", "punch", "slap", "kick", "assault",
        "hurt", "injury", "bruise", "blood", "bleeding", "wound",
        "swollen", "black eye", "scratch", "bite", "push", "drag",
        "maara", "peeta", "thappad", "laat", "ghusa",
        "pulled hair", "baal kheencha", "attacked", "attack"
    ]
    death_threat_kw = [
        "kill", "murder threat", "death threat", "laash",
        "jaan se maar", "zinda nahi", "finish", "eliminate",
        "maar daalenge", "jaan le lenge", "khatam",
        "ungli kat", "seedha laash", "threat to kill",
        "threatened to kill", "threat of death",
        "fear of death", "will not survive", "alive nahi",
        "life in danger", "zinda dekhna hai", "laash milegi"
    ]
    intimidation_kw = [
        "threaten", "intimidat", "blackmail", "dhamki",
        "dharamki", "warning", "sabak sikhaunga", "dare",
        "challenge", "yaad rakh"
    ]
    grievous_kw = [
        "fracture", "permanent", "disfigure", "endanger life",
        "emasculate", "destroy eye", "loss of limb", "skull",
        "broken bone", "internal bleeding", "hospitalized",
        "ICU", "critical condition", "coma", "paralysis",
        "permanent disability", "permanent injury"
    ]
    rape_kw = [
        "rape", "raped", "sexual assault", "sexually assaulted",
        "ravish", "forced sex", "forced intercourse", "balatkar",
        "gang rape", "gangrape"
    ]
    sexual_harassment_kw = [
        "molestation", "molested", "grope", "groped",
        "sexual harassment", "outrage modesty", "indecent",
        "izzat looti", "chhed-chhaad", "sexual advances",
        "touched inappropriately", "disrobed"
    ]
    stalking_kw = [
        "stalking", "stalked", "following repeatedly",
        "followed repeatedly", "peechha", "watching",
        "monitoring movements", "cyber stalking"
    ]
    minor_kw = [
        "minor", "child", "underage", "below 18", "school",
        "juvenile", "bachcha", "naabaligh", "small boy",
        "small girl", "year old girl", "year old boy"
    ]
    dowry_kw = [
        "dowry", "stridhan", "dahej", "tilak",
        "demand money marriage", "wedding gifts", "gold jewelry",
        "in-laws demand", "sasural", "matrimonial", "dahej ki maang"
    ]
    cruelty_kw = [
        "cruelty", "torture", "torment", "harass", "mental torture",
        "physical torture", "verbal abuse", "domestic violence",
        "thrown out", "driven out of house", "not given food",
        "starved", "taunting", "humiliation", "taunt"
    ]
    marriage_kw = [
        "husband", "wife", "marriage", "married", "in-law",
        "wedding", "matrimonial", "shaadi", "vivah", "pati",
        "patni", "nikah"
    ]
    dowry_death_kw = [
        "died within 7 years", "suicide", "committed suicide",
        "set on fire", "hanging", "burnt alive", "poison",
        "died after marriage", "unnatural death"
    ]
    robbery_kw = [
        "rob", "robbed", "robbery", "loot", "looted", "dacoity",
        "dacoit", "armed robbery", "highway robbery"
    ]
    snatch_kw = [
        "snatch", "snatched", "snatching", "chain snatch",
        "chain snatching", "mobile snatch", "purse snatch"
    ]
    theft_kw = [
        "steal", "stole", "stolen", "theft", "thief", "chori",
        "pickpocket", "shoplifting"
    ]
    burglary_kw = [
        "break-in", "broke into", "burglary", "house-breaking",
        "forced entry", "trespassed and stole"
    ]
    cheat_kw = [
        "cheat", "cheated", "cheating", "fraud", "fraudulent",
        "deceive", "deceived", "deception", "swindle", "con",
        "scam", "ponzi", "scheme", "fake", "false promise",
        "misrepresentation", "dhoka", "thagi"
    ]
    forgery_kw = [
        "forge", "forged", "forgery", "fabricated", "falsified",
        "false document", "fake document", "counterfeit",
        "jaali", "farzi", "duplicate document"
    ]
    impersonation_kw = [
        "impersonate", "impersonation", "pretended to be",
        "posed as", "identity theft", "false identity",
        "fake identity", "nakal"
    ]
    embezzle_kw = [
        "embezzle", "misappropriate", "siphoned", "diverted funds",
        "breach of trust", "criminal breach", "misused funds"
    ]
    murder_kw = [
        "murder", "murdered", "killed", "stabbed to death",
        "shot dead", "beaten to death", "homicide", "hatya",
        "qatl", "dead body found", "found dead"
    ]
    attempt_murder_kw = [
        "attempt to murder", "tried to kill", "attempted murder",
        "nearly killed", "left for dead", "aimed gun at",
        "fired at", "stabbed", "tried to shoot", "tried to stab"
    ]
    negligent_death_kw = [
        "death by negligence", "died due to", "negligent act",
        "died in accident", "rash and negligent"
    ]
    cyber_kw = [
        "online", "whatsapp", "upi", "cyber", "computer", "otp",
        "phishing", "hacking", "digital", "internet", "social media",
        "email", "sms", "app", "website", "link", "bank transfer",
        "net banking", "debit card", "credit card", "gpay",
        "phonepe", "google pay", "paytm", "payment gateway"
    ]
    vehicle_kw = [
        "rash driving", "negligent driving", "hit and run",
        "over-speeding", "speeding", "zigzag", "wrong side",
        "drunk driving", "reckless driving", "overtaking",
        "lane change", "signal jump", "red light"
    ]
    vehicle_type_kw = [
        "car", "bike", "truck", "bus", "auto", "scooter",
        "motorcycle", "vehicle", "SUV", "lorry", "tempo",
        "flyover", "highway", "junction"
    ]
    extortion_kw = [
        "extort", "extortion", "blackmail", "hafta", "vasooli",
        "protection money", "demand money with threat",
        "pay or else", "pay or face consequences"
    ]
    trespass_kw = [
        "trespass", "entered property", "forced entry",
        "entered without permission", "unlawful entry",
        "ghar mein ghusa", "todkar ghusa", "broke in",
        "broke into house"
    ]
    arson_kw = [
        "set fire", "arson", "burnt", "burning", "explosive",
        "bomb", "blast", "petrol bomb", "molotov", "aag lagai",
        "fire to property", "incendiary"
    ]
    drug_kw = [
        "drugs", "narcotic", "ganja", "marijuana", "cocaine",
        "heroin", "meth", "amphetamine", "mdma", "lsd",
        "opium", "charas", "smack", "brown sugar", "contraband",
        "psychotropic", "drug trafficking", "peddling"
    ]
    scst_kw = [
        "scheduled caste", "scheduled tribe", "dalit", "caste slur",
        "caste discrimination", "caste-based", "atrocity", "untouchable",
        "jati", "caste abuse", "casteist remark"
    ]
    religious_kw = [
        "desecration", "temple", "mosque", "church", "gurudwara",
        "religious", "communal", "place of worship", "religious feelings",
        "idol", "scriptures"
    ]
    if not _has_any(full_text, rape_kw + sexual_harassment_kw + minor_kw):
        forbidden.update(["63", "64", "65", "66", "74", "75", "76", "77", "78", "79"])
    if not _has_any(full_text, cheat_kw + forgery_kw + impersonation_kw + embezzle_kw):
        forbidden.update(["314", "316", "318", "319", "320", "336", "338", "340", "344"])
    if not _has_any(full_text, dowry_kw + cruelty_kw + dowry_death_kw):
        forbidden.update(["80", "85", "86"])
    if not _has_any(full_text, murder_kw + attempt_murder_kw):
        forbidden.update(["101", "103", "104", "105", "109", "110"])
    if not _has_any(full_text, robbery_kw + snatch_kw + theft_kw + burglary_kw):
        forbidden.update(["303", "304", "305", "307", "309", "310", "311", "323", "329", "331", "332", "333"])
    if not _has_any(full_text, kidnap_kw + confine_kw):
        forbidden.update(["126", "127", "128", "129", "130", "131", "137", "138", "139", "140", "141", "143"])
    if not _has_any(full_text, vehicle_kw + vehicle_type_kw):
        forbidden.update(["281"])
    kidnap_kw = [
        "kidnap", "abduct", "abduction", "hostage", "ransom",
        "agwa", "utha liya", "bahrain", "fidya",
        "taken away forcibly", "held captive", "snatched away",
        "demand money for release", "forcibly taken", "captive"
    ]
    if _has_any(full_text, kidnap_kw):
        ransom_kw = [
            "ransom", "fidya", "demand money", "lakh", "crore",
            "pay up", "paisa", "transfer", "UPI", "50 lakh",
            "money for release"
        ]
        if _has_any(full_text, ransom_kw):
            injected["140"] = _build_section_entry("140",
                reason="The victim was kidnapped/abducted for the purpose of demanding ransom money.")
            guidance.append(
                "Section 140 (Kidnapping for Ransom) is the PRIMARY charge — "
                "carries death or life imprisonment. Do NOT also add Section 137 "
                "(basic Kidnapping) as 140 subsumes it.")
            injected["308"] = _build_section_entry("308", "extortion_death_threat",
                reason="Ransom demand with threats of death/harm constitutes extortion under Section 308(4).")
            guidance.append(
                "Use Section 308(4) (NOT 308 alone) — the extortion involves "
                "putting a person in fear of death or grievous hurt.")
        else:
            injected["137"] = _build_section_entry("137",
                reason="The victim was kidnapped/abducted from their location.")
    confine_kw = [
        "confined", "locked", "tied", "imprisoned", "detained",
        "held captive", "warehouse", "godown", "basement",
        "tied hands", "rope", "nylon", "chain", "handcuff",
        "bound", "captive", "holding", "confine", "confinement",
        "not allowed to leave", "prevented from leaving",
        "qaid", "band kamra", "rassi", "hathkadi",
        "hands tied", "legs tied", "blindfolded"
    ]
    if _has_any(full_text, confine_kw):
        injected["127"] = _build_section_entry("127",
            reason="The victim was confined in a space against their will, "
                   "preventing them from moving freely.")
        guidance.append(
            "Section 127 (Wrongful Confinement) MUST be included — the victim "
            "was held against their will in a confined space.")
        extra_queries.append(
            "wrongful confinement detained against will locked room "
            "tied hands rope prevented from leaving imprisoned")
    group_kw = [
        "gang", "group of", "conspiracy", "planned", "mastermind",
        "alias", "together", "accomplice", "associate", "co-accused",
        "ring", "network", "organised", "organized", "henchmen",
        "goons", "associates", "saath", "milkar", "saazish",
        "planning", "hatched", "plotted", "orchestrated"
    ]
    accused_text = str(extracted_facts.get("accused", "")).lower()
    has_multiple_accused = (
        _has_any(full_text, group_kw) or
        "," in accused_text or
        " and " in accused_text or
        _has_any(full_text, [
            "father-in-law", "mother-in-law", "brother-in-law",
            "sister-in-law", "sasur", "saas", "devar", "jeth", "nanad"
        ]) or
        _has_any(full_text, [
            "masked man", "masked men", "unknown persons",
            "several persons", "multiple attackers", "two persons",
            "three persons", "four persons", "all accused"
        ])
    )
    if has_multiple_accused:
        injected["61"] = _build_section_entry("61", "criminal_conspiracy",
            reason="Multiple accused persons conspired and planned the criminal act together.")
        injected["3"] = _build_section_entry("3", "common_intention_multiple",
            reason="The criminal act was done by several persons in furtherance of common intention.")
        guidance.append(
            "Section 61(2) (Criminal Conspiracy) and Section 3(5) (Common Intention) "
            "MUST be included because multiple accused persons acted together.")
        extra_queries.append(
            "criminal conspiracy agreement plan illegal act two or more persons "
            "common intention joint liability several persons")
    firearm_kw = [
        "gun", "pistol", "katta", "firearm", "revolver", "rifle",
        "barrel", "trigger", "bullet", "ammunition", "cartridge",
        "country-made", "country made", "bandook", "tamancha",
        "desi katta", "shot", "fired", "gunpoint"
    ]
    if _has_any(full_text, firearm_kw):
        special.append({
            **SPECIAL_ACTS_DB["arms_act_25_27"],
            "confidence": "Very High (95-100%)",
            "reason": "A firearm or country-made weapon was used or possessed "
                      "during the commission of the offence, violating the Arms Act."
        })
        guidance.append(
            "Arms Act Sections 25 and 27 MUST be applied — illegal possession "
            "and use of firearms in commission of offence.")
    weapon_kw = [
        "knife", "sword", "axe", "iron rod", "bat", "dagger",
        "sharp weapon", "blunt weapon", "machete", "lathi",
        "rod", "hockey stick", "chaaku", "talwar", "kulhadi",
        "acid", "tezaab", "chemical", "weapon"
    ]
    assault_kw = [
        "beat", "hit", "punch", "slap", "kick", "assault",
        "hurt", "injury", "bruise", "blood", "bleeding", "wound",
        "swollen", "black eye", "scratch", "bite", "push", "drag",
        "maara", "peeta", "thappad", "laat", "ghusa",
        "pulled hair", "baal kheencha", "attacked", "attack"
    ]
    has_weapon = _has_any(full_text, firearm_kw + weapon_kw)
    has_assault = _has_any(full_text, assault_kw)
    if has_weapon and has_assault:
        injected["118"] = _build_section_entry("118",
            reason="Dangerous weapons or means were used to voluntarily "
                   "cause hurt or grievous hurt to the victim.")
        extra_queries.append(
            "voluntarily causing hurt grievous hurt dangerous weapons "
            "means acid fire firearm")
    death_threat_kw = [
        "kill", "murder threat", "death threat", "laash",
        "jaan se maar", "zinda nahi", "finish", "eliminate",
        "maar daalenge", "jaan le lenge", "khatam",
        "ungli kat", "seedha laash", "threat to kill",
        "threatened to kill", "threat of death",
        "fear of death", "will not survive", "alive nahi",
        "life in danger", "zinda dekhna hai", "laash milegi"
    ]
    intimidation_kw = [
        "threaten", "intimidat", "blackmail", "dhamki",
        "dharamki", "warning", "sabak sikhaunga", "dare",
        "challenge", "yaad rakh"
    ]
    if _has_any(full_text, death_threat_kw):
        injected["351"] = _build_section_entry("351", "intimidation_death_threat",
            reason="The accused threatened the victim with death or grievous hurt, "
                   "constituting criminal intimidation of the gravest degree.")
        guidance.append(
            "Use Section 351(3) (NOT just 351) — the intimidation specifically "
            "involves a threat of DEATH or grievous hurt, carrying enhanced punishment.")
    elif _has_any(full_text, intimidation_kw):
        injected["351"] = _build_section_entry("351",
            reason="The accused threatened or intimidated the victim.")
    grievous_kw = [
        "fracture", "permanent", "disfigure", "endanger life",
        "emasculate", "destroy eye", "loss of limb", "skull",
        "broken bone", "internal bleeding", "hospitalized",
        "ICU", "critical condition", "coma", "paralysis",
        "permanent disability", "permanent injury"
    ]
    if _has_any(full_text, grievous_kw):
        if has_weapon:
            injected["117"] = _build_section_entry("117",
                reason="The victim suffered grievous hurt using dangerous "
                       "weapons or means, including fractures or permanent injuries.")
        else:
            injected["116"] = _build_section_entry("116",
                reason="The victim suffered grievous hurt including fractures, "
                       "permanent injuries, or life-threatening harm.")
    elif has_assault and "118" not in injected:
        injected["115"] = _build_section_entry("115", "hurt_simple",
            reason="The victim was subjected to physical violence causing "
                   "bodily pain, bruises, swelling, or other injuries.")
        guidance.append(
            "Section 115(2) applies for voluntarily causing hurt to the victim.")
    rape_kw = [
        "rape", "raped", "sexual assault", "sexually assaulted",
        "ravish", "forced sex", "forced intercourse", "balatkar",
        "gang rape", "gangrape"
    ]
    sexual_harassment_kw = [
        "molestation", "molested", "grope", "groped",
        "sexual harassment", "outrage modesty", "indecent",
        "izzat looti", "chhed-chhaad", "sexual advances",
        "touched inappropriately", "disrobed"
    ]
    stalking_kw = [
        "stalking", "stalked", "following repeatedly",
        "followed repeatedly", "peechha", "watching",
        "monitoring movements", "cyber stalking"
    ]
    minor_kw = [
        "minor", "child", "underage", "below 18", "school",
        "juvenile", "bachcha", "naabaligh", "small boy",
        "small girl", "year old girl", "year old boy"
    ]
    if _has_any(full_text, rape_kw):
        injected["63"] = _build_section_entry("63",
            reason="The victim was subjected to rape or sexual assault.")
        if _has_any(full_text, minor_kw):
            special.append({
                **SPECIAL_ACTS_DB["pocso_act"],
                "confidence": "Very High (95-100%)",
                "reason": "The victim is a minor/child, invoking POCSO Act."
            })
    if _has_any(full_text, sexual_harassment_kw):
        injected["75"] = _build_section_entry("75",
            reason="The victim was subjected to sexual harassment.")
        injected["74"] = _build_section_entry("74",
            reason="Criminal force was used against a woman with intent "
                   "to outrage her modesty.")
    if _has_any(full_text, stalking_kw):
        injected["78"] = _build_section_entry("78",
            reason="The accused repeatedly followed or contacted the victim against their will.")
    dowry_kw = [
        "dowry", "stridhan", "dahej", "tilak",
        "demand money marriage", "wedding gifts", "gold jewelry",
        "in-laws demand", "sasural", "matrimonial", "dahej ki maang"
    ]
    cruelty_kw = [
        "cruelty", "torture", "torment", "harass", "mental torture",
        "physical torture", "verbal abuse", "domestic violence",
        "thrown out", "driven out of house", "not given food",
        "starved", "taunting", "humiliation", "taunt"
    ]
    marriage_kw = [
        "husband", "wife", "marriage", "married", "in-law",
        "wedding", "matrimonial", "shaadi", "vivah", "pati",
        "patni", "nikah"
    ]
    dowry_death_kw = [
        "died within 7 years", "suicide", "committed suicide",
        "set on fire", "hanging", "burnt alive", "poison",
        "died after marriage", "unnatural death"
    ]
    if _has_any(full_text, dowry_kw) or (
        _has_any(full_text, cruelty_kw) and _has_any(full_text, marriage_kw)
    ):
        injected["85"] = _build_section_entry("85",
            reason="The woman was subjected to cruelty by her husband or "
                   "his relatives in connection with dowry demand.")
        special.append({
            **SPECIAL_ACTS_DB["dp_act"],
            "confidence": "Very High (95-100%)",
            "reason": "Dowry was demanded before, during, or after the "
                      "marriage, violating the Dowry Prohibition Act."
        })
        if _has_any(full_text, dowry_death_kw):
            injected["80"] = _build_section_entry("80",
                reason="The woman died within 7 years of marriage under "
                       "circumstances indicating dowry-related cruelty.")
    robbery_kw = [
        "rob", "robbed", "robbery", "loot", "looted", "dacoity",
        "dacoit", "armed robbery", "highway robbery"
    ]
    snatch_kw = [
        "snatch", "snatched", "snatching", "chain snatch",
        "chain snatching", "mobile snatch", "purse snatch"
    ]
    theft_kw = [
        "steal", "stole", "stolen", "theft", "thief", "chori",
        "pickpocket", "shoplifting"
    ]
    burglary_kw = [
        "break-in", "broke into", "burglary", "house-breaking",
        "forced entry", "trespassed and stole"
    ]
    if _has_any(full_text, robbery_kw):
        injected["309"] = _build_section_entry("309",
            reason="The accused committed robbery — theft with force or fear.")
        if has_weapon:
            injected["311"] = _build_section_entry("311",
                reason="Robbery with attempt to cause death or grievous hurt "
                       "using weapons.")
    elif _has_any(full_text, snatch_kw):
        injected["304"] = _build_section_entry("304",
            reason="The accused committed snatching of property from the victim.")
    elif _has_any(full_text, theft_kw):
        injected["303"] = _build_section_entry("303",
            reason="The accused committed theft of movable property.")
    if _has_any(full_text, burglary_kw):
        injected["331"] = _build_section_entry("331",
            reason="The accused committed house-trespass.")
        injected["333"] = _build_section_entry("333",
            reason="The accused committed house-breaking to gain entry.")
    cheat_kw = [
        "cheat", "cheated", "cheating", "fraud", "fraudulent",
        "deceive", "deceived", "deception", "swindle", "con",
        "scam", "ponzi", "scheme", "fake", "false promise",
        "misrepresentation", "dhoka", "thagi"
    ]
    forgery_kw = [
        "forge", "forged", "forgery", "fabricated", "falsified",
        "false document", "fake document", "counterfeit",
        "jaali", "farzi", "duplicate document"
    ]
    impersonation_kw = [
        "impersonate", "impersonation", "pretended to be",
        "posed as", "identity theft", "false identity",
        "fake identity", "nakal"
    ]
    embezzle_kw = [
        "embezzle", "misappropriate", "siphoned", "diverted funds",
        "breach of trust", "criminal breach", "misused funds"
    ]
    if _has_any(full_text, cheat_kw):
        injected["318"] = _build_section_entry("318",
            reason="The accused cheated through deception or false representation.")
    if _has_any(full_text, forgery_kw):
        injected["336"] = _build_section_entry("336",
            reason="The accused forged documents or records.")
        injected["340"] = _build_section_entry("340",
            reason="Forgery was committed for the purpose of cheating.")
    if _has_any(full_text, impersonation_kw):
        injected["319"] = _build_section_entry("319",
            reason="The accused cheated by pretending to be someone else.")
    if _has_any(full_text, embezzle_kw):
        injected["316"] = _build_section_entry("316",
            reason="The accused committed criminal breach of trust by "
                   "misappropriating property entrusted to them.")
    murder_kw = [
        "murder", "murdered", "killed", "stabbed to death",
        "shot dead", "beaten to death", "homicide", "hatya",
        "qatl", "dead body found", "found dead"
    ]
    attempt_murder_kw = [
        "attempt to murder", "tried to kill", "attempted murder",
        "nearly killed", "left for dead", "aimed gun at",
        "fired at", "stabbed", "tried to shoot", "tried to stab"
    ]
    negligent_death_kw = [
        "death by negligence", "died due to", "negligent act",
        "died in accident", "rash and negligent"
    ]
    if _has_any(full_text, murder_kw):
        injected["103"] = _build_section_entry("103",
            reason="The accused committed murder — intentionally causing "
                   "the death of a person.")
    elif _has_any(full_text, attempt_murder_kw):
        injected["109"] = _build_section_entry("109", "attempt_murder",
            reason="The accused attempted to murder the victim.")
    death_words = ["died", "death", "dead", "killed", "fatal", "deceased"]
    negligence_words = ["negligent", "negligence", "rash", "careless", "reckless"]
    if (_has_any(full_text, negligent_death_kw) or
        (_has_any(full_text, death_words) and _has_any(full_text, negligence_words))):
        injected["106"] = _build_section_entry("106", "negligent_death",
            reason="Death was caused by a rash or negligent act not "
                   "amounting to culpable homicide.")
    cyber_kw = [
        "online", "whatsapp", "upi", "cyber", "computer", "otp",
        "phishing", "hacking", "digital", "internet", "social media",
        "email", "sms", "app", "website", "link", "bank transfer",
        "net banking", "debit card", "credit card", "gpay",
        "phonepe", "google pay", "paytm", "payment gateway"
    ]
    if _has_any(full_text, cyber_kw):
        special.append({
            **SPECIAL_ACTS_DB["it_act_66d"],
            "confidence": "High (85-95%)",
            "reason": "Computer resources, communication devices, or digital "
                      "payment systems were used to facilitate the crime."
        })
        identity_kw = [
            "identity theft", "impersonate online", "fake profile",
            "hacking", "otp fraud", "phishing", "unauthorized access"
        ]
        if _has_any(full_text, identity_kw):
            special.append({
                **SPECIAL_ACTS_DB["it_act_66c"],
                "confidence": "High (85-95%)",
                "reason": "The accused committed identity theft or "
                          "unauthorized access using computer resources."
            })
    vehicle_kw = [
        "rash driving", "negligent driving", "hit and run",
        "over-speeding", "speeding", "zigzag", "wrong side",
        "drunk driving", "reckless driving", "overtaking",
        "lane change", "signal jump", "red light"
    ]
    vehicle_type_kw = [
        "car", "bike", "truck", "bus", "auto", "scooter",
        "motorcycle", "vehicle", "SUV", "lorry", "tempo",
        "flyover", "highway", "junction"
    ]
    if (_has_any(full_text, vehicle_kw) or
        (_has_any(full_text, vehicle_type_kw) and
         _has_any(full_text, negligence_words + ["speed", "accident", "crash"]))):
        injected["281"] = _build_section_entry("281",
            reason="The accused drove rashly or negligently on a public way, "
                   "endangering human life and safety.")
        injected["125"] = _build_section_entry("125",
            reason="The rash/negligent act endangered the life and personal "
                   "safety of others on the public road.")
        if _has_any(full_text, death_words):
            injected["106"] = _build_section_entry("106", "negligent_death",
                reason="Rash/negligent driving caused the death of a person.")
        special.append({
            **SPECIAL_ACTS_DB["mv_act_184"],
            "confidence": "High (85-95%)",
            "reason": "The vehicle was driven in a manner dangerous to the public."
        })
    extortion_kw = [
        "extort", "extortion", "blackmail", "hafta", "vasooli",
        "protection money", "demand money with threat",
        "pay or else", "pay or face consequences"
    ]
    if _has_any(full_text, extortion_kw) and "308" not in injected:
        if _has_any(full_text, death_threat_kw):
            injected["308"] = _build_section_entry("308", "extortion_death_threat",
                reason="The accused extorted money by putting the victim in "
                       "fear of death or grievous hurt.")
        else:
            injected["308"] = _build_section_entry("308",
                reason="The accused extorted money or property from the victim.")
    trespass_kw = [
        "trespass", "entered property", "forced entry",
        "entered without permission", "unlawful entry",
        "ghar mein ghusa", "todkar ghusa", "broke in",
        "broke into house"
    ]
    if _has_any(full_text, trespass_kw):
        injected["329"] = _build_section_entry("329",
            reason="The accused committed criminal trespass by unlawfully "
                   "entering the victim's property.")
    arson_kw = [
        "set fire", "arson", "burnt", "burning", "explosive",
        "bomb", "blast", "petrol bomb", "molotov", "aag lagai",
        "fire to property", "incendiary"
    ]
    if _has_any(full_text, arson_kw):
        injected["326"] = _build_section_entry("326",
            reason="The accused committed mischief by fire or explosive "
                   "substance, destroying or damaging property.")
    drug_kw = [
        "drugs", "narcotic", "ganja", "marijuana", "cocaine",
        "heroin", "meth", "amphetamine", "mdma", "lsd",
        "opium", "charas", "smack", "brown sugar", "contraband",
        "psychotropic", "drug trafficking", "peddling"
    ]
    if _has_any(full_text, drug_kw):
        special.append({
            **SPECIAL_ACTS_DB["ndps_act"],
            "confidence": "Very High (95-100%)",
            "reason": "The case involves possession, sale, or trafficking "
                      "of narcotic drugs or psychotropic substances."
        })
    scst_kw = [
        "scheduled caste", "scheduled tribe", "dalit", "caste slur",
        "caste discrimination", "caste-based", "atrocity", "untouchable",
        "jati", "caste abuse", "casteist remark"
    ]
    if _has_any(full_text, scst_kw):
        special.append({
            **SPECIAL_ACTS_DB["sc_st_act"],
            "confidence": "High (85-95%)",
            "reason": "The offence targets a person of Scheduled Caste or "
                      "Scheduled Tribe community."
        })
    religious_kw = [
        "desecration", "temple", "mosque", "church", "gurudwara",
        "religious", "communal", "place of worship", "religious feelings",
        "idol", "scriptures"
    ]
    if _has_any(full_text, religious_kw) and _has_any(full_text, [
        "damage", "destroy", "defile", "insult", "vandal", "arson", "attack"
    ]):
        injected["298"] = _build_section_entry("298",
            reason="The accused injured or defiled a place of worship with "
                   "intent to insult religion.")
        injected["299"] = _build_section_entry("299",
            reason="The accused committed deliberate and malicious acts "
                   "intended to outrage religious feelings.")
    companion_guidance = ""
    if guidance:
        companion_guidance = (
            "MANDATORY COMPANION SECTIONS (Crime Pattern Engine - Deterministic Legal Rules):\n"
            "The following sections have been identified by rule-based legal analysis and "
            "MUST be included in your selection:\n"
            + "\n".join(f"  - {line}" for line in guidance)
        )
    print(f"[*] Crime Pattern Engine: Detected {len(injected)} mandatory BNS sections "
          f"+ {len(special)} Special Acts")
    for sec_id, entry in injected.items():
        print(f"    [+] Section {entry['display_section']}: {entry['title']}")
    for sa in special:
        print(f"    [+] {sa['section_number']}: {sa['short_title']}")
    return {
        "injected_sections": injected,
        "special_acts": special,
        "companion_guidance": companion_guidance,
        "extra_queries": extra_queries,
        "mandatory_sections": list(injected.keys()),
    }
