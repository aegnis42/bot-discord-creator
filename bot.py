"""
Bot Discord pour régiment Foxhole.

Commandes :
- /create : construit la totalité du serveur (rôles, salons, permissions, paramètres,
            messages d'accueil, boutons de choix de spécialité, mode Communauté).
- /delete : supprime tous les salons et rôles (avec confirmation).

Le bot gère aussi :
- Un DM de bienvenue aux nouveaux membres.
- Des boutons persistants dans le salon "Choix-de-Specialite" pour que les
  recrues s'auto-attribuent leur spécialité.
"""

import os
import discord
from discord import app_commands
from discord.ext import commands

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.members = True
intents.message_content = False
bot = commands.Bot(command_prefix="!", intents=intents)


# ============================================================
#  STYLE — convertit du texte en gras mathématique
# ============================================================
def _bold(s: str) -> str:
    out = ""
    for c in s:
        if "A" <= c <= "Z":
            out += chr(0x1D400 + ord(c) - ord("A"))
        elif "a" <= c <= "z":
            out += chr(0x1D41A + ord(c) - ord("a"))
        elif "0" <= c <= "9":
            out += chr(0x1D7CE + ord(c) - ord("0"))
        else:
            out += c
    return out


def _strip_accents(s: str) -> str:
    return s.translate(str.maketrans(
        "àâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ",
        "aaaeeeeiioouuucAAAEEEEIIOOUUUC"
    ))


def T(s: str) -> str:
    """Salon texte/forum : 『』𝐍𝐨𝐦"""
    return "『』" + _bold(_strip_accents(s))


def V(s: str) -> str:
    """Salon vocal : 】𝐍𝐨𝐦【"""
    return "】" + _bold(_strip_accents(s)) + "【"


def SEP(s: str) -> str:
    """Rôle séparateur décoratif dans la liste des rôles."""
    return "】ıllıllı " + s + " ıllıllı【"


# ============================================================
#  SPÉCIALITÉS — la base de la structure régimentaire
# ============================================================
# (nom, emoji, couleur_officier, couleur_sergent, couleur_soldat, couleur_recrue)
SPECIALTIES = [
    ("Infanterie",  "🪖", 0x7F8C8D, 0x95A5A6, 0xBDC3C7, 0xECF0F1),
    ("Blindés",     "🚗", 0x34495E, 0x546A7B, 0x778899, 0xB0C4DE),
    ("Artillerie",  "💥", 0x873600, 0xA04000, 0xD35400, 0xF5B041),
    ("Marine",      "⚓", 0x154360, 0x1F618D, 0x2980B9, 0x5DADE2),
    ("Logistique",  "🚛", 0xB7950B, 0xD4AC0D, 0xF1C40F, 0xF7DC6F),
    ("Médic",       "⚕️", 0x117A65, 0x16A085, 0x48C9B0, 0xA3E4D7),
    ("Partisan",    "🎯", 0x4A235A, 0x6C3483, 0x8E44AD, 0xBB8FCE),
]
RANKS = ["Officier", "Sergent", "Soldat", "Recrue"]

SPEC_NAMES = [s[0] for s in SPECIALTIES]


def specialty_role(spec: str, rank: str) -> str:
    return f"{rank} {spec}"


def all_ranks_of(spec: str) -> list:
    return [specialty_role(spec, r) for r in RANKS]


# Groupes de rôles utilisés pour les permissions
HIGH_COMMAND = ["Colonel", "Commandant", "Capitaine"]
ALL_OFFICERS = HIGH_COMMAND + [specialty_role(s, "Officier") for s in SPEC_NAMES]
ALL_SERGENTS_PLUS = ALL_OFFICERS + [specialty_role(s, "Sergent") for s in SPEC_NAMES]
RECRUITERS = ["Recruteur"] + HIGH_COMMAND
ALL_MEMBERS = []
for s in SPEC_NAMES:
    ALL_MEMBERS.extend(all_ranks_of(s))


# ============================================================
#  STRUCTURE DES RÔLES
# ============================================================
# Format : (nom, couleur, permissions, est_separateur, hoist_dans_sidebar)
# Le 1er créé finit en haut de la hiérarchie (les suivants le poussent).
def build_roles():
    r = []
    r.append((SEP("HAUT COMMANDEMENT"), 0x2B2D31, {}, True, False))
    r.append(("Colonel",    0xE91E63, {"administrator": True}, False, True))
    r.append(("Commandant", 0xD32F2F, {
        "manage_channels": True, "manage_roles": True,
        "kick_members": True, "ban_members": True,
        "manage_messages": True, "mute_members": True,
        "deafen_members": True, "move_members": True,
        "manage_nicknames": True, "manage_threads": True,
        "view_audit_log": True,
    }, False, True))
    r.append(("Capitaine",  0xC2185B, {
        "kick_members": True, "manage_messages": True,
        "mute_members": True, "move_members": True,
        "manage_threads": True, "manage_nicknames": True,
    }, False, True))

    r.append((SEP("FONCTIONS"), 0x2B2D31, {}, True, False))
    r.append(("Recruteur",  0x00BCD4, {"manage_messages": True, "manage_threads": True}, False, False))
    r.append(("Formateur",  0x4CAF50, {"manage_messages": True, "manage_threads": True}, False, False))
    r.append(("Diplomate",  0x3F51B5, {}, False, False))
    r.append(("Modérateur", 0xFF5722, {
        "manage_messages": True, "mute_members": True,
        "kick_members": True, "moderate_members": True,
    }, False, False))

    for name, _emoji, c_off, c_serg, c_sol, c_rec in SPECIALTIES:
        r.append((SEP(_strip_accents(name).upper()), 0x2B2D31, {}, True, False))
        r.append((specialty_role(name, "Officier"), c_off,  {}, False, True))
        r.append((specialty_role(name, "Sergent"),  c_serg, {}, False, True))
        r.append((specialty_role(name, "Soldat"),   c_sol,  {}, False, True))
        r.append((specialty_role(name, "Recrue"),   c_rec,  {}, False, True))

    r.append((SEP("VISITEURS"), 0x2B2D31, {}, True, False))
    r.append(("Allié",  0x90CAF9, {}, False, True))
    r.append(("Invité", 0xBDBDBD, {}, False, True))
    return r


ROLES = build_roles()


# ============================================================
#  STRUCTURE DES SALONS
# ============================================================
# Chaque catégorie : name, channels [(type, name, [private_for_optionnel])], private_for (None = publique)
def build_categories():
    cats = [
        {
            "name": "🚪 ENTREE",
            "private_for": None,
            "channels": [
                ("text",  T("Reglement"),         None, "readonly"),
                ("text",  T("Bienvenue"),         None, None),
                ("text",  T("Annonces"),          None, "readonly"),
                ("text",  T("Choix-de-Specialite"), None, "readonly"),
            ],
        },
        {
            "name": "📋 RECRUTEMENT",
            "private_for": None,
            "channels": [
                ("text",  T("Comment-Nous-Rejoindre"), None, "readonly"),
                ("forum", T("Candidatures"),           None, None),
                ("text",  T("Discussion-Recruteurs"),  RECRUITERS, None),
            ],
        },
        {
            "name": "🎓 FORMATION",
            "private_for": None,
            "channels": [
                ("forum", T("Tutos"),                None, None),
                ("forum", T("Questions-Reponses"),   None, None),
                ("forum", T("Entrainements"),        None, None),
                ("text",  T("Guides-Officiels"),     None, "readonly"),
            ],
        },
        {
            "name": "📢 INFORMATIONS",
            "private_for": None,
            "channels": [
                ("text", T("Actualites"),    None, "readonly"),
                ("text", T("Calendrier"),    None, "readonly"),
                ("text", T("News-Foxhole"),  None, "readonly"),
                ("text", T("Maj-Foxhole"),   None, "readonly"),
            ],
        },
        {
            "name": "💬 GENERAL",
            "private_for": None,
            "channels": [
                ("text", T("Discussion-Generale"), None, None),
                ("text", T("Memes"),               None, None),
                ("text", T("Medias"),              None, None),
                ("text", T("Hors-Sujet"),          None, None),
                ("text", T("Bot-Commandes"),       None, None),
                ("text", T("Musique"),             None, None),
            ],
        },
        {
            "name": "⚔️ OPERATIONS",
            "private_for": None,
            "channels": [
                ("text",  T("Ops-En-Cours"),       None, None),
                ("forum", T("Planification-Ops"),  None, None),
                ("forum", T("Debriefs"),           None, None),
                ("forum", T("Renseignements"),     None, None),
                ("text",  T("Cartes"),             None, None),
                ("text",  T("Screenshots"),        None, None),
            ],
        },
        {
            "name": "🚛 LOGISTIQUE",
            "private_for": None,
            "channels": [
                ("forum", T("Demandes-Logi"),  None, None),
                ("text",  T("Production"),     None, None),
                ("text",  T("Convois"),        None, None),
                ("forum", T("Stocks-Bases"),   None, None),
                ("text",  T("Records"),        None, None),
            ],
        },
    ]

    # Catégorie 🎖️ SALONS-SPECIALITES : 1 salon par spécialité, visible uniquement par celle-ci
    spec_text_channels = []
    for name, _e, *_ in SPECIALTIES:
        spec_text_channels.append(("text", T(name), all_ranks_of(name) + HIGH_COMMAND, None))
    cats.append({
        "name": "🎖️ SALONS-SPECIALITES",
        "private_for": None,
        "channels": spec_text_channels,
    })

    cats.extend([
        {
            "name": "🪖 SOUS-OFFICIERS",
            "private_for": ALL_SERGENTS_PLUS,
            "channels": [
                ("text",  T("Salon-Sergents"),    None, None),
                ("text",  T("Coordination-Op"),   None, None),
            ],
        },
        {
            "name": "⭐ OFFICIERS",
            "private_for": ALL_OFFICERS,
            "channels": [
                ("text",  T("Salon-Officiers"),       None, None),
                ("text",  T("Strategie"),             None, None),
                ("forum", T("Planification-EM"),      None, None),
                ("text",  T("Diplomatie"),            None, None),
                ("text",  T("Logs-Bot"),              None, None),
            ],
        },
        {
            "name": "🔊 VOCAUX GENERAUX",
            "private_for": None,
            "channels": [
                ("voice", V("Salle-Attente"), None, None),
                ("voice", V("General-1"),     None, None),
                ("voice", V("General-2"),     None, None),
                ("voice", V("Detente"),       None, None),
                ("voice", V("Musique"),       None, None),
                ("voice", V("AFK"),           None, None),
            ],
        },
        {
            "name": "⚔️ VOCAUX OPS",
            "private_for": None,
            "channels": [
                ("voice", V("QG"),          None, None),
                ("voice", V("Op-1"),        None, None),
                ("voice", V("Op-2"),        None, None),
                ("voice", V("Op-3"),        None, None),
                ("voice", V("Op-4"),        None, None),
                ("voice", V("Logistique"),  None, None),
                ("voice", V("Front"),       None, None),
            ],
        },
    ])

    # Vocaux par spécialité, chacun privé à sa spécialité
    spec_voice_channels = []
    for name, _e, *_ in SPECIALTIES:
        spec_voice_channels.append(("voice", V(name), all_ranks_of(name) + HIGH_COMMAND, None))
    cats.append({
        "name": "🎖️ VOCAUX SPECIALITES",
        "private_for": None,
        "channels": spec_voice_channels,
    })

    cats.append({
        "name": "⭐ VOCAUX COMMAND",
        "private_for": ALL_OFFICERS,
        "channels": [
            ("voice", V("Officiers"),  None, None),
            ("voice", V("Strategie"),  None, None),
        ],
    })

    return cats


CATEGORIES = build_categories()


# ============================================================
#  MESSAGES D'ACCUEIL
# ============================================================
WELCOME_MESSAGES = {
    T("Reglement"): {
        "title": "📜 Règlement du Régiment",
        "color": 0xE91E63,
        "description": (
            "**Conduite générale**\n"
            "1. Respect mutuel obligatoire — pas de toxicité, racisme, harcèlement.\n"
            "2. Pas de spam, pub, ou contenu NSFW.\n"
            "3. Utilise les bons salons. Les memes vont dans le salon dédié, pas dans les ops.\n"
            "4. Ton pseudo Discord doit correspondre à ton pseudo en jeu.\n\n"
            "**En jeu**\n"
            "5. Suis les ordres des officiers en opération.\n"
            "6. Communique sur Discord lors des ops, pas en in-game proximity.\n"
            "7. Pas de friendly fire intentionnel.\n"
            "8. Représente le régiment dignement, même envers les alliés.\n\n"
            "**Inactivité**\n"
            "9. Plus de 14 jours d'inactivité sans prévenir → rétrogradation possible.\n"
            "10. Préviens un officier si tu pars en pause.\n\n"
            "**Sanctions**\n"
            "• 1er avertissement : oral\n"
            "• 2e : retrait de spécialité\n"
            "• 3e : exclusion\n\n"
            "*En restant sur ce serveur, tu acceptes ces règles.*"
        ),
    },
    T("Bienvenue"): {
        "title": "👋 Bienvenue dans le Régiment",
        "color": 0x3498DB,
        "description": (
            "Tu viens d'arriver — voici par où commencer :\n\n"
            "📜 Lis le **règlement** dans le salon précédent.\n"
            "📋 Postule dans **Comment-Nous-Rejoindre** si tu veux nous rejoindre.\n"
            "🪖 Choisis ta **spécialité** dans le salon Choix-de-Specialite (boutons).\n"
            "🎓 Découvre les **tutoriels** dans la catégorie Formation.\n\n"
            "**Briser la glace :** présente-toi en quelques mots dans le forum dédié.\n\n"
            "Pour la voie : Front, Logistique, Marine, Médic, Blindés, Artillerie, Partisan — il y a une place pour toi."
        ),
    },
    T("Comment-Nous-Rejoindre"): {
        "title": "📋 Comment nous rejoindre",
        "color": 0x00BCD4,
        "description": (
            "**1. Lis le règlement** complet.\n"
            "**2. Ouvre une candidature** dans le forum Candidatures avec ces infos :\n\n"
            "```\n"
            "• Pseudo Foxhole :\n"
            "• Faction joué (Colonial / Warden) :\n"
            "• Heures de jeu / Steam :\n"
            "• Spécialité(s) souhaitée(s) :\n"
            "• Fuseau horaire :\n"
            "• Disponibilités hebdomadaires :\n"
            "• Pourquoi ce régiment ?\n"
            "```\n\n"
            "**3. Un recruteur te contactera** dans les 48 h.\n"
            "**4. Entretien rapide** en vocal pour valider ta candidature.\n"
            "**5. Tu deviens Recrue** dans ta spécialité — un Sergent t'encadrera.\n\n"
            "Bonne chance, soldat. 🪖"
        ),
    },
    T("Choix-de-Specialite"): {
        "title": "🎖️ Choisis ta spécialité",
        "color": 0xF1C40F,
        "description": (
            "Clique sur un bouton ci-dessous pour rejoindre une branche du régiment "
            "(ou en sortir, si tu cliques à nouveau).\n\n"
            "Tu peux avoir plusieurs spécialités. Tu commences toujours comme **Recrue** — "
            "un officier te promouvra selon ton implication.\n\n"
            "🪖 **Infanterie** — front, assaut, défense de tranchées\n"
            "🚗 **Blindés** — tankers, chasseurs de chars, escorte\n"
            "💥 **Artillerie** — barrages, contre-batterie, soutien\n"
            "⚓ **Marine** — navires, débarquements, ravitaillement maritime\n"
            "🚛 **Logistique** — convois, scoop, production, stocks\n"
            "⚕️ **Médic** — soins terrain, trauma center, évacuations\n"
            "🎯 **Partisan** — sabotage, raid, opérations spéciales"
        ),
    },
    T("Guides-Officiels"): {
        "title": "📚 Guides officiels Foxhole",
        "color": 0x4CAF50,
        "description": (
            "**Wiki officiel :** https://foxhole.wiki.gg\n"
            "**Subreddit :** https://reddit.com/r/foxholegame\n"
            "**Carte interactive :** https://foxholestats.com\n"
            "**Logistique-calculateur :** https://logiwaze.com\n\n"
            "Les guides spécifiques au régiment sont dans le forum **Tutos**."
        ),
    },
}


# ============================================================
#  VUE PERSISTANTE — Boutons de choix de spécialité
# ============================================================
class SpecialtyButton(discord.ui.Button):
    def __init__(self, specialty: str, emoji: str):
        super().__init__(
            label=specialty,
            emoji=emoji,
            style=discord.ButtonStyle.secondary,
            custom_id=f"specialty_role:{specialty}",
        )
        self.specialty = specialty

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild
        if not isinstance(member, discord.Member):
            member = guild.get_member(member.id)

        recrue_role_name = specialty_role(self.specialty, "Recrue")
        recrue_role = discord.utils.get(guild.roles, name=recrue_role_name)

        if not recrue_role:
            await interaction.response.send_message(
                f"❌ Le rôle « {recrue_role_name} » n'existe pas. Préviens un admin.",
                ephemeral=True,
            )
            return

        # L'utilisateur a-t-il déjà un grade dans cette spécialité ?
        ranks_of_spec_names = all_ranks_of(self.specialty)
        existing_in_spec = [r for r in member.roles if r.name in ranks_of_spec_names]

        try:
            if existing_in_spec:
                await member.remove_roles(*existing_in_spec, reason="Self-leave specialty")
                await interaction.response.send_message(
                    f"❌ Tu as quitté la branche **{self.specialty}**.",
                    ephemeral=True,
                )
            else:
                await member.add_roles(recrue_role, reason="Self-join specialty")
                await interaction.response.send_message(
                    f"✅ Bienvenue dans **{self.specialty}** ! Un officier te promouvra "
                    f"à partir de l'observation de ton activité.",
                    ephemeral=True,
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Le bot n'a pas les permissions nécessaires (son rôle doit être plus haut).",
                ephemeral=True,
            )


class SpecialtyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for name, emoji, *_ in SPECIALTIES:
            self.add_item(SpecialtyButton(name, emoji))


# ============================================================
#  VUE DE CONFIRMATION /delete
# ============================================================
class ConfirmDelete(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.confirmed = None

    @discord.ui.button(label="OUI, tout supprimer", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction, _button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Seul l'auteur peut confirmer.", ephemeral=True)
            return
        self.confirmed = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction, _button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Seul l'auteur peut annuler.", ephemeral=True)
            return
        self.confirmed = False
        await interaction.response.defer()
        self.stop()


# ============================================================
#  HELPERS — Permissions
# ============================================================
def _perms_from_dict(d: dict) -> discord.Permissions:
    p = discord.Permissions.none()
    for name, value in d.items():
        if hasattr(p, name):
            setattr(p, name, value)
    return p


def _build_overwrites(guild: discord.Guild, roles: dict, allowed_role_names, mode=None):
    """Construit les permission overwrites.
    - allowed_role_names : liste des rôles autorisés à voir le salon (None = public)
    - mode : "readonly" (refuse send_messages au public, autorise aux officiers)
    """
    ow = {}
    if allowed_role_names:
        ow[guild.default_role] = discord.PermissionOverwrite(view_channel=False)
        for name in allowed_role_names:
            if name in roles:
                ow[roles[name]] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
    if mode == "readonly":
        # Si le salon est public, refuse l'écriture sauf aux officiers et fonctions habilitées
        if not allowed_role_names:
            ow[guild.default_role] = discord.PermissionOverwrite(send_messages=False)
        writers = ALL_OFFICERS + ["Modérateur"]
        for name in writers:
            if name in roles:
                # Préserve un éventuel view_channel déjà mis ci-dessus
                existing = ow.get(roles[name], discord.PermissionOverwrite())
                existing.send_messages = True
                ow[roles[name]] = existing
    return ow


# ============================================================
#  CRÉATION — Rôles
# ============================================================
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
                reason="Auto-create via /create",
            )
            created[name] = role
            tag = "📌" if hoist else ("➖" if is_sep else "  ")
            log.append(f"{tag} {name}")
        except Exception as e:
            log.append(f"✗ Rôle '{name}' : {e}")
    return created


# ============================================================
#  CRÉATION — Salons
# ============================================================
async def _create_channels(guild: discord.Guild, roles: dict, log: list) -> dict:
    """Crée toutes les catégories et leurs salons. Retourne un dict {nom: Channel}."""
    created_channels = {}
    for cat_def in CATEGORIES:
        try:
            cat_ow = {}
            if cat_def["private_for"]:
                cat_ow = _build_overwrites(guild, roles, cat_def["private_for"])
            category = await guild.create_category(cat_def["name"], overwrites=cat_ow)
            log.append(f"📁 {cat_def['name']}")

            for ch_def in cat_def["channels"]:
                ch_type, ch_name, ch_private, mode = ch_def
                ch_ow = _build_overwrites(guild, roles, ch_private, mode)
                kwargs = {"category": category}
                if ch_ow:
                    kwargs["overwrites"] = ch_ow

                try:
                    if ch_type == "voice":
                        ch = await guild.create_voice_channel(ch_name, **kwargs)
                    elif ch_type == "forum":
                        ch = await guild.create_forum(ch_name, **kwargs)
                    else:
                        ch = await guild.create_text_channel(ch_name, **kwargs)
                    created_channels[ch_name] = ch
                    log.append(f"   ✓ {ch_name}")
                except Exception as e:
                    log.append(f"   ✗ {ch_name} : {e}")
        except Exception as e:
            log.append(f"✗ Catégorie '{cat_def['name']}' : {e}")
    return created_channels


# ============================================================
#  CONFIGURATION — Mode Communauté
# ============================================================
async def _ensure_community(guild: discord.Guild, log: list) -> tuple:
    """Active le mode Communauté si nécessaire. Crée des salons temporaires si besoin.
    Retourne (temp_rules, temp_updates) à supprimer après reconfiguration."""
    if "COMMUNITY" in guild.features:
        log.append("✓ Mode Communauté déjà actif.")
        return None, None

    log.append("⚙️ Activation du mode Communauté (forums)...")
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
        log.append(f"✗ Échec activation Communauté : {e}")
        for ch in (temp_rules, temp_updates):
            try:
                await ch.delete()
            except Exception:
                pass
        return None, None


async def _finalize_server_config(guild: discord.Guild, channels: dict, temp_pair, log: list):
    """Définit les rules/updates/system channels et supprime les temps."""
    real_rules = channels.get(T("Reglement"))
    real_updates = channels.get(T("Actualites"))
    real_system = channels.get(T("Bienvenue"))

    try:
        kwargs = {}
        if real_rules:
            kwargs["rules_channel"] = real_rules
        if real_updates:
            kwargs["public_updates_channel"] = real_updates
        if real_system:
            kwargs["system_channel"] = real_system
        if kwargs:
            await guild.edit(**kwargs)
            log.append("✓ Salons système configurés (règlement, actualités, accueil).")
    except Exception as e:
        log.append(f"✗ Config salons système : {e}")

    if temp_pair:
        for ch in temp_pair:
            if ch:
                try:
                    await ch.delete()
                except Exception:
                    pass
        log.append("✓ Salons temporaires supprimés.")


# ============================================================
#  MESSAGES — Envoi des accueils + boutons
# ============================================================
async def _send_welcome_messages(channels: dict, log: list):
    for ch_name, content in WELCOME_MESSAGES.items():
        ch = channels.get(ch_name)
        if not ch:
            continue
        try:
            embed = discord.Embed(
                title=content["title"],
                description=content["description"],
                color=content.get("color", 0x3498DB),
            )
            embed.set_footer(text="Régiment Foxhole")
            msg = await ch.send(embed=embed)
            try:
                await msg.pin()
            except Exception:
                pass
            log.append(f"💬 Message envoyé dans {ch_name}")
        except Exception as e:
            log.append(f"✗ Message {ch_name} : {e}")

    # Boutons de spécialité dans Choix-de-Specialite
    choix_ch = channels.get(T("Choix-de-Specialite"))
    if choix_ch:
        try:
            view = SpecialtyView()
            await choix_ch.send(
                "**🎖️ Sélectionne ta ou tes spécialités :**\n"
                "*Clique à nouveau sur un bouton pour quitter cette branche.*",
                view=view,
            )
            log.append(f"🎛️ Boutons de spécialité installés.")
        except Exception as e:
            log.append(f"✗ Boutons spécialité : {e}")


# ============================================================
#  ENVOI DE MESSAGES LONGS
# ============================================================
async def _send_long(interaction: discord.Interaction, text: str, ephemeral: bool = False):
    chunks = [text[i:i + 1900] for i in range(0, len(text), 1900)] or [""]
    try:
        await interaction.followup.send(chunks[0], ephemeral=ephemeral)
    except Exception:
        return
    for chunk in chunks[1:]:
        try:
            await interaction.channel.send(chunk)
        except Exception:
            pass


# ============================================================
#  ÉVÉNEMENTS
# ============================================================
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    # Enregistre la vue persistante (pour que les boutons survivent aux redémarrages)
    bot.add_view(SpecialtyView())
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} commande(s) synchronisée(s).")
    except Exception as e:
        print(f"Erreur sync : {e}")


@bot.event
async def on_member_join(member: discord.Member):
    """DM de bienvenue (silencieux si l'utilisateur a les DM fermés)."""
    try:
        embed = discord.Embed(
            title=f"👋 Bienvenue sur {member.guild.name}",
            description=(
                "Tu viens de rejoindre le serveur !\n\n"
                "**Étapes recommandées :**\n"
                "📜 Lis le règlement\n"
                "📋 Postule dans le salon Comment-Nous-Rejoindre\n"
                "🪖 Choisis ta spécialité (boutons dans Choix-de-Specialite)\n"
                "🎓 Visite la catégorie Formation\n\n"
                "Tu seras encadré dès qu'un officier te validera. À bientôt en jeu !"
            ),
            color=0x3498DB,
        )
        await member.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        pass  # DMs fermés, on ignore


# ============================================================
#  COMMANDE /create
# ============================================================
@bot.tree.command(name="create", description="Construit le serveur Foxhole complet (rôles, salons, paramètres).")
async def create_cmd(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrateurs seulement.", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)
    log = []
    guild = interaction.guild

    log.append("**=== ÉTAPE 1 — Mode Communauté ===**")
    temp_pair = await _ensure_community(guild, log)

    log.append("\n**=== ÉTAPE 2 — Création des rôles ===**")
    log.append("*(📌 = visible comme groupe dans la sidebar)*")
    roles = await _create_roles(guild, log)

    log.append("\n**=== ÉTAPE 3 — Création des salons ===**")
    channels = await _create_channels(guild, roles, log)

    log.append("\n**=== ÉTAPE 4 — Paramètres du serveur ===**")
    await _finalize_server_config(guild, channels, temp_pair, log)

    log.append("\n**=== ÉTAPE 5 — Messages et boutons ===**")
    await _send_welcome_messages(channels, log)

    log.append(
        f"\n✅ **Terminé** — {len(roles)} rôles, {len(CATEGORIES)} catégories, "
        f"{len(channels)} salons."
    )
    await _send_long(interaction, "\n".join(log))


# ============================================================
#  COMMANDE /delete
# ============================================================
@bot.tree.command(name="delete", description="⚠️ Supprime TOUS les salons et rôles du serveur.")
async def delete_cmd(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrateurs seulement.", ephemeral=True)
        return

    view = ConfirmDelete(interaction.user.id)
    await interaction.response.send_message(
        "⚠️ **ATTENTION** — supprime tous les salons et rôles du serveur.\n"
        "Action **irréversible**. Confirme pour continuer.",
        view=view,
        ephemeral=True,
    )
    await view.wait()
    if not view.confirmed:
        try:
            await interaction.followup.send("Annulé.", ephemeral=True)
        except Exception:
            pass
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


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
