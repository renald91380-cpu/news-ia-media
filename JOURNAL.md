# Journal News IA

Suivi du projet : décisions, réglages, chiffres et prochaines étapes.
À lire en premier avant toute modification des scripts ou des tâches programmées.
Dernière mise à jour : lundi 9 novembre 2026 (soir).

---

## 1. Vue d'ensemble

| Élément | Valeur |
| --- | --- |
| Comptes | TikTok @dimahako et Threads @renald91150 en automatique ; Instagram @renald91150 seulement à la main |
| Outil de publication | Metricool (marque 7238534), 20 publications par mois au maximum |
| Hébergement des fichiers | ce dépôt, liens `raw.githubusercontent.com/.../main/<dossier>/reel.mp4` |
| Format | vidéo courte 9:16 d'environ 15 s, la même sur TikTok et Threads |
| Heure | 10h00 (meilleur créneau Instagram selon Metricool, 18h en second) |

### Calendrier automatique

| Jour de publication | Contenu | Tâche programmée (préparée la veille à 19h57) |
| --- | --- | --- |
| Lundi, mardi, jeudi, vendredi | News IA en français, légende FR + EN | « News IA (préparée la veille, publication auto) » |
| Mercredi | Édition Indonésie, puis édition Chine, puis rien | « News IA – Éditions Indonésie / Chine du mercredi » |

Quota de novembre : 17 News IA + Spécial création du 4 + Indonésie du 11 + Chine du 18 = 20 sur 20. Rien le 25.

Les posts publiés à la main dans l'app Instagram (carrousels, stories) ne comptent pas dans le quota Metricool.

---

## 2. Outils du dépôt

### `outils/carrousel.py`
Produit les images 1080 x 1350 (carrousel de secours) et les étapes 1080 x 1920 de la vidéo (`carrousel/reel/` + `manifest.json`).

- Seule partie à modifier par copie : bloc « CONTENU DU JOUR » (DATE, ACCROCHE, ACCROCHE_EN, NEWS, LANG).
- `LANG` : `"fr"`, `"id"` (Indonésie) ou `"zh"` (chinois simplifié). Les textes d'interface sont traduits ; en chinois, police Noto Sans CJK SC et coupure des lignes caractère par caractère, sans couper les mots latins.
- Les chiffres des titres et de l'accroche s'affichent dans la couleur d'accent.
- Couleurs : `ACCENTS[n]`, lundi = 0 … dimanche = 6. Indonésie = 1 (vert), Chine = 3 (rouge/rose).

### `outils/reel.py`
`python3 outils/reel.py carrousel reel.mp4 [--court]`

- `--court` (format actuel) : accroche, puis titre + 1re phrase de chaque actu, puis récap. Environ 12 à 16 s.
- Sans option : version longue avec les 3 phrases (environ 48 s).
- Effets : ouverture « punch » avec impact sonore, texte qui glisse vers le haut, transition « push » avec whoosh, barre de progression segmentée, musique originale 118 BPM générée par le script (aucun droit à gérer).

### `manuel/`
Contenus publiés à la main hors Metricool. Chaque dossier contient les images, la légende et le script qui les a générés.

---

## 3. Historique des décisions

| Date | Décision | Raison |
| --- | --- | --- |
| 17 oct. | Légende et titre TikTok bilingues FR + EN | Demande de Renald |
| 19 oct. | Ligne éditoriale : IA générale + IA pour la création | « Pas que post-prod » |
| 19 oct. | Tenter un son tendance Instagram à chaque post | Demande de Renald |
| 22 oct. | Reel classique, jamais de Reel d'essai (TRIAL_REEL) | Refusé par Instagram : pas assez d'abonnés |
| 2 nov. | 3 phrases par actu, vidéo de 40 à 50 s | Contenu plus explicatif |
| 4 nov. | **Vidéo courte (~15 s) sur les 3 réseaux** | Instagram : 70 à 85 % des gens partaient avant 3 s |
| 4 nov. | Une seule vidéo pour les 3 réseaux, pas de version séparée pour Instagram | Une 2e publication par jour dépasserait le quota de 20 |
| 4 nov. | Spéciales création du mercredi remplacées par une édition Indonésie et une édition Chine par mois | Demande de Renald |
| 9 nov. | Ajout d'un carrousel manuel par semaine, publié dans l'app | Toucher les abonnés sans consommer le quota |
| 9 nov. | **Instagram retiré des publications automatiques** (tâches + post du 10 nov.) | 2 à 62 vues par Reel, aucune progression |

---

## 4. Chiffres de référence

### Avant le changement de format (Reels de 40 à 50 s)

| Réseau | Vues par vidéo | Rétention |
| --- | --- | --- |
| Instagram | 5 à 62, une trentaine en moyenne | 2 à 5 s regardées, 12 à 30 % restent plus de 3 s |
| TikTok | 170 à 770, environ 250 en moyenne | non fournie par Metricool |

### Après (premiers points, à suivre)

| Date | Instagram | TikTok |
| --- | --- | --- |
| 4 nov. (dernière longue) | 11 vues | 238 vues |
| 6 nov. (1re courte) | 3 vues, 33 % restent plus de 3 s | 258 vues |
| 9 nov. | à relever | à relever |

À refaire vers le 20 novembre, avec au moins 8 vidéos courtes, avant de conclure.

### Analyse du 9 novembre : ce qui fait des vues

**TikTok (le moteur du compte)** : socle d'environ 230 à 270 vues quel que soit le contenu.

| Vues | Date | Format | Sujet |
| --- | --- | --- | --- |
| 769 | 16 oct. | vidéo 16 s | « Ton perso IA reste le même d'un plan à l'autre » (problème de créateur résolu) |
| 766 | 13 oct. | diaporama photo | 3 news IA générales (jeu vidéo en 30 min) |
| 743 | 13 oct. | diaporama photo | Édition Indonésie |
| 418 | 27 oct. | vidéo 26 s | Siri parle enfin français |
| 303 | 6 oct. | diaporama photo | IA en visio prise pour un humain |
| 229 à 238 | 3 et 4 nov. | vidéo 47 à 54 s | les plus faibles : formats longs |

Likes : 0 à 5 par vidéo, commentaires : 0. Les gens regardent mais n'interagissent pas.

**Threads** : les images et carrousels font 94 à 176 vues (4, 6, 13 et 14 oct.), les vidéos 5 à 70, sauf Mistral (148, angle français).

**Instagram** : Reels 2 à 62 vues, carrousels 19 à 57 vues (portée 7 à 17 personnes). Meilleur Reel : l'agence IA open source avec lien GitHub (62), une ressource utile plutôt qu'un résumé d'actus.

**Constats** : le diaporama photo et les vidéos courtes battent les vidéos longues sur TikTok ; un sujet unique et concret bat le « 3 news » ; l'angle français et l'Indonésie marchent ; Threads préfère l'image à la vidéo.

---

## 5. Problèmes connus

- **Son tendance Instagram refusé (erreur 403)** à chaque tentative depuis le 21 octobre. Cause : le compte Instagram n'est pas un compte professionnel relié à une Page Facebook. La publication part sans son tendance, avec la musique d'origine.
- **Pas de publication le jeudi 5 novembre.** La tâche du mercredi 4 au soir n'a rien programmé. Cause à vérifier dans le compte rendu de cette exécution.
- Envoi Git (`git push`) parfois lent depuis l'environnement cloud : vérifier avec `git fetch` que le commit est bien arrivé avant de réessayer.

---

## 6. Semaine du 9 novembre

```
LUN  10h00  REEL       NEWS (auto)     Claude lit tes comptes bancaires
MAR  10h00  REEL       NEWS (auto)
MER  10h00  REEL       NEWS (auto)     Édition Indonésie
JEU  10h00  REEL       NEWS (auto)
     18h00  CARROUSEL  ASTUCE (main)   5 IA pour monter plus vite
VEN  10h00  REEL       NEWS (auto)
SAM  11h00  STORY      OPINION         sondage : « Tu laisserais une IA lire tes comptes ? »
DIM  -

Chaque jour : 20 min de commentaires avant 10h, partage du Reel en story avec une question.
```

### Carrousel du jeudi 12 novembre
Fichiers dans `manuel/2026-11-12-carrousel-montage/` (9 slides, légende, texte alternatif).

1. Couverture : 5 IA pour monter plus vite
2. Pourquoi : trier, monter, sonoriser, nettoyer
3. Monter : Edits, gratuit sur Mac
4. Trier : Resolve 21.1.2 trouve le bon plan
5. Nettoyer : Topaz Wonder 4
6. Sonoriser : ElevenLabs SFX v3
7. Musique : Suno depuis ton chatbot
8. Récap
9. Appel : enregistre ce post

Faits repris des News IA déjà publiées (2, 4, 6 et 9 novembre).

### Interactions quotidiennes (20 min)
Liste de 10 comptes à constituer : 5 grands comptes IA ou montage, 3 comptes de même taille, 2 comptes de ton public. En attente des comptes que Renald suit déjà.

---

## 7. À faire

- [ ] Décider : alterner vidéo courte et diaporama photo sur TikTok + Threads (les diaporamas ont fait 740 à 770 vues).
- [ ] Renald : passer Instagram en compte professionnel relié à une Page Facebook (débloque les sons tendance), si Instagram doit repartir un jour.
- [ ] Renald : publier le carrousel jeudi 12 novembre à 18h et répondre aux commentaires dans l'heure.
- [ ] Renald : envoyer la liste des comptes suivis pour la routine de commentaires.
- [ ] Vérifier pourquoi aucune publication n'est partie le 5 novembre.
- [ ] Vers le 20 novembre : comparer les vues Instagram des vidéos courtes à la référence ci-dessus.
- [ ] Contrôler les éditions Indonésie (11 nov.) et Chine (18 nov.) : rendu des caractères, légende, quota.
