# Bot Discord — Régiment Foxhole

Bot complet pour générer un serveur Discord prêt à l'emploi pour un régiment Foxhole.

## Deux commandes

- **`/create`** — construit tout le serveur en une fois (rôles, salons, permissions, mode Communauté, messages d'accueil, boutons de choix de spécialité).
- **`/delete`** — supprime tous les salons et rôles (avec un bouton de confirmation rouge).

---

## Ce qui est créé par `/create`

### 🪖 Rôles (47 au total)

**Haut Commandement** (au-dessus des officiers, groupe séparé en haut de la sidebar) :
- Colonel (Administrateur)
- Commandant (gère salons, rôles, kick, ban, etc.)
- Capitaine (modération, gestion threads)

**Fonctions transversales** (non affichées séparément) :
- Recruteur, Formateur, Diplomate, Modérateur

**Pour chaque spécialité — 7 spécialités × 4 grades** :
- 🪖 Infanterie : Officier / Sergent / Soldat / Recrue
- 🚗 Blindés : Officier / Sergent / Soldat / Recrue
- 💥 Artillerie : Officier / Sergent / Soldat / Recrue
- ⚓ Marine : Officier / Sergent / Soldat / Recrue
- 🚛 Logistique : Officier / Sergent / Soldat / Recrue
- ⚕️ Médic : Officier / Sergent / Soldat / Recrue
- 🎯 Partisan : Officier / Sergent / Soldat / Recrue

**Visiteurs** : Allié, Invité

Chaque spécialité a sa propre **palette de couleur dégradée** (Officier sombre → Recrue clair).
Les séparateurs `】ıllıllı NOM ıllıllı【` organisent visuellement la liste des rôles côté admin.

### 📁 Catégories et salons (14 catégories, ~60 salons)

| Catégorie | Type | Accès |
|---|---|---|
| 🚪 ENTREE | Règlement (lecture seule), Bienvenue, Annonces, Choix de spécialité | Public |
| 📋 RECRUTEMENT | Info publique, forum Candidatures, salon recruteurs | Mixte |
| 🎓 FORMATION | Forums Tutos / Questions-Réponses / Entraînements, Guides | Public |
| 📢 INFORMATIONS | Actualités, Calendrier, News Foxhole, MAJ | Public (lecture) |
| 💬 GENERAL | Discussion, Memes, Médias, Hors-Sujet, Bot, Musique | Public |
| ⚔️ OPERATIONS | Ops en cours, forums Planif/Debriefs/Renseignements, Cartes, Screenshots | Public |
| 🚛 LOGISTIQUE | Forum Demandes, Production, Convois, forum Stocks, Records | Public |
| 🎖️ SALONS-SPECIALITES | 1 salon par spécialité, **privé à cette spécialité** | Spécialités |
| 🪖 SOUS-OFFICIERS | Salon Sergents, Coordination | Sergent+ |
| ⭐ OFFICIERS | Salon Officiers, Stratégie, forum Planif EM, Diplomatie, Logs | Officiers |
| 🔊 VOCAUX GENERAUX | Attente, General 1/2, Détente, Musique, AFK | Public |
| ⚔️ VOCAUX OPS | QG, Op 1-4, Logistique, Front | Public |
| 🎖️ VOCAUX SPECIALITES | 1 vocal par spécialité | Spécialités |
| ⭐ VOCAUX COMMAND | Officiers, Stratégie | Officiers |

### 🤖 Automatisations supplémentaires

- **Mode Communauté activé** automatiquement (requis pour les forums)
- **Salon des règles** et **Actualités** configurés au niveau serveur
- **Salon système** (notifs de bienvenue Discord) pointé sur Bienvenue
- **5 messages d'accueil** envoyés et épinglés dans les bons salons
- **Boutons de choix de spécialité** persistants dans le salon dédié — les nouveaux cliquent eux-mêmes pour obtenir le rôle Recrue de leur branche
- **DM de bienvenue** envoyé aux nouveaux membres (si leurs DM sont ouverts)

---

## Installation (1ʳᵉ fois)

### 1. Créer le bot Discord

1. https://discord.com/developers/applications → **New Application**
2. Onglet **Bot** :
   - Active **SERVER MEMBERS INTENT**
   - **Reset Token** → copie le token (garde-le secret)
3. Onglet **OAuth2 → URL Generator** :
   - Scopes : `bot`, `applications.commands`
   - Permissions : **Administrator**
4. Ouvre l'URL générée, sélectionne ton serveur, autorise.

### 2. Placer le rôle du bot tout en haut

Paramètres du serveur → **Rôles** → glisse le rôle du bot **au-dessus** de tous les rôles qu'il va créer (juste en dessous du rôle "Server Booster" s'il existe).
Sans ça, le bot ne pourra pas gérer les rôles qu'il crée.

### 3. Déployer sur Railway (gratuit)

1. https://railway.app → connexion via GitHub
2. Push `bot.py` + `requirements.txt` sur un dépôt GitHub
3. Railway → **New Project** → **Deploy from GitHub repo**
4. Onglet **Variables** → ajoute :
   - `DISCORD_TOKEN` = ton token Discord
5. Onglet **Settings → Deploy** → Custom Start Command : `python bot.py`
6. Vérifie les logs : tu dois voir `Connecté en tant que ...`

---

## Utilisation

### Tout créer
Tape `/create` dans n'importe quel salon de ton serveur. Le bot prend ~1 minute pour tout construire et affiche un récap.

### Tout supprimer
Tape `/delete`. Un bouton rouge "OUI, tout supprimer" apparaît. Confirme pour tout wiper.

Tu peux enchaîner `/delete` → `/create` pour repartir à zéro proprement.

---

## Comment les nouveaux membres rejoignent

1. Ils arrivent sur le serveur → reçoivent un DM de bienvenue automatique
2. Ils lisent le règlement, voient `Bienvenue` dans le salon système
3. Ils vont dans `Choix-de-Specialite` → cliquent sur le bouton de leur spécialité (Infanterie, Blindés, etc.) → reçoivent automatiquement le rôle Recrue correspondant
4. Ils postulent dans le forum `Candidatures` (modèle de candidature dans `Comment-Nous-Rejoindre`)
5. Un Recruteur les valide ; un Sergent les promeut quand ils progressent

---

## Notes importantes

- **Les forums nécessitent le mode Communauté** — le bot l'active automatiquement, mais ça nécessite que ton serveur ait un niveau de vérification minimal et un filtre de contenu activé (le bot les configure aussi).
- **Le rôle du bot doit être plus haut que les rôles qu'il manipule.** S'il est en bas de la liste des rôles, `/create` créera les rôles mais ne pourra pas les modifier ni les attribuer via les boutons.
- **`/delete` ignore les rôles plus hauts que le bot** et les rôles "managed" (rôles de bots, boosts Nitro).
- Le salon où tu lances `/delete` est gardé pour afficher le résultat — supprime-le manuellement après si tu veux un nettoyage total.
- Le **DM de bienvenue** échoue silencieusement si l'utilisateur a fermé ses DM (Discord normal).

---

## Personnaliser la structure

Tout est en haut du fichier `bot.py` :

- **`SPECIALTIES`** — la liste des spécialités, leur emoji, leurs 4 couleurs (officier → recrue). Ajoute, retire, change.
- **`RANKS`** — les grades à l'intérieur d'une spécialité. Par défaut `["Officier", "Sergent", "Soldat", "Recrue"]`. Tu peux changer (ex: `["Capitaine", "Lieutenant", "Sergent", "Caporal", "Soldat", "Recrue"]`).
- **`HIGH_COMMAND`** — les rôles au-dessus des officiers.
- **`CATEGORIES`** dans `build_categories()` — la structure complète des salons.
- **`WELCOME_MESSAGES`** — les embeds envoyés dans certains salons.

Après modification, push sur GitHub → Railway redéploie tout seul. Puis `/delete` + `/create` pour appliquer.

---

## Coûts

- **Railway** : ~500h/mois gratuites (suffisant pour faire tourner le bot en continu)
- **Discord Developer** : gratuit
- **Aucune API payante** (pas d'OpenAI/Anthropic) — c'est 100 % gratuit à utiliser.
