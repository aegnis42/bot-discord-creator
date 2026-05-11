"""
Bot Discord — 404e RI "Les Disparus" (Wardens)

Commandes :
  /create        Crée toute la structure (rôles + salons + paramètres + boutons)
  /delete        Supprime tout (avec confirmation)
  /front <nom>   Crée un salon de front (Officier Comms+)
  /close_front <nom>  Archive un salon de front (Officier Comms+)

Variables d'environnement requises :
  DISCORD_TOKEN
"""

import os
import discord
from discord import app_commands
from discord.ext import commands

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


# ════════════════════════════════════════════════════════════════════
#  STYLE HELPERS
# ════════════════════════════════════════════════════════════════════
def _bold(s: str) -> str:
    out = ""
    for c in s:
        if "A" <= c <= "Z":   out += chr(0x1D400 + ord(c) - ord("A"))
        elif "a" <= c <= "z": out += chr(0x1D41A + ord(c) - ord("a"))
        elif "0" <= c <= "9": out += chr(0x1D7CE + ord(c) - ord("0"))
        else: out += c
    return out


def _bold_italic(s: str) -> str:
    out = ""
    for c in s:
        if "A" <= c <= "Z":   out += chr(0x1D468 + ord(c) - ord("A"))
        elif "a" <= c <= "z": out += chr(0x1D482 + ord(c) - ord("a"))
        else: out += c
    return out


def _strip_accents(s: str) -> str:
    return s.translate(str.maketrans(
        "àâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ",
        "aaaeeeeiioouuucAAAEEEEIIOOUUUC"))


def T(s: str) -> str:
    """Salon texte/forum : 『』𝐍𝐨𝐦"""
    return "『』" + _bold(_strip_accents(s))


def V(s: str) -> str:
    """Salon vocal : 】𝐍𝐨𝐦【"""
    return "】" + _bold(_strip_accents(s)) + "【"


def C(s: str) -> str:
    """Catégorie : ◆━━ 𝑵𝑨𝑴𝑬 ━━◆"""
    return "◆━━ " + _bold_italic(_strip_accents(s).upper()) + " ━━◆"


def SEP(s: str) -> str:
    """Rôle séparateur : 】ıllıllı NOM ıllıllı【"""
    return "】ıllıllı " + s + " ıllıllı【"


# ════════════════════════════════════════════════════════════════════
#  DONNÉES — Spécialités
# ════════════════════════════════════════════════════════════════════
# (nom, emoji, couleur_officier, couleur_membre, couleur_recrue)
SPECIALTIES = [
    ("Infanterie",   "🪖", 0x0D47A1, 0x1976D2, 0x64B5F6),  # bleu
    ("Blindés",      "🚗", 0x37474F, 0x546E7A, 0x90A4AE),  # bleu-gris
    ("Artillerie",   "💥", 0xBF360C, 0xE64A19, 0xFF8A65),  # rouge-orange
    ("Marine",       "⚓", 0x01579B, 0x0288D1, 0x4FC3F7),  # cyan
    ("Logistique",   "🚛", 0xF57F17, 0xFBC02D, 0xFFEE58),  # jaune-or
    ("Builder",      "🔨", 0x4E342E, 0x6D4C41, 0xA1887F),  # marron
    ("Médic",        "⚕️", 0x00695C, 0x009688, 0x4DB6AC),  # vert-teal
    ("Sniper-Recon", "🎯", 0x33691E, 0x558B2F, 0x9CCC65),  # olive
    ("Anti-Char",    "🚀", 0x4A148C, 0x6A1B9A, 0xAB47BC),  # violet
    ("Partisan",     "🗡️", 0x263238, 0x455A64, 0x78909C),  # gris-ombre
]
SPEC_NAMES = [s[0] for s in SPECIALTIES]


# ════════════════════════════════════════════════════════════════════
#  AUTO-ATTRIBUABLES (Boutons)
# ════════════════════════════════════════════════════════════════════
AVAILABILITIES = [
    ("Matin",       "🌅"),
    ("Après-midi",  "☀️"),
    ("Soir",        "🌆"),
    ("Nuit",        "🌙"),
    ("Weekend",     "📅"),
    ("Semaine",     "🗓️"),
]

NOTIFICATIONS = [
    ("Ping Ops",          "⚔️"),
    ("Ping Logi",         "🚛"),
    ("Ping Intel",        "🕵️"),
    ("Ping Événements",   "🎉"),
    ("Ping Recrutement",  "📋"),
]


# ════════════════════════════════════════════════════════════════════
#  RÔLES — Structure complète
# ════════════════════════════════════════════════════════════════════
COL_SEP = 0  # default color, ne masque pas le nom des membres groupés sous ce séparateur

OFFICIER_PERMS = {
    "manage_messages": True, "mute_members": True,
    "move_members": True, "manage_threads": True,
}

COMMANDANT_PERMS = {
    "manage_channels": True, "manage_roles": True,
    "kick_members": True, "ban_members": True,
    "manage_messages": True, "mute_members": True,
    "deafen_members": True, "move_members": True,
    "manage_nicknames": True, "manage_threads": True,
    "view_audit_log": True,
}


def build_roles():
    r = []

    # Haut Commandement
    r.append((SEP("COMMANDEMENT"), COL_SEP, {}, True, True))
    r.append(("Général",   0xFFD700, {"administrator": True}, False, False))
    r.append(("Colonel",   0xE91E63, {"administrator": True}, False, False))
    r.append(("Commandant",0xD32F2F, COMMANDANT_PERMS,        False, False))

    # Spécialités (3 grades par spec)
    for name, _emoji, c_off, c_mem, c_rec in SPECIALTIES:
        r.append((SEP(_strip_accents(name).upper()), COL_SEP, {}, True, True))
        r.append((f"Officier {name}", c_off, OFFICIER_PERMS, False, False))
        r.append((name,                c_mem, {},             False, False))
        r.append((f"Recrue {name}",    c_rec, {},             False, False))

    # Statuts
    r.append((SEP("STATUTS"), COL_SEP, {}, True, True))
    r.append(("Réserviste", 0xBDBDBD, {}, False, False))
    r.append(("Visiteur",   0x9E9E9E, {}, False, False))
    r.append(("Allié",      0x66BB6A, {}, False, False))

    # Fonctions transversales (non hoist)
    r.append((SEP("FONCTIONS"), COL_SEP, {}, True, False))
    r.append(("Recruteur",            0x00BCD4, {"manage_messages": True, "manage_threads": True}, False, False))
    r.append(("Formateur",            0x4CAF50, {"manage_messages": True, "manage_threads": True}, False, False))
    r.append(("Officier Logi",        0xFBC02D, {"manage_messages": True}, False, False))
    r.append(("Officier Intel",       0x673AB7, {"manage_messages": True}, False, False))
    r.append(("Officier Comms",       0x00838F, {"manage_channels": True, "manage_messages": True}, False, False))
    r.append(("Médiateur",            0xFF9800, {"manage_messages": True, "moderate_members": True}, False, False))
    r.append(("Event Manager",        0xE91E63, {"mention_everyone": True}, False, False))
    r.append(("Créateur de contenu",  0x2196F3, {}, False, False))
    r.append(("Ambassadeur",          0x009688, {}, False, False))

    # Distinctions (non hoist)
    r.append((SEP("DISTINCTIONS"), COL_SEP, {}, True, False))
    r.append(("Vétéran",         0xFFD700, {}, False, False))
    r.append(("Héros de Guerre", 0xFFC107, {}, False, False))
    r.append(("MVP du Mois",     0xF9A825, {}, False, False))
    r.append(("Donateur",        0xE91E63, {}, False, False))
    r.append(("Anniversaire",    0xFF80AB, {}, False, False))

    # Disponibilités (non hoist)
    r.append((SEP("DISPONIBILITES"), COL_SEP, {}, True, False))
    for av_name, _emoji in AVAILABILITIES:
        r.append((av_name, 0x90A4AE, {}, False, False))

    # Notifications opt-in (non hoist)
    r.append((SEP("NOTIFICATIONS"), COL_SEP, {}, True, False))
    for n_name, _emoji in NOTIFICATIONS:
        r.append((n_name, 0x607D8B, {}, False, False))

    return r


ROLES = build_roles()


# ════════════════════════════════════════════════════════════════════
#  MAPPING — Rôle fonctionnel → Rôle séparateur (auto-attribution)
# ════════════════════════════════════════════════════════════════════
# Quand un membre reçoit un rôle fonctionnel, le bot lui ajoute aussi
# le rôle séparateur correspondant. Comme c'est le séparateur qui est
# "hoist", c'est lui qui apparaît comme groupe dans la sidebar.
def _build_role_to_sep_map():
    m = {
        "Général":    SEP("COMMANDEMENT"),
        "Colonel":    SEP("COMMANDEMENT"),
        "Commandant": SEP("COMMANDEMENT"),
        "Réserviste": SEP("STATUTS"),
        "Visiteur":   SEP("STATUTS"),
        "Allié":      SEP("STATUTS"),
    }
    for spec_name, *_ in SPECIALTIES:
        sep = SEP(_strip_accents(spec_name).upper())
        m[f"Officier {spec_name}"] = sep
        m[spec_name] = sep
        m[f"Recrue {spec_name}"] = sep
    return m


ROLE_TO_SEP = _build_role_to_sep_map()
ALL_SEP_NAMES = set(ROLE_TO_SEP.values())


# ════════════════════════════════════════════════════════════════════
#  NIVEAUX D'ACCÈS (cumulatifs)
# ════════════════════════════════════════════════════════════════════
RECRUE_ROLES = [f"Recrue {s}" for s in SPEC_NAMES]
MEMBER_ROLES = list(SPEC_NAMES)
OFFICIER_ROLES = [f"Officier {s}" for s in SPEC_NAMES]
HIGH_COMMAND = ["Commandant", "Colonel", "Général"]

LVL_VISITEUR     = ["Visiteur", "Allié", "Réserviste"]
LVL_RECRUE       = LVL_VISITEUR + RECRUE_ROLES
LVL_SOLDAT       = LVL_RECRUE + MEMBER_ROLES
LVL_OFFICIER     = LVL_SOLDAT + OFFICIER_ROLES
LVL_COMMANDEMENT = LVL_OFFICIER + ["Commandant"]
LVL_ADMIN        = LVL_COMMANDEMENT + ["Colonel", "Général"]

# Combinaisons utiles
RECRUITERS = ["Recruteur"] + OFFICIER_ROLES + HIGH_COMMAND
COMMS_TEAM = ["Officier Comms"] + OFFICIER_ROLES + HIGH_COMMAND
INTEL_TEAM = ["Officier Intel"] + OFFICIER_ROLES + HIGH_COMMAND
LOGI_TEAM  = ["Officier Logi"] + OFFICIER_ROLES + HIGH_COMMAND


def specialty_access(spec_name: str) -> list:
    """Rôles autorisés à voir les salons d'une spécialité donnée."""
    return [f"Officier {spec_name}", spec_name, f"Recrue {spec_name}"] + HIGH_COMMAND


# ════════════════════════════════════════════════════════════════════
#  CATÉGORIES & SALONS
# ════════════════════════════════════════════════════════════════════
# Format d'un salon : (type, name, private_for, mode)
#   type        : "text" | "voice" | "forum"
#   private_for : None (public) | liste de rôles autorisés à voir
#   mode        : None | "readonly" (refuse send_messages au public)
# Pour les forums avec tags, ajouter un 5e élément : liste de noms de tags

def build_categories():
    cats = []


    cats.append({
        "name": C("ACCUEIL"),
        "private_for": None,
        "channels": [
            ("text",  T("bienvenue"),        None, "readonly"),
            ("text",  T("regles"),           None, "readonly"),
            ("text",  T("charte-militaire"), None, "readonly"),
            ("forum", T("presentations"),    None, None),
            ("text",  T("faq"),              None, "readonly"),
            ("text",  T("liens-utiles"),     None, "readonly"),
            ("text",  T("choix-roles"),      None, "readonly"),  # fusion des 3 anciens choix-*
        ],
    })

    cats.append({
        "name": C("RECRUTEMENT"),
        "private_for": None,  # catégorie publique pour que candidatures soit accessible
        "channels": [
            ("forum", T("candidatures"),     None, None),         # public : les candidats postent ici
            ("text",  T("salon-officiers"),  LVL_OFFICIER, None), # privé officiers
            ("text",  T("dossiers-recrues"), RECRUITERS, None),   # privé recruteurs
            ("voice", V("Entretien"),        RECRUITERS, None),   # privé recruteurs
        ],
    })

    cats.append({
        "name": C("ANNONCES"),
        "private_for": None,
        "channels": [
            ("text", T("annonces"),          None, "readonly"),
            ("text", T("patch-notes"),       None, "readonly"),
            ("text", T("etat-de-la-guerre"), None, "readonly"),
            ("text", T("evenements"),        None, "readonly"),
        ],
    })

    cats.append({
        "name": C("COMMUNAUTE"),
        "private_for": None,
        "channels": [
            ("text",  T("general"),     None, None),
            ("forum", T("partages"),    None, None, ["Memes", "Screenshots", "Clips", "Fanart", "Builds", "Autres"]),
            ("forum", T("suggestions"), None, None),
            ("voice", V("General"),     None, None),
            ("voice", V("Musique"),     None, None),
            ("voice", V("AFK"),         None, None),
        ],
    })

    cats.append({
        "name": C("OPS COMMANDEMENT"),
        "private_for": LVL_SOLDAT,
        "channels": [
            ("text",  T("plan-de-bataille"), LVL_OFFICIER, None),
            ("text",  T("ordres"),           None, None),                 # fusion ordres-du-jour + objectifs-prioritaires
            ("forum", T("debriefings"),      None, None),
            ("text",  T("etat-major"),       LVL_COMMANDEMENT, None),
            ("voice", V("Officiers"),        LVL_OFFICIER, None),
        ],
    })

    cats.append({
        "name": C("OPS FRONTS"),
        "private_for": LVL_SOLDAT,
        "channels": [
            ("text",  T("comms"), None, None),  # fusion réserve + évacuation
            ("voice", V("QG"),    None, None),
        ],
    })

    cats.append({
        "name": C("LOGISTIQUE"),
        "private_for": LVL_SOLDAT,
        "channels": [
            ("forum", T("demandes-logi"),     None, None),
            ("forum", T("production"),        None, None, ["BMats", "RMats", "EMats", "HEMats", "Vehicules", "Armement"]),
            ("text",  T("convois"),           None, None),
            ("text",  T("stockpiles"),        None, None),
            ("text",  T("comms-logi"),        None, None),
            ("voice", V("Coordination-Logi"), None, None),
        ],
    })

    cats.append({
        "name": C("RENSEIGNEMENT"),
        "private_for": LVL_SOLDAT,
        "channels": [
            ("forum", T("intel"),                 None, None, ["Cartes", "Recon", "Bases ennemies", "Convois ennemis", "Mouvements"]),
            ("forum", T("analyses-strategiques"), LVL_OFFICIER, None),
        ],
    })

    # SPECIALITES — 1 salon texte par spec, privé à sa spec (pas de vocal, géré par le bot on-demand plus tard)
    spec_channels = []
    for name, _e, *_ in SPECIALTIES:
        spec_channels.append(("text", T(name), specialty_access(name), None))
    cats.append({
        "name": C("SPECIALITES"),
        "private_for": None,
        "channels": spec_channels,
    })

    cats.append({
        "name": C("FORMATION"),
        "private_for": LVL_RECRUE,
        "channels": [
            ("forum", T("academie"),             None, None, ["Débutant", "Infanterie", "Blindés", "Artillerie", "Marine", "Logistique", "Construction", "Médic", "Snipers-Recon", "Anti-Char", "Partisan", "Bibliothèque"]),
            ("text",  T("exercices-programmes"), None, None),
            ("voice", V("Salle-Cours"),          None, None),
        ],
    })

    cats.append({
        "name": C("BOTS"),
        "private_for": LVL_RECRUE,
        "channels": [
            ("text", T("outils-bot"), None, None),  # fusion : commandes + stats + classements + calculatrices
        ],
    })

    cats.append({
        "name": C("ARCHIVES"),
        "private_for": LVL_SOLDAT,
        "channels": [
            ("forum", T("archives"), None, None, ["Guerres", "Opérations", "Vétérans", "Mémorial"]),
        ],
    })

    cats.append({
        "name": C("SUPPORT"),
        "private_for": None,
        "channels": [
            ("forum", T("support"), None, None, ["Aide technique", "Aide Discord", "Contact staff", "Signalement"]),
        ],
    })

    return cats


CATEGORIES = build_categories()


# ════════════════════════════════════════════════════════════════════
#  MESSAGES D'ACCUEIL
# ════════════════════════════════════════════════════════════════════
WELCOME_MESSAGES = {
    T("bienvenue"): {
        "title": "👋 Bienvenue au 404e RI \"Les Disparus\"",
        "color": 0x1976D2,
        "description": (
            "**Introuvables, indomptables.**\n\n"
            "Tu rejoins un régiment Wardens dédié à la coordination, la logistique et la maîtrise du terrain.\n\n"
            "**Tes premières étapes :**\n"
            "1. Lis le **règlement** et la **charte militaire**\n"
            "2. Présente-toi dans **présentations**\n"
            "3. Choisis ta **spécialité** dans choix-specialite (boutons)\n"
            "4. Sélectionne tes **disponibilités** et **notifications**\n"
            "5. Postule via le forum **candidatures**\n\n"
            "Un Recruteur viendra te chercher pour l'entretien. Bon vent, soldat."
        ),
    },
    T("regles"): {
        "title": "📜 Règlement du serveur",
        "color": 0xE91E63,
        "description": (
            "**Respect absolu**\n"
            "1. Pas de toxicité, racisme, sexisme, discrimination.\n"
            "2. Pas de spam, pub, ou contenu NSFW.\n"
            "3. Anglais toléré, français prioritaire.\n\n"
            "**Vie du serveur**\n"
            "4. Utilise les bons salons (memes dans Communauté/Partages, pas dans Ops).\n"
            "5. Ping responsable : @role uniquement si pertinent.\n"
            "6. Une candidature par compte (pas de multi-compte).\n"
            "7. Pas de pub pour serveurs concurrents.\n\n"
            "**Sanctions**\n"
            "• 1er avertissement : oral\n"
            "• 2e : retrait de fonction / rétrogradation\n"
            "• 3e : exclusion\n\n"
            "*En restant sur ce serveur, tu acceptes ces règles.*"
        ),
    },
    T("charte-militaire"): {
        "title": "🪖 Charte militaire",
        "color": 0x0D47A1,
        "description": (
            "**Code de conduite en opération**\n\n"
            "1. **Chaîne de commandement** — Suis les ordres des officiers pendant les ops.\n"
            "2. **OPSEC** — Ne partage pas d'intel sensible à l'extérieur.\n"
            "3. **Comms claires** — Texte concis et précis dans les salons live.\n"
            "4. **Pas de teamkill** — Friendly fire intentionnel = exclusion immédiate.\n"
            "5. **Représentation** — Pas de toxicité envers les alliés. Tu portes l'écusson.\n"
            "6. **Tricheurs** — Pas de cheats, exploits, ou triche. Exclusion immédiate.\n"
            "7. **Absences** — Préviens un officier si tu pars en pause.\n"
            "8. **Inactivité** — 14 jours sans signe = rétrogradation Réserviste.\n\n"
            "**Devise :** *Introuvables, indomptables.*"
        ),
    },
    T("faq"): {
        "title": "❓ FAQ",
        "color": 0x607D8B,
        "description": (
            "**Comment rejoindre le régiment ?**\n"
            "→ Poste ta candidature dans le forum **candidatures**.\n\n"
            "**Quelle spécialité choisir ?**\n"
            "→ Lis les descriptions dans **choix-specialite**. Tu peux en changer plus tard.\n\n"
            "**Faut-il jouer tous les jours ?**\n"
            "→ Non. Préviens juste si tu pars en pause prolongée.\n\n"
            "**Anglais accepté ?**\n"
            "→ Toléré mais le français prime.\n\n"
            "**Faction du régiment ?**\n"
            "→ Wardens uniquement."
        ),
    },
    T("liens-utiles"): {
        "title": "🔗 Liens utiles",
        "color": 0x2196F3,
        "description": (
            "**Wiki officiel** — https://foxhole.wiki.gg\n"
            "**Carte interactive** — https://foxholestats.com\n"
            "**Reddit** — https://reddit.com/r/foxholegame\n"
            "**Calculateur logi** — https://logiwaze.com\n"
            "**Calculateur artillerie** — https://www.foxholeartillery.com\n"
            "**Wiki Wardens** — https://foxhole.wiki.gg/wiki/Wardens\n"
            "**Steam** — https://store.steampowered.com/app/505460/Foxhole/"
        ),
    },
    T("choix-roles"): {
        "title": "🎖️ Personnalise ton profil",
        "color": 0xFBC02D,
        "description": (
            "Ce salon contient **3 panneaux** pour te configurer :\n\n"
            "**1️⃣ Ta spécialité** — la branche que tu intègres (Infanterie, Blindés, etc.)\n"
            "**2️⃣ Tes disponibilités** — les créneaux où tu joues habituellement\n"
            "**3️⃣ Tes notifications** — les types de pings que tu acceptes de recevoir\n\n"
            "Clique sur les boutons des sections plus bas. Tu peux changer tes choix à tout moment."
        ),
    },
    T("candidatures"): {
        "title": "📋 Comment postuler",
        "color": 0x00BCD4,
        "description": (
            "Ouvre un nouveau post avec ton pseudo Foxhole comme titre, et utilise ce template :\n\n"
            "```\n"
            "• Pseudo Foxhole :\n"
            "• Profil Steam (URL) :\n"
            "• Heures de jeu :\n"
            "• Spécialité(s) souhaitée(s) :\n"
            "• Fuseau horaire :\n"
            "• Disponibilités (jours/heures) :\n"
            "• Régiments précédents (si applicable) :\n"
            "• Pourquoi le 404e RI ?\n"
            "• Quelque chose à ajouter ?\n"
            "```\n\n"
            "Un Recruteur te contactera dans les 48h pour un entretien vocal."
        ),
    },
    T("presentations"): {
        "title": "👤 Présente-toi",
        "color": 0x3F51B5,
        "description": (
            "Ouvre un post avec ton pseudo Foxhole comme titre et raconte-nous qui tu es :\n\n"
            "```\n"
            "• Pseudo Foxhole :\n"
            "• D'où viens-tu (pays/région) :\n"
            "• Depuis quand tu joues à Foxhole :\n"
            "• Tes spécialités préférées :\n"
            "• Ce que tu fais dans la vie (optionnel) :\n"
            "• Un fun fact :\n"
            "```"
        ),
    },
    T("debriefings"): {
        "title": "📝 Format des debriefings",
        "color": 0x795548,
        "description": (
            "Ouvre un post par opération. Titre : `[DATE] - [OPÉRATION/HEX]`. Template :\n\n"
            "```\n"
            "• Date / heure :\n"
            "• Hex / Front :\n"
            "• Objectif initial :\n"
            "• Effectifs engagés :\n"
            "• Résultat (succès/échec/partiel) :\n"
            "• Ce qui a bien fonctionné :\n"
            "• Ce qui a mal fonctionné :\n"
            "• Pertes (humaines/matériel) :\n"
            "• Leçons retenues :\n"
            "```"
        ),
    },
    T("suggestions"): {
        "title": "💡 Format des suggestions",
        "color": 0x009688,
        "description": (
            "Ouvre un post avec ta suggestion. Sois clair et concis :\n\n"
            "```\n"
            "• Domaine concerné (Discord / Régiment / Ops / Logi / autre) :\n"
            "• Suggestion :\n"
            "• Pourquoi (quel problème ça résout) :\n"
            "• Idées d'implémentation (si applicable) :\n"
            "```\n\n"
            "Les membres peuvent voter en réaction. Les officiers traiteront les suggestions actives."
        ),
    },
    T("demandes-logi"): {
        "title": "🚛 Format des demandes logi",
        "color": 0xF57F17,
        "description": (
            "Ouvre un post par demande. Titre : `[URGENCE] [HEX] [TYPE]`. Template :\n\n"
            "```\n"
            "• Quoi (matériel précis + quantité) :\n"
            "• Où (hex de destination, stockpile/base) :\n"
            "• Quand (urgent / sous 24h / pas pressé) :\n"
            "• Pourquoi (front actif / réserve / production) :\n"
            "• Code base (si privé) :\n"
            "• Qui livre / qui réceptionne :\n"
            "```\n\n"
            "Cocher comme **résolu** une fois la demande livrée."
        ),
    },
    T("analyses-strategiques"): {
        "title": "🧠 Format des analyses stratégiques",
        "color": 0x880E4F,
        "description": (
            "**Salon réservé aux Officiers.** Pour les analyses approfondies du conflit en cours :\n\n"
            "```\n"
            "• Sujet de l'analyse :\n"
            "• Front / hex concerné :\n"
            "• Situation actuelle (côtés Wardens et Colonials) :\n"
            "• Hypothèses sur l'intention adverse :\n"
            "• Options stratégiques pour notre camp :\n"
            "• Recommandation :\n"
            "• Risques / contre-indications :\n"
            "```"
        ),
    },
}


# ════════════════════════════════════════════════════════════════════
#  POSTS DE DÉMARRAGE — Forum 『』partages
# ════════════════════════════════════════════════════════════════════
# Un post par tag, créé et épinglé automatiquement par /create.
PARTAGES_STARTER_POSTS = [
    # (tag, titre, description, couleur)
    ("Memes",       "🤣 Memes Foxhole",
     "Postez ici vos memes liés à Foxhole, à la communauté, aux situations "
     "absurdes en jeu, aux mèmes recyclés de la guerre actuelle...\n\n"
     "**Règles :** rien de raciste, sexiste ou discriminatoire. Le reste passe.",
     0xFFB300),
    ("Screenshots", "📸 Captures d'écran",
     "Vos plus belles captures du jeu : combats, paysages, scènes épiques, "
     "kill confirmés, moments dramatiques...\n\n"
     "Si possible, précise le hex et le contexte dans ton post.",
     0x42A5F5),
    ("Clips",       "🎬 Clips & vidéos",
     "Vos meilleurs moments en vidéo : actions, fails, exploits, "
     "compilations de kills, ambush épiques...\n\n"
     "Formats acceptés : liens YouTube, Twitch, Medal, ou upload Discord direct (≤ 25 Mo).",
     0xE91E63),
    ("Fanart",      "🎨 Créations artistiques",
     "Vos dessins, montages, créations 3D, peintures, sculptures... "
     "Tout ce qui touche à l'univers Foxhole de près ou de loin.\n\n"
     "Crédite les artistes si tu partages le travail de quelqu'un d'autre.",
     0xAB47BC),
    ("Builds",      "🏗️ Bases & constructions",
     "Présente tes bases, FOB, bunkers, défenses, fortifications, "
     "bases logi, hospices, dépôts...\n\n"
     "**Bonus** si tu mets une carte annotée du build ou un guide de construction.",
     0x6D4C41),
    ("Autres",      "📦 Autres partages",
     "Catégorie fourre-tout pour ce qui ne rentre pas dans les autres tags : "
     "anecdotes, histoires de guerre, partages liés au jeu mais hors-format.",
     0x90A4AE),
]

# ════════════════════════════════════════════════════════════════════
#  POSTS DE DÉMARRAGE — Forum production (LOGISTIQUE)
# ════════════════════════════════════════════════════════════════════
PRODUCTION_STARTER_POSTS = [
    ("BMats",     "🟫 Production BMats",     "Coordination de la production des matériaux de base (Basic Materials). Postez ici les besoins en BMats, les fonderies actives, et les volumes produits.", 0x6D4C41),
    ("RMats",     "🟧 Production RMats",     "Coordination du raffinage en Refined Materials. Notez les usines actives et les stocks disponibles.", 0xD35400),
    ("EMats",     "💥 Production EMats",     "Coordination de la production d'Explosive Materials. Critique pour la munition AT et l'artillerie.", 0xC0392B),
    ("HEMats",    "🚀 Production HEMats",    "Coordination de la production d'Heavy Explosive Materials. Indispensable pour les rockets, mortiers lourds, ATGM.", 0xE74C3C),
    ("Vehicules", "🚗 Production véhicules", "Coordination de la production de véhicules : tankers, half-tracks, camions logi, navires.", 0x34495E),
    ("Armement",  "🔫 Production armement",  "Coordination de la production d'armes individuelles et munitions : fusils, mortiers, MG, AT léger.", 0x7F8C8D),
]


# ════════════════════════════════════════════════════════════════════
#  POSTS DE DÉMARRAGE — Forum academie (FORMATION)
# ════════════════════════════════════════════════════════════════════
ACADEMIE_STARTER_POSTS = [
    ("Débutant",      "🎓 Guide du débutant",        "Les bases du jeu pour les nouvelles recrues : interface, mouvement, premier équipement, premiers réflexes. **Si tu débutes, lis d'abord ce post avant tout le reste.**", 0x4CAF50),
    ("Infanterie",    "🪖 Formation Infanterie",     "Tactiques d'infanterie, choix d'armement, mouvement en équipe, défense de tranchées, assaut.", 0x7F8C8D),
    ("Blindés",       "🚗 Formation Blindés",        "Opération de char : conduite, tir, communication équipage. Doctrine d'engagement, points faibles ennemis.", 0x37474F),
    ("Artillerie",    "💥 Formation Artillerie",     "Calculs de tir, doctrine, contre-batterie, observation, coordination avec spotter.", 0xBF360C),
    ("Marine",        "⚓ Formation Marine",         "Navigation, opération de navires, débarquements, ravitaillement maritime.", 0x01579B),
    ("Logistique",    "🚛 Formation Logistique",     "Chaînes de production, convois, scoop, stockage, codes bases.", 0xF57F17),
    ("Construction",  "🔨 Formation Construction",   "Bunkers, FOB, défenses, garnisons, lignes de tranchées.", 0x4E342E),
    ("Médic",         "⚕️ Formation Médic",          "Soins de combat, évacuation, trauma center, gestion de blessés.", 0x00695C),
    ("Snipers-Recon", "🎯 Formation Snipers / Recon","Observation longue distance, tir précis, infiltration, rapport recon.", 0x33691E),
    ("Anti-Char",     "🚀 Formation Anti-Char",      "Tactiques AT : RPG, mines, satchel, chasseurs de chars.", 0x4A148C),
    ("Partisan",      "🗡️ Formation Partisan",       "Guerre asymétrique : sabotage, raids, opérations derrière les lignes.", 0x263238),
    ("Bibliothèque",  "📚 Bibliothèque",             "Documents, guides PDF, fiches techniques, manuels écrits.", 0x607D8B),
]


# ════════════════════════════════════════════════════════════════════
#  POSTS DE DÉMARRAGE — Forum intel (RENSEIGNEMENT)
# ════════════════════════════════════════════════════════════════════
INTEL_STARTER_POSTS = [
    ("Cartes",          "🗺️ Cartes et fronts",             "Captures de cartes annotées, hex contrôlés, situations stratégiques. Précise toujours le hex et l'heure de la capture.", 0x2196F3),
    ("Recon",           "🕵️ Rapports de reconnaissance",   "Observations terrain, repérages d'éclaireurs, points d'intérêt.", 0x4CAF50),
    ("Bases ennemies",  "🏰 Bases ennemies localisées",    "Forteresses adverses, FOB ennemis, dépôts repérés.", 0xE91E63),
    ("Convois ennemis", "🚛 Convois ennemis signalés",     "Mouvements de logi adverse, itinéraires, fréquences observées.", 0xFFB300),
    ("Mouvements",      "👣 Mouvements de troupes",        "Déplacements observés, concentrations, ruptures de front.", 0x9C27B0),
]


# ════════════════════════════════════════════════════════════════════
#  POSTS DE DÉMARRAGE — Forum archives (ARCHIVES)
# ════════════════════════════════════════════════════════════════════
ARCHIVES_STARTER_POSTS = [
    ("Guerres",    "🏆 Archives des guerres",    "Résultats des WARs passées, bilans, statistiques.", 0xFFD700),
    ("Opérations", "📜 Archives des opérations", "Débriefings anciens, post-mortems, leçons retenues.", 0x9C27B0),
    ("Vétérans",   "🎖️ Hall des vétérans",       "Membres historiques du régiment, ceux qui ont laissé leur marque.", 0xFFC107),
    ("Mémorial",   "🕯️ Mémorial",                "Hommages aux anciens combattants partis.", 0x607D8B),
]


# ════════════════════════════════════════════════════════════════════
#  POSTS DE DÉMARRAGE — Forum support (SUPPORT)
# ════════════════════════════════════════════════════════════════════
SUPPORT_STARTER_POSTS = [
    ("Aide technique", "🔧 Aide technique Foxhole", "Bugs en jeu, problèmes de performance, crashs, glitches. Décris ton problème, ta config, ce que tu as déjà essayé.", 0xFF5722),
    ("Aide Discord",   "💬 Aide Discord",           "Problèmes avec le serveur Discord, accès, notifications, permissions.", 0x2196F3),
    ("Contact staff",  "📞 Contact staff",          "Pour parler avec un membre de l'État-Major (sujet général). Pour un signalement, utilise le tag « Signalement ».", 0x4CAF50),
    ("Signalement",    "⚠️ Signalement",            "Signaler un comportement problématique, un conflit, une violation du règlement. **Ton post sera traité confidentiellement par les officiers.**", 0xE91E63),
]


# ════════════════════════════════════════════════════════════════════
#  MAP des seeds par forum
# ════════════════════════════════════════════════════════════════════
FORUM_STARTERS = {
    T("partages"):   PARTAGES_STARTER_POSTS,
    T("production"): PRODUCTION_STARTER_POSTS,
    T("academie"):   ACADEMIE_STARTER_POSTS,
    T("intel"):      INTEL_STARTER_POSTS,
    T("archives"):   ARCHIVES_STARTER_POSTS,
    T("support"):    SUPPORT_STARTER_POSTS,
}


class ToggleRoleButton(discord.ui.Button):
    """Bouton générique pour toggle (ajouter/retirer) un rôle."""
    def __init__(self, role_name: str, emoji: str, custom_id_prefix: str, style=discord.ButtonStyle.secondary):
        super().__init__(
            label=role_name,
            emoji=emoji,
            style=style,
            custom_id=f"{custom_id_prefix}:{role_name}",
        )
        self.role_name = role_name

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        if not isinstance(member, discord.Member):
            member = interaction.guild.get_member(member.id)
        role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if not role:
            await interaction.response.send_message(
                f"❌ Rôle « {self.role_name} » introuvable. Préviens un admin.",
                ephemeral=True,
            )
            return
        try:
            if role in member.roles:
                await member.remove_roles(role, reason="Self-remove")
                await interaction.response.send_message(
                    f"❌ Rôle **{self.role_name}** retiré.", ephemeral=True)
            else:
                await member.add_roles(role, reason="Self-assign")
                await interaction.response.send_message(
                    f"✅ Rôle **{self.role_name}** attribué.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Le bot n'a pas la permission (son rôle doit être plus haut).",
                ephemeral=True,
            )


class SpecialtyButton(discord.ui.Button):
    """Donne le rôle Recrue [Spécialité] (ou le retire)."""
    def __init__(self, specialty: str, emoji: str):
        super().__init__(
            label=specialty,
            emoji=emoji,
            style=discord.ButtonStyle.primary,
            custom_id=f"spec:{specialty}",
        )
        self.specialty = specialty

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        if not isinstance(member, discord.Member):
            member = interaction.guild.get_member(member.id)
        guild = interaction.guild

        # Les 3 grades possibles de cette spec
        grades = [f"Officier {self.specialty}", self.specialty, f"Recrue {self.specialty}"]
        existing = [r for r in member.roles if r.name in grades]

        try:
            if existing:
                await member.remove_roles(*existing, reason="Self-leave specialty")
                await interaction.response.send_message(
                    f"❌ Tu as quitté **{self.specialty}**.", ephemeral=True)
            else:
                recrue_role = discord.utils.get(guild.roles, name=f"Recrue {self.specialty}")
                if not recrue_role:
                    await interaction.response.send_message(
                        f"❌ Rôle « Recrue {self.specialty} » introuvable.", ephemeral=True)
                    return
                await member.add_roles(recrue_role, reason="Self-join specialty")
                await interaction.response.send_message(
                    f"✅ Bienvenue dans **{self.specialty}** ! Un officier te promouvra "
                    f"selon ton implication.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Le bot n'a pas la permission.", ephemeral=True)


class SpecialtyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for name, emoji, *_ in SPECIALTIES:
            self.add_item(SpecialtyButton(name, emoji))


class AvailabilityView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for name, emoji in AVAILABILITIES:
            self.add_item(ToggleRoleButton(name, emoji, "avail",
                                            discord.ButtonStyle.secondary))


class NotificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for name, emoji in NOTIFICATIONS:
            self.add_item(ToggleRoleButton(name, emoji, "notif",
                                            discord.ButtonStyle.success))


# ════════════════════════════════════════════════════════════════════
#  VUE DE CONFIRMATION /delete
# ════════════════════════════════════════════════════════════════════
class ConfirmDelete(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.confirmed = None

    @discord.ui.button(label="OUI, tout supprimer", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction, _b):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Seul l'auteur peut confirmer.", ephemeral=True)
            return
        self.confirmed = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction, _b):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Seul l'auteur peut annuler.", ephemeral=True)
            return
        self.confirmed = False
        await interaction.response.defer()
        self.stop()


# ════════════════════════════════════════════════════════════════════
#  HELPERS — Permissions
# ════════════════════════════════════════════════════════════════════
def _perms_from_dict(d: dict) -> discord.Permissions:
    p = discord.Permissions.none()
    for name, value in d.items():
        if hasattr(p, name):
            setattr(p, name, value)
    return p


def _build_overwrites(guild, roles_dict, allowed_role_names, mode=None):
    """Construit les permission overwrites.
    - allowed_role_names : liste de rôles autorisés à voir (None = public)
    - mode : "readonly" => refuse send_messages au public, autorise aux officiers
    """
    ow = {}
    if allowed_role_names:
        ow[guild.default_role] = discord.PermissionOverwrite(view_channel=False)
        for name in allowed_role_names:
            if name in roles_dict:
                ow[roles_dict[name]] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
    if mode == "readonly":
        if not allowed_role_names:
            ow[guild.default_role] = discord.PermissionOverwrite(send_messages=False)
        writers = OFFICIER_ROLES + HIGH_COMMAND + ["Modérateur"]
        for name in writers:
            if name in roles_dict:
                existing = ow.get(roles_dict[name], discord.PermissionOverwrite())
                existing.send_messages = True
                ow[roles_dict[name]] = existing
    return ow


# ════════════════════════════════════════════════════════════════════
#  CRÉATION — Rôles
# ════════════════════════════════════════════════════════════════════
async def _create_roles(guild: discord.Guild, log: list) -> dict:
    created = {}
    for name, color, perms_dict, is_sep, hoist in ROLES:
        try:
            role = await guild.create_role(
                name=name,
                color=discord.Color(color),
                permissions=_perms_from_dict(perms_dict),
                hoist=hoist,
                mentionable=not is_sep,
                reason="Auto via /create",
            )
            created[name] = role
            tag = "📌" if hoist else ("➖" if is_sep else "  ")
            log.append(f"{tag} {name}")
        except Exception as e:
            log.append(f"✗ Rôle '{name}' : {e}")
    return created


# ════════════════════════════════════════════════════════════════════
#  CRÉATION — Salons
# ════════════════════════════════════════════════════════════════════
async def _create_channels(guild: discord.Guild, roles: dict, log: list) -> dict:
    created = {}
    for cat_def in CATEGORIES:
        try:
            cat_ow = {}
            if cat_def["private_for"]:
                cat_ow = _build_overwrites(guild, roles, cat_def["private_for"])
            category = await guild.create_category(cat_def["name"], overwrites=cat_ow)
            log.append(f"📁 {cat_def['name']}")

            for ch_def in cat_def["channels"]:
                ch_type = ch_def[0]
                ch_name = ch_def[1]
                ch_private = ch_def[2] if len(ch_def) > 2 else None
                mode = ch_def[3] if len(ch_def) > 3 else None
                tags = ch_def[4] if len(ch_def) > 4 else None

                ch_ow = _build_overwrites(guild, roles, ch_private, mode)
                kwargs = {"category": category}
                if ch_ow:
                    kwargs["overwrites"] = ch_ow

                try:
                    if ch_type == "voice":
                        ch = await guild.create_voice_channel(ch_name, **kwargs)
                    elif ch_type == "forum":
                        if tags:
                            kwargs["available_tags"] = [discord.ForumTag(name=t) for t in tags]
                        ch = await guild.create_forum(ch_name, **kwargs)
                    else:
                        ch = await guild.create_text_channel(ch_name, **kwargs)
                    created[ch_name] = ch
                    log.append(f"   ✓ {ch_name}")
                except Exception as e:
                    log.append(f"   ✗ {ch_name} : {e}")
        except Exception as e:
            log.append(f"✗ Catégorie '{cat_def['name']}' : {e}")
    return created


# ════════════════════════════════════════════════════════════════════
#  MODE COMMUNAUTÉ
# ════════════════════════════════════════════════════════════════════
async def _ensure_community(guild: discord.Guild, log: list) -> tuple:
    if "COMMUNITY" in guild.features:
        log.append("✓ Mode Communauté déjà actif.")
        return None, None

    log.append("⚙️ Activation du mode Communauté...")
    temp_rules = await guild.create_text_channel("temp-rules-setup")
    temp_updates = await guild.create_text_channel("temp-updates-setup")
    try:
        await guild.edit(
            community=True,
            rules_channel=temp_rules,
            public_updates_channel=temp_updates,
            verification_level=discord.VerificationLevel.low,
            explicit_content_filter=discord.ContentFilter.all_members,
            default_notifications=discord.NotificationLevel.only_mentions,
        )
        log.append("✓ Mode Communauté activé.")
        return temp_rules, temp_updates
    except Exception as e:
        log.append(f"✗ Échec Communauté : {e}")
        for ch in (temp_rules, temp_updates):
            try: await ch.delete()
            except: pass
        return None, None


async def _finalize_server_config(guild, channels, temp_pair, log):
    real_rules    = channels.get(T("regles"))
    real_updates  = channels.get(T("annonces-serveur"))
    real_system   = channels.get(T("bienvenue"))
    try:
        kwargs = {}
        if real_rules:   kwargs["rules_channel"] = real_rules
        if real_updates: kwargs["public_updates_channel"] = real_updates
        if real_system:  kwargs["system_channel"] = real_system
        if kwargs:
            await guild.edit(**kwargs)
            log.append("✓ Salons système configurés.")
    except Exception as e:
        log.append(f"✗ Config salons système : {e}")

    if temp_pair:
        for ch in temp_pair:
            if ch:
                try: await ch.delete()
                except: pass
        log.append("✓ Salons temporaires supprimés.")


# ════════════════════════════════════════════════════════════════════
#  MESSAGES D'ACCUEIL + BOUTONS
# ════════════════════════════════════════════════════════════════════
async def _send_welcome_messages(channels, log):
    for ch_name, content in WELCOME_MESSAGES.items():
        ch = channels.get(ch_name)
        if not ch:
            continue
        try:
            embed = discord.Embed(
                title=content["title"],
                description=content["description"],
                color=content.get("color", 0x1976D2),
            )
            embed.set_footer(text="404e RI \"Les Disparus\" — Wardens")
            # Forums : un thread initial
            if isinstance(ch, discord.ForumChannel):
                await ch.create_thread(name=content["title"][:90], embed=embed)
            else:
                msg = await ch.send(embed=embed)
                try: await msg.pin()
                except: pass
            log.append(f"💬 Message envoyé dans {ch_name}")
        except Exception as e:
            log.append(f"✗ Message {ch_name} : {e}")

    # Boutons : tous dans choix-roles (3 panneaux dans le même salon)
    roles_ch = channels.get(T("choix-roles"))
    if roles_ch:
        try:
            await roles_ch.send(
                "**🎖️ Sélectionne ta ou tes spécialités :**\n"
                "*Tu peux en cocher plusieurs. Tu commences toujours en Recrue.*\n"
                "🪖 Infanterie · 🚗 Blindés · 💥 Artillerie · ⚓ Marine · 🚛 Logistique · "
                "🔨 Builder · ⚕️ Médic · 🎯 Sniper-Recon · 🚀 Anti-Char · 🗡️ Partisan",
                view=SpecialtyView(),
            )
            log.append("🎛️ Boutons spécialités installés.")
        except Exception as e:
            log.append(f"✗ Boutons spécialités : {e}")

        try:
            await roles_ch.send(
                "\n**🕒 Quand est-ce que tu joues d'habitude ?**\n"
                "*Coche toutes les cases qui s'appliquent. Sert aux officiers à planifier les ops.*",
                view=AvailabilityView(),
            )
            log.append("🎛️ Boutons disponibilités installés.")
        except Exception as e:
            log.append(f"✗ Boutons dispos : {e}")

        try:
            await roles_ch.send(
                "\n**🔔 Quels pings veux-tu recevoir ?**\n"
                "*Activé = tu seras notifié quand le rôle est ping. Aucun n'est obligatoire.*",
                view=NotificationView(),
            )
            log.append("🎛️ Boutons notifications installés.")
        except Exception as e:
            log.append(f"✗ Boutons notifs : {e}")


# ════════════════════════════════════════════════════════════════════
#  SEED — Posts initiaux dans le forum 『』partages
# ════════════════════════════════════════════════════════════════════
async def _seed_forums(channels, log):
    """Crée un post épinglé par tag dans chacun des forums seedés."""
    for forum_name, posts in FORUM_STARTERS.items():
        forum = channels.get(forum_name)
        if not forum or not isinstance(forum, discord.ForumChannel):
            log.append(f"⚠️ Forum '{forum_name}' introuvable, seed sauté.")
            continue
        tags_by_name = {tag.name: tag for tag in forum.available_tags}
        log.append(f"📌 Seed → {forum_name}")
        for tag_name, title, description, color in posts:
            tag = tags_by_name.get(tag_name)
            if not tag:
                log.append(f"   ⚠️ Tag '{tag_name}' absent.")
                continue
            try:
                embed = discord.Embed(title=title, description=description, color=color)
                embed.set_footer(text="404e RI — Post d'introduction")
                thread, _msg = await forum.create_thread(
                    name=title[:100],
                    embed=embed,
                    applied_tags=[tag],
                )
                try:
                    await thread.edit(pinned=True)
                except Exception:
                    pass
                log.append(f"   ✓ {tag_name}")
            except Exception as e:
                log.append(f"   ✗ {tag_name} : {e}")


# ════════════════════════════════════════════════════════════════════
#  ENVOI DE MESSAGES LONGS
# ════════════════════════════════════════════════════════════════════
async def _send_long(interaction, text, ephemeral=False):
    chunks = [text[i:i + 1900] for i in range(0, len(text), 1900)] or [""]
    try:
        await interaction.followup.send(chunks[0], ephemeral=ephemeral)
    except Exception:
        return
    for chunk in chunks[1:]:
        try: await interaction.channel.send(chunk)
        except: pass


# ════════════════════════════════════════════════════════════════════
#  HELPERS — Recherche de catégorie / front
# ════════════════════════════════════════════════════════════════════
def _denorm(name: str) -> str:
    """Convertit les gras maths en ASCII pour recherche."""
    out = ""
    for c in name:
        cp = ord(c)
        if 0x1D400 <= cp <= 0x1D419:    # bold A-Z
            out += chr(ord("a") + cp - 0x1D400)
        elif 0x1D41A <= cp <= 0x1D433:  # bold a-z
            out += chr(ord("a") + cp - 0x1D41A)
        elif 0x1D468 <= cp <= 0x1D481:  # bold italic A-Z
            out += chr(ord("a") + cp - 0x1D468)
        elif 0x1D482 <= cp <= 0x1D49B:  # bold italic a-z
            out += chr(ord("a") + cp - 0x1D482)
        elif "A" <= c <= "Z":
            out += c.lower()
        elif "a" <= c <= "z":
            out += c
        elif "0" <= c <= "9":
            out += c
        elif c == "-":
            out += "-"
    return out


def _find_category_by_keyword(guild: discord.Guild, keyword: str):
    keyword = keyword.upper()
    for cat in guild.categories:
        if keyword in _denorm(cat.name).upper():
            return cat
    return None


def _user_has_role(member: discord.Member, names) -> bool:
    if isinstance(names, str):
        names = [names]
    member_role_names = {r.name for r in member.roles}
    return any(n in member_role_names for n in names)


# ════════════════════════════════════════════════════════════════════
#  ÉVÉNEMENTS
# ════════════════════════════════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    # Vues persistantes
    bot.add_view(SpecialtyView())
    bot.add_view(AvailabilityView())
    bot.add_view(NotificationView())
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} commande(s) synchronisée(s).")
    except Exception as e:
        print(f"Erreur sync : {e}")


@bot.event
async def on_member_join(member: discord.Member):
    try:
        embed = discord.Embed(
            title=f"👋 Bienvenue au 404e RI \"Les Disparus\"",
            description=(
                "Tu viens de rejoindre le serveur — bienvenue, soldat.\n\n"
                "**Tes premières étapes :**\n"
                "📜 Lis le règlement et la charte militaire\n"
                "📋 Postule dans le forum **candidatures**\n"
                "🪖 Choisis ta spécialité (boutons dans **choix-specialite**)\n"
                "🕒 Indique tes disponibilités\n"
                "🔔 Active les notifications utiles\n\n"
                "Un Recruteur viendra te chercher. *Introuvables, indomptables.*"
            ),
            color=0x1976D2,
        )
        await member.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        pass


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    """Auto-attribue/retire les rôles séparateurs en fonction des rôles fonctionnels.

    Quand un membre reçoit "Recrue Infanterie", le bot lui ajoute aussi
    "】ıllıllı INFANTERIE ıllıllı【". Comme ce dernier est hoist, c'est lui
    qui définit le groupe du membre dans la sidebar des connectés.
    """
    if {r.id for r in before.roles} == {r.id for r in after.roles}:
        return  # pas de changement de rôle

    guild = after.guild
    after_names = {r.name for r in after.roles}

    # Quels séparateurs le membre DOIT avoir ?
    desired = set()
    for r_name in after_names:
        if r_name in ROLE_TO_SEP:
            desired.add(ROLE_TO_SEP[r_name])

    # Quels séparateurs le membre A ACTUELLEMENT ?
    current = after_names & ALL_SEP_NAMES

    to_add = desired - current
    to_remove = current - desired

    if to_add:
        roles = [discord.utils.get(guild.roles, name=n) for n in to_add]
        roles = [r for r in roles if r is not None]
        if roles:
            try: await after.add_roles(*roles, reason="Auto-attribution séparateur")
            except: pass

    if to_remove:
        roles = [discord.utils.get(guild.roles, name=n) for n in to_remove]
        roles = [r for r in roles if r is not None]
        if roles:
            try: await after.remove_roles(*roles, reason="Retrait séparateur orphelin")
            except: pass


# ════════════════════════════════════════════════════════════════════
#  COMMANDE /create
# ════════════════════════════════════════════════════════════════════
@bot.tree.command(name="create", description="Crée toute la structure du serveur (rôles + salons + paramètres).")
async def create_cmd(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrateurs seulement.", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)
    log = []
    guild = interaction.guild

    log.append("**=== ÉTAPE 1 — Mode Communauté ===**")
    temp_pair = await _ensure_community(guild, log)

    log.append("\n**=== ÉTAPE 2 — Rôles ===**")
    log.append("*(📌 = visible comme groupe dans la sidebar)*")
    roles = await _create_roles(guild, log)

    log.append("\n**=== ÉTAPE 3 — Salons ===**")
    channels = await _create_channels(guild, roles, log)

    log.append("\n**=== ÉTAPE 4 — Paramètres serveur ===**")
    await _finalize_server_config(guild, channels, temp_pair, log)

    log.append("\n**=== ÉTAPE 5 — Messages et boutons ===**")
    await _send_welcome_messages(channels, log)

    log.append("\n**=== ÉTAPE 6 — Seed des forums (partages, production, academie, intel, archives, support) ===**")
    await _seed_forums(channels, log)

    log.append(
        f"\n✅ **Terminé** — {len(roles)} rôles, {len(CATEGORIES)} catégories, {len(channels)} salons."
    )
    await _send_long(interaction, "\n".join(log))


# ════════════════════════════════════════════════════════════════════
#  COMMANDE /delete
# ════════════════════════════════════════════════════════════════════
@bot.tree.command(name="delete", description="⚠️ Supprime TOUS les salons et rôles du serveur.")
async def delete_cmd(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrateurs seulement.", ephemeral=True)
        return

    view = ConfirmDelete(interaction.user.id)
    await interaction.response.send_message(
        "⚠️ **ATTENTION** — supprime tous les salons et rôles du serveur.\n"
        "Action **irréversible**. Confirme pour continuer.",
        view=view, ephemeral=True,
    )
    await view.wait()
    if not view.confirmed:
        try: await interaction.followup.send("Annulé.", ephemeral=True)
        except: pass
        return

    guild = interaction.guild
    log = []
    bot_top_role = guild.me.top_role
    current_channel_id = interaction.channel_id

    for ch in [c for c in guild.channels if c.id != current_channel_id]:
        try:
            await ch.delete()
            log.append(f"✓ Salon : {ch.name}")
        except Exception as e:
            log.append(f"✗ Salon '{ch.name}' : {e}")

    for role in list(guild.roles):
        if role.is_default() or role.managed:
            continue
        if role >= bot_top_role:
            log.append(f"⊘ Rôle ignoré (≥ bot) : {role.name}")
            continue
        try:
            await role.delete()
            log.append(f"✓ Rôle : {role.name}")
        except Exception as e:
            log.append(f"✗ Rôle '{role.name}' : {e}")

    log.append("\n✅ **Suppression terminée.**")
    await _send_long(interaction, "\n".join(log), ephemeral=True)


# ════════════════════════════════════════════════════════════════════
#  COMMANDE /front
# ════════════════════════════════════════════════════════════════════
@bot.tree.command(name="front", description="Crée un salon de front (texte + vocal) — Officier Comms+.")
@app_commands.describe(nom="Nom du front (ex: Stema-Landing)")
async def front_cmd(interaction: discord.Interaction, nom: str):
    member = interaction.user
    if not _user_has_role(member, COMMS_TEAM) and not member.guild_permissions.administrator:
        await interaction.response.send_message("❌ Officier Comms ou Officier+ uniquement.", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)
    guild = interaction.guild

    fronts_cat = _find_category_by_keyword(guild, "OPS FRONTS")
    if not fronts_cat:
        await interaction.followup.send("❌ Catégorie OPS FRONTS introuvable. Lance /create d'abord.", ephemeral=True)
        return

    # Permissions Soldat+
    roles_dict = {r.name: r for r in guild.roles}
    ow = _build_overwrites(guild, roles_dict, LVL_SOLDAT)

    text_name = T(nom)
    voice_name = V(nom)
    msg_lines = [f"✅ Front **{nom}** ouvert."]

    try:
        text_ch = await guild.create_text_channel(text_name, category=fronts_cat, overwrites=ow)
        msg_lines.append(f"• Salon texte : {text_ch.mention}")
    except Exception as e:
        msg_lines.append(f"• Salon texte : ❌ {e}")

    try:
        voice_ch = await guild.create_voice_channel(voice_name, category=fronts_cat, overwrites=ow)
        msg_lines.append(f"• Salon vocal : {voice_ch.mention}")
    except Exception as e:
        msg_lines.append(f"• Salon vocal : ❌ {e}")

    await interaction.followup.send("\n".join(msg_lines))


# ════════════════════════════════════════════════════════════════════
#  COMMANDE /close_front
# ════════════════════════════════════════════════════════════════════
@bot.tree.command(name="close_front", description="Archive un salon de front — Officier Comms+.")
@app_commands.describe(nom="Nom du front à archiver (recherche par mot-clé)")
async def close_front_cmd(interaction: discord.Interaction, nom: str):
    member = interaction.user
    if not _user_has_role(member, COMMS_TEAM) and not member.guild_permissions.administrator:
        await interaction.response.send_message("❌ Officier Comms ou Officier+ uniquement.", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)
    guild = interaction.guild

    fronts_cat   = _find_category_by_keyword(guild, "OPS FRONTS")
    archives_cat = _find_category_by_keyword(guild, "ARCHIVES")
    if not archives_cat:
        await interaction.followup.send("❌ Catégorie ARCHIVES introuvable.", ephemeral=True)
        return

    search = _denorm(nom).lower()
    text_ch = None
    voice_ch = None

    if fronts_cat:
        for ch in fronts_cat.text_channels:
            d = _denorm(ch.name)
            if search in d and "comms" not in d:  # protège comms-reserve et comms-evacuation
                text_ch = ch
                break
        for ch in fronts_cat.voice_channels:
            d = _denorm(ch.name)
            if search in d and "qg" not in d:  # protège le vocal QG par défaut
                voice_ch = ch
                break

    if not text_ch and not voice_ch:
        await interaction.followup.send(f"❌ Aucun salon de front trouvé pour '{nom}'.", ephemeral=True)
        return

    msg_lines = [f"✅ Front **{nom}** archivé."]
    if text_ch:
        try:
            await text_ch.edit(category=archives_cat, sync_permissions=True)
            msg_lines.append(f"• Salon texte déplacé → ARCHIVES")
        except Exception as e:
            msg_lines.append(f"• Salon texte : ❌ {e}")
    if voice_ch:
        try:
            await voice_ch.delete(reason="Front fermé")
            msg_lines.append(f"• Salon vocal supprimé")
        except Exception as e:
            msg_lines.append(f"• Salon vocal : ❌ {e}")

    await interaction.followup.send("\n".join(msg_lines))


# ════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
