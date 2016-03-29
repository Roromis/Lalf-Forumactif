---
layout: page
title: En cas de problème
category: annexes
toc:
- Erreurs
- Avertissements
- Problèmes
pos: 3
---

{% include links.md %}

Cette page décrit différentes erreurs, avertissements et problèmes que
vous pouvez rencontrer lors de l'utilisation du Lalf. Si vous
rencontrez une erreur qui n'est pas sur cette page, créez un
[rapport de bug][].

## Erreurs

### Le fichier de configuration (config.cfg) n'existe pas

Si vous n'avez pas créé le fichier de configuration, référez vous à
l'étape [Configuration][] de la documentation.

Si vous l'avez créé, assurez vous de vous être placé dans le dossier
contenant ce fichier avant de lancer le Lalf (voir début de l'étape
[Exportation][]).

### Le fichier de configuration (config.cfg) est invalide

Référez vous à l'étape [Configuration][] de la documentation.

## Avertissements

### Erreur lors du chargement de la sauvegarde

Si l'exportation est terminée malgré cette erreur, celle-ci n'aura
aucun effet sur l'importation. Si l'exportation échoue et cette erreur
a lieu de manière répétée, créez un [rapport de bug][].

### La balise bbcode [...] n'est pas supportée

Certaines balises bbcodes ne sont pas supportés par phpbb, ou ne le
sont que partiellement. Lors de l'exportation d'un message contenant
une de ces balises, le Lalf ajoutera un `WARNING` dans le fichier
`debug.log`.

Par exemple, si le fichier `debug.log` contient les lignes suivantes :

```
DEBUG    : Exportation du message 3706 (sujet 271)
WARNING  : La propriété "border" du bbcode [table] n'est pas supportée.
WARNING  : La balise bbcode [hide] n'est pas supportée.
```

Un fois l'importation terminée, vous pouvez comparer le message
exporté avec l'original, en ouvrant les pages :

- `http://localhost/viewtopic.php?p=3706#p3706` et
- `http://exemple.forumactif.fr/a-p3706.htm` (en remplaçant *3706* par
  le numéro indiqué dans le message de `DEBUG`)

et éventuellement effectuer des corrections.

### La propriété "..." du bbcode [...] n'est pas supportée

Voir [La balise bbcode [...] n'est pas
supportée](#la-balise-bbcode--nest-pas-supporte).

Voir également [Bordures des tableaux](#bordures-des-tableaux).

### Le message ... (sujet ...) semble être vide

Si le fichier `debug.log` contient la ligne suivante :

```
WARNING  : Le message 3706 (sujet 271) semble être vide
```

Ouvrez la page ``http://exemple.forumactif.fr/a-p3706.htm`` (en
remplaçant *3706* par le numéro indiqué), et vérifiez que le message
est vide.

S'il ne l'est pas, vous pouvez ouvrir la page
`http://localhost/viewtopic.php?p=3706#p3706` pour corriger
manuellement le message correspondant dans votre nouveau forum, et
créer un [rapport de bug][] pour me permettre de corriger ce problème.

### Le lien suivant n'a pas pu être réécrit: *lien*

Si le fichier `debug.log` contient les lignes suivantes :

```
DEBUG    : Exportation du message 3706 (sujet 271)
WARNING  : Le lien suivant n'a pas pu être réécrit: ...
```

Vous pouvez ouvrir la page
`http://localhost/viewtopic.php?p=3706#p3706` pour corriger
manuellement le lien.

Certains liens ne peuvent pas être réécrits :

 - Les fiches de personnages : `/rpg_sheet.forum?u=<id>`
 - Les pages html : `/...-h<id>.html`

Si le lien indiqué dans le message d'erreur n'est pas dans la liste
ci-dessus, créez un [rapport de bug][].

## Problèmes

### Bordures des tableaux

PhpBB ne fournit pas de BBCode tableau par défaut. Le Lalf ajoute
automatiquement un support basique des balises `[table]`, `[tr]` et
`[td]`, mais il n'est pas possible de modifier le style du tableau
(bordures, espacements...) comme cela est possible avec Forumactif.

Tous les tableaux seront affichés sans bordures.

Je vous recommande de modifier le style des tableaux dans le style de
votre forum ou en modifiant les bbcodes `[table]`, `[tr]` et `[td]`
dans le panneau d'administration.

N'hésitez pas à créer un [rapport de bug][] pour proposer vos
modifications si vous acceptez que je les intègre au Lalf ou que je
les ajoute à cette documentation.
