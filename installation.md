---
layout: page
title: Installation
category: documentation
toc:
- Linux
- Windows
- MacOS
- Installation manuelle
pos: 2
---

{% include links.md %}

## Linux

Installez [GOCR][] (le paquet `gocr` est probablement disponible dans
les dépôts de votre distribution).

Lancez la commande suivante :

```bash
pip install --user -U https://github.com/Roromis/Lalf-Forumactif/archive/master.zip
```

Créez ensuite un nouveau dossier (par exemple `~/Lalf`), et
placez-vous dans ce dossier :

```bash
mkdir ~/Lalf
cd ~/Lalf
```

Copiez-y le fichier `~/.local/share/doc/lalf/config.cfg` en le
renommant en `config.cfg` :

```bash
cp ~/.local/share/doc/lalf/config.cfg .
```

Vous pouvez à présent passer à l'étape [Configuration][].

## Windows

<div class="information" markdown="1">
Par soucis de simplicité, la distribution python Miniconda est
utilisée dans ce tutoriel. Vous pouvez essayer d'utiliser la
distribution Python officielle si vous savez ce que vous faites.
</div>

Téléchargez la version *Python 3.5*, *32-bit* de [Miniconda][]. Lancez
l'installeur, et laissez les options par défaut.

Une fois l'installation terminée, ouvrez un terminal (un invite de
commande), et exécutez les commandes :

```batch
conda install lxml
pip install -U https://github.com/Roromis/Lalf-Forumactif/archive/master.zip
```

Quand la ligne `Proceed([y]/n)?` s'affiche, appuyez sur Entrée.

Créez ensuite un nouveau dossier (par exemple `C:\Lalf`), et copiez-y
le fichier
`C:\Users\<votrenom>\Miniconda3\share\doc\lalf\config.cfg`.

Téléchargez [GOCR][] (cliquez sur le lien *Windows binary*), et
enregistrez l'exécutable dans le dossier précédemment créé. Renommez le
en `gocr.exe`.

Vous pouvez à présent passer à l'étape [Configuration][].

## MacOS

<div class="information" markdown="1">
Je ne suis pas en mesure de tester le Lalf sur MacOS. La procédure
d'installation est probablement similaire à celle de [Linux](#linux).

Si vous êtes utilisateur de MacOS, n'hésitez pas à créer un
[rapport de bug][] pour m'aider à compléter cette section.
</div>

Vous pouvez à présent passer à l'étape [Configuration][].

## Installation manuelle

Téléchargez la dernière version du [Lalf][] et installez les
dépendances suivantes :

- [Python 3][python]
- [PyQuery][]
- [Requests][]
- [Pillow][]
- [GOCR][]

Placez vous dans le dossier contenant le fichier `lalf.py`. Dans la
suite, utilisez la commande `./lalf.py` à la place de `lalf`.

Vous pouvez à présent passer à l'étape [Configuration][].
