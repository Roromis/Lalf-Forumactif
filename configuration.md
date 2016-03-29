---
layout: page
title: Configuration
category: documentation
toc:
- Forum
- Lalf
pos: 3
---

{% include links.md %}

## Forum

Le Lalf exporte les données en parcourant votre forum, et quelques
modifications sont nécessaire pour rendre ces données lisibles (aucune
de ces modifications ne sera visible par vos membres).

Dans votre profil, sélectionnez : 

 - la langue française
 - un fuseau horaire *UTC +00:00*
 - le format de date *jour J mois AAAA - HH:MM*

(voir [configurer votre profil][] pour plus de détails)

Votre forum doit utiliser la version de thème *phpBB2*. Si ce n'est
pas le cas, vous pouvez utiliser un thème temporaire (voir
[utiliser un thème temporaire][] pour plus de détails).

## Lalf

<div class="information" markdown="1">
Dans la suite de cette documentation, je supposerai que :

- l'adresse de votre ancien forum est `http://exemple.forumactif.fr/`
- l'adresse de votre nouveau forum est `http://localhost/`

Remplacez ces adresses par les votres.
</div>

### Paramètres du forum

Ouvrez le fichier `config.cfg` avec votre éditeur de texte favori et
commencez par modifier les options suivantes :

```conf
# Adresse de votre forum (par exemple exemple.forumactif.fr)
url=exemple.forumactif

# Nom d'utilisateur de l'administrateur
admin_name=

# Mot de passe de l'administrateur
admin_password=
```

### Réécriture des liens

Par défaut, les liens internes de votre forum ne sont pas
modifiés. Par exemple, si un message contient un lien vers un sujet,
ce lien ne sera pas modifié lors de l'exportation, et pointera donc
vers votre ancien forum.

Si vous souhaitez éviter ce problème, activez la réécriture des liens :

```conf
# Réécrire les liens internes
# Permet d'éviter que des liens pointent vers votre ancien forum
rewrite_links=true
```

Il sera alors nécessaire d'indiquer l'adresse de votre nouveau
forum. Vous pouvez utiliser l'adresse `http://localhost/...` lors de vos tests,
mais n'oubliez pas de redéfinir cette option avant d'exporter
définitivement votre forum.

```conf
# Lien de votre nouveau forum (utilisé pour la réécriture des liens internes)
phpbb_url=http://localhost
```

Une fois l'exportation terminée, vous pouvez modifier l'option
`phpbb_url` et relancer le Lalf. Le fichier phpbb.sql sera regénéré.

### Autres options

Les autres options sont documentées dans le fichier `config.cfg`, et
n'ont normalement pas besoin d'être modifiées.

Vous pouvez à présent passer à l'étape [Exportation][].
