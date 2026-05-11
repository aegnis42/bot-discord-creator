# Bot Discord — 404e RI "Les Disparus" (Wardens)

Bot complet qui construit un serveur Foxhole prêt à l'emploi en une commande.

## 4 commandes

| Commande | Effet |
|---|---|
| `/create` | Construit toute la structure (rôles + salons + paramètres + boutons) |
| `/delete` | Supprime tout (avec confirmation) |
| `/front <nom>` | Crée un salon texte + vocal de front (Officier Comms+) |
| `/close_front <nom>` | Archive le salon texte vers ARCHIVES, supprime le vocal |

## Ce qui est créé par `/create`

- **~75 rôles** dont ~36 hoist (visibles comme groupes dans la sidebar)
- **19 catégories**, ~90 salons (~40 vocaux, ~17 forums)
- **Mode Communauté activé** automatiquement
- **Boutons persistants** pour choisir spécialité / dispos / notifications
- **Embeds d'accueil** épinglés (règlement, charte, FAQ, etc.)
- **DM de bienvenue** envoyé à chaque nouveau membre

---

## Installation

### 1. Bot Discord

1. https://discord.com/developers/applications → New Application
2. Onglet **Bot** : active **SERVER MEMBERS INTENT**, Reset Token, copie-le
3. Onglet **OAuth2 → URL Generator** :
   - Scopes : `bot`, `applications.commands`
   - Permissions : **Administrator**
4. Ouvre l'URL, autorise sur ton serveur

### 2. Placer le rôle du bot tout en haut

Paramètres du serveur → Rôles → glisse le rôle du bot **au-dessus** de tous les autres.
Indispensable, sinon il ne pourra pas gérer les rôles qu'il crée.

### 3. Déployer sur Railway

1. Pousse `bot.py` et `requirements.txt` sur un dépôt GitHub
2. Railway → New Project → Deploy from GitHub repo
3. Variables → ajoute `DISCORD_TOKEN`
4. Settings → Custom Start Command : `python bot.py`

---

## Utilisation

Une fois le bot connecté :
1. `/create` (~1-2 min, construit tout)
2. Tu installes les bots tiers de la checklist ci-dessous
3. Tu uploades les emojis customs et bannières

---

## ✅ Checklist bots tiers à installer après /create

Le bot Python ne fait pas tout. Voici ce qu'il manque, par priorité :

### 🔴 Indispensables

**1. Ticket Tool** — système de tickets pour candidatures et signalements
- Site : https://tickettool.xyz
- Configurer un panel dans le forum `『』candidatures` (mais le forum natif Discord marche aussi)
- Configurer un panel pour `『』signalements` et `『』contact-staff`
- Permissions : Recruteur pour candidatures, Modérateur + Officier+ pour signalements

**2. Carl-bot** ou **Dyno** — modération, anti-raid, vérification, reaction roles
- Carl-bot : https://carl.gg
- Dyno : https://dyno.gg
- À configurer :
  - **Automod** : anti-spam, anti-mention, anti-invite, anti-cap
  - **Anti-raid** : lockdown auto en cas d'invasion
  - **Verification** : reaction role dans `『』verification` qui donne accès au serveur
  - **Logs de modération** dans `『』logs-bot` (à créer si absent) ou `『』signalements`

### 🟠 Très utiles

**3. Sesh** — planification d'opérations
- Site : https://sesh.fyi
- Pour créer des événements avec RSVP, fuseaux horaires, rappels
- Utiliser dans `『』evenements`

**4. Foxhole War Stats Bot** — état de la guerre en direct
- Recherche "Foxhole" sur top.gg ou disboard.org
- Affiche le score, les hex contrôlés, les stockpiles
- Configurer dans `『』etat-de-la-guerre`

### 🟡 Utiles

**5. Statbot** — statistiques d'activité
- https://statbot.net
- Identifier les membres actifs vs inactifs

**6. Birthday Bot** ou **Carl-bot anniversaires**
- Pour gérer le salon `『』anniversaires`

**7. Logi Calculator / Artillery Bot**
- Bots Foxhole pour les calculs
- À configurer dans `『』calculatrices`

### ⚪ Optionnels

**8. MEE6** ou **Arcane** — niveaux/XP, gamification
**9. Tupperbox** — RP/personae si vous voulez du roleplay

---

## 🎨 À faire à la main

### Bannière et icône du serveur

Paramètres du serveur → Aperçu → uploader :
- **Icône** : logo du régiment (PNG 512x512 minimum)
- **Bannière** : 960x540 pixels minimum
- **Splash d'invitation** (si Boost niveau 1+)

### Emojis customs (à créer/uploader)

Paramètres du serveur → Émojis → uploader les fichiers PNG.

**Insignes de grade** (10 emojis) : un par grade militaire
**Ressources Foxhole** : `:bmat:`, `:rmat:`, `:emat:`, `:hemat:`, `:scrap:`, `:components:`, `:oil:`, `:salvage:`
**Véhicules** : `:tank:`, `:halftrack:`, `:navire:`, `:train:`
**Armes** : `:fusil:`, `:mortier:`, `:at:`, `:mg:`
**Statuts** : `:en_op:`, `:kia:`, `:mia:`, `:rtb:`, `:afk:`

Discord limite à 50 emojis sans boost. Priorise les ressources et les véhicules.

---

## 🛠️ Personnalisation

Tout est en haut de `bot.py` :

- **`SPECIALTIES`** (ligne ~72) — liste des 10 spécialités, emoji, couleurs des 3 grades
- **`AVAILABILITIES`** (ligne ~88) — créneaux de disponibilité auto-attribuables
- **`NOTIFICATIONS`** (ligne ~96) — types de notifications opt-in
- **`build_roles()`** (ligne ~118) — structure complète des rôles
- **`build_categories()`** (ligne ~190) — catégories et salons
- **`WELCOME_MESSAGES`** (ligne ~460) — embeds d'accueil

Pour modifier la structure : édite ces sections, push sur GitHub → Railway redéploie tout seul → `/delete` + `/create` sur Discord.

---

## ⚠️ Notes importantes

- **Mode Communauté requis** pour les forums : le bot l'active tout seul.
- **Le rôle du bot doit être tout en haut** dans la hiérarchie Discord (sinon `/delete` et `/create` n'arriveront pas à modifier les rôles qu'ils créent).
- **`/front` et `/close_front`** sont restreints à Officier Comms et Officier+ pour éviter les abus.
- Les **archives de fronts** s'accumulent dans la catégorie ARCHIVES — purge manuellement si ça pollue.

---

## 💡 Flow d'onboarding du nouveau membre

1. Arrivée → reçoit un **DM de bienvenue** automatique
2. Voit `『』bienvenue` (notification système Discord)
3. Lit `『』regles` + `『』charte-militaire`
4. Passe par `『』verification` (à gérer par Wick/Dyno)
5. Va dans `『』choix-specialite` → clique sur sa branche → reçoit **Recrue [Spec]**
6. Clique sur `『』choix-disponibilite` pour ses créneaux
7. Active des `『』choix-notifications`
8. Se présente dans le forum `『』presentations`
9. Postule dans le forum `『』candidatures` (avec template fourni)
10. Recruteur le contacte dans `』Entretien-1【` ou `』Entretien-2【` (vocaux)
11. Validation → un Officier transforme **Recrue X** en **X** (membre confirmé)
12. Plus tard, promotion en **Officier X** par un Officier+

---

## Coûts

- **Railway** : ~500h/mois gratuites (suffisant pour un serveur 24/7)
- **Discord Developer** : gratuit
- **Bots tiers** : tous ont un tier gratuit suffisant pour 100+ membres
