# Diffusion sur X des posts sur les mobilisations des 17 et 24 octobre 2026

Chiffres sur la circulation, sur X, des posts consacrés aux journées de mobilisation des samedis 17 et 24 octobre 2026 en France, comparée aux autres posts des mêmes comptes. Toutes les données et tous les scripts sont dans ce dépôt. Chaque tableau se recalcule avec `python methode/analyse.py`.

## Comment c'est mesuré

- **Comptes suivis** : 83 comptes publics (médias nationaux et régionaux, agences, journalistes de terrain, médias militants, personnalités politiques), liste dans `methode/comptes.txt`. 71 ont publié les deux jours.
- **Collecte** : tous les posts de ces comptes, de 8 h à minuit (heure de Paris) les 17 et 24 octobre, via la recherche de X (acteur Apify `theagents/twitter-scraper`). Relevé le 25 octobre 2026 vers 16 h UTC : 6 683 posts. Script : `methode/collecte.py`.
- **Posts retenus** : posts originaux (ni retweets ni réponses) des comptes présents les deux jours, soit 5 320 posts.
- **Classement** : chaque post est classé par le modèle Jev (TypeSafe, version `jev-1.14.0`) à partir de cinq questions fermées (le post décrit-il des faits dans la rue, une réaction à la journée, le congrès du RN à Orléans, l'attentat de Trappes, le compte lui-même ?), puis une règle écrite en code décide « manif », « autre » ou « non tranché ». Deux questions de plus repèrent les violences policières et les pillages ou dégâts, une dernière le ton du post. Questions et règle : `methode/questions_jev.json`, `methode/classer_jev.py`.
- **Contrôle du classement** : 100 posts tirés au hasard, étiquetés à la main sans voir ni le compte ni les vues. Sur le sujet, Jev donne la même réponse que l'étiquetage humain dans 86 cas sur 88 où il tranche.
- **Intervalles** : bootstrap sur les comptes, 2 000 tirages, 95 %.

## 1. Portée brute

| Posts | 17 oct : nombre | 17 oct : vues totales | 17 oct : vues médianes | 24 oct : nombre | 24 oct : vues totales | 24 oct : vues médianes |
|---|---|---|---|---|---|---|
| Manif | 2 413 | 331,8 M | 9 962 | 1 455 | 52,7 M | 7 541 |
| Manif avec image ou vidéo | 2 198 | 298,1 M | 9 514 | 1 286 | 47,5 M | 7 676 |
| Manif, violences policières | 295 | 16,4 M | 7 816 | 288 | 10,6 M | 5 978 |
| Manif, pillages et dégâts | 836 | 198,7 M | 12 810 | 181 | 5,3 M | 8 422 |
| Autres posts des mêmes comptes | 558 | 30,6 M | 5 682 | 894 | 33,1 M | 7 415 |

- 17 octobre : les 10 posts manif les plus vus totalisent 139,3 M de vues (42 % du total). Post le plus vu : 64,8 M.
- 24 octobre : les 10 posts manif les plus vus totalisent 14,3 M de vues (27 % du total). Post le plus vu : 3,0 M.

## 2. Vues médianes des posts manif rapportées aux autres posts du même compte

Rapport = vues médianes des posts manif ÷ vues médianes des autres posts du compte, le même jour. Comptes ayant au moins 3 posts de chaque sorte chaque jour.

| Compte | Rapport 17 oct | Rapport 24 oct | Évolution |
|---|---|---|---|
| lci | 2,70 | 0,74 | -72 % |
| gptvoff | 3,25 | 0,96 | -71 % |
| lambdactu | 3,64 | 1,10 | -70 % |
| cerfiafr | 0,96 | 0,37 | -62 % |
| frontieresmedia | 1,85 | 0,77 | -59 % |
| kameliamedia13 | 4,13 | 1,72 | -58 % |
| mandat_media | 3,11 | 1,30 | -58 % |
| tf1info | 2,44 | 1,02 | -58 % |
| le_parisien | 1,24 | 0,52 | -58 % |
| directbrut | 2,04 | 0,94 | -54 % |
| radioorient | 13,73 | 6,52 | -53 % |
| bfmtv | 2,17 | 1,07 | -51 % |
| humanite_fr | 2,75 | 1,42 | -48 % |
| courrierouest | 2,69 | 1,44 | -47 % |
| l_thinktank | 1,15 | 0,65 | -44 % |
| le_figaro | 1,70 | 0,97 | -43 % |
| cnews | 2,26 | 1,33 | -41 % |
| lamarsweb | 3,31 | 2,06 | -38 % |
| impactmediafr | 0,72 | 0,46 | -37 % |
| franceinfo | 1,83 | 1,23 | -33 % |
| bref_actualites | 3,60 | 2,49 | -31 % |
| europe1 | 1,36 | 1,00 | -26 % |
| afpfr | 1,35 | 1,01 | -25 % |
| fr_presstv | 3,62 | 3,30 | -9 % |
| alertesinfos | 0,59 | 0,56 | -5 % |
| sudradio | 1,60 | 1,76 | +10 % |
| tribunepop23 | 2,49 | 2,82 | +13 % |
| 20minutes | 0,87 | 1,03 | +18 % |
| saladeinfofr | 1,51 | 1,94 | +28 % |
| lemainelibre | 3,69 | 5,96 | +61 % |
| focusmedia_fr | 0,65 | 1,12 | +73 % |
| kronikinsights | 0,33 | 1,00 | +202 % |

- Évolution médiane sur 32 comptes : **-42 %** (intervalle 95 % : -52 % ; -17 %).
- Comptes en baisse d'au moins 30 % : 21 sur 32.

## 3. Écart de portée entre sortes de posts manif

Vues relatives = log naturel des vues moins la médiane des log-vues des posts manif du même compte le même jour. Écart = moyenne du premier groupe moins moyenne du second.

| Comparaison | Écart 17 oct | Écart 24 oct | Évolution | Intervalle 95 % |
|---|---|---|---|---|
| Violences policières moins pillages | -0,15 | -0,06 | +0,09 | -0,14 ; +0,35 |
| Ton favorable aux manifestants moins ton hostile | +0,03 | +0,05 | +0,02 | -0,13 ; +0,16 |

## 4. Interactions pour 100 vues

Likes, retweets, réponses et citations, posts d'au moins 200 vues, médianes.

| Posts | 17 oct | 24 oct |
|---|---|---|
| Manif | 0,91 | 0,77 |
| Autres | 0,39 | 0,59 |

Évolution du rapport manif ÷ autres, compte par compte (29 comptes) : ×0,99 (intervalle 95 % : ×0,74 ; ×1,26).

## 5. Marques de restriction posées par X

Recherche X, posts contenant « manif », « manifestation » ou « manifestants », en français, avec image ou vidéo, 20 posts par demi-heure de 10 h à 22 h (heure de Paris), relevés dans la nuit du 24 au 25 octobre depuis un compte sans réglage de filtrage de la recherche. Fichier : `donnees/marques_x.csv`.

| Onglet | Jour | Posts | Marqués sensibles | Floutés par X | Floutés par l'auteur | Retenus dans un pays | Avertissement | Action limitée par X | Média indisponible |
|---|---|---|---|---|---|---|---|---|---|
| Récent | 17 oct | 480 | 15 | 0 | 16 | 0 | 0 | 0 | 0 |
| Récent | 24 oct | 480 | 9 | 0 | 10 | 0 | 0 | 0 | 0 |
| Top | 17 oct | 362 | 13 | 0 | 21 | 0 | 0 | 0 | 0 |
| Top | 24 oct | 362 | 4 | 0 | 13 | 0 | 0 | 0 | 1 |

## 6. Accès aux réseaux depuis la France (OONI)

Mesures de l'Open Observatory of Network Interference, France. Fichier : `donnees/ooni_france.csv`.

| Domaine | 17 oct : mesures / blocages confirmés | 24 oct : mesures / blocages confirmés |
|---|---|---|
| x.com | 238 / 0 | 292 / 0 |
| twitter.com | 453 / 0 | 534 / 0 |
| www.tiktok.com | 219 / 0 | 243 / 0 |
| www.instagram.com | 451 / 0 | 534 / 0 |
| www.snapchat.com | 66 / 0 | 77 / 0 |

x.com le 24 octobre, par opérateur : Free (AS12322) 98 mesures, Orange (AS3215) 86, Bouygues Telecom (AS5410) 36, SFR (AS15557) 27, aucun blocage confirmé.

## 7. Recherches Google en France

Google Trends, France, indice 100 = jour le plus haut de la période du 10 au 25 octobre. Fichier : `donnees/google_trends_france.csv`.

| Recherche | 17 oct | 24 oct |
|---|---|---|
| manifestation | 100 | 85 |
| manif | 30 | 24 |
| mobilisation | 3 | 1 |
| pillage | 2 | 1 |
| CRS | 4 | 2 |

## Fichiers

- `donnees/posts.csv` : un post par ligne (identifiant, compte, date, vues, interactions, présence d'un média, classement et probabilités données par Jev). Le texte des posts n'est pas inclus : chaque post se retrouve sur X à partir de son identifiant.
- `donnees/marques_x.csv`, `donnees/ooni_france.csv`, `donnees/google_trends_france.csv` : données des sections 5 à 7.
- `methode/` : liste des comptes, collecte, questions et classement Jev, analyse.

Code sous licence MIT, données sous licence CC BY 4.0.
