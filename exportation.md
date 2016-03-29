---
layout: page
title: Exportation
category: documentation
pos: 4
---

{% include links.md %}

Ouvrez un terminal, et placez vous dans le dossier créé à l'étape
[Installation][] :

```bash
cd $dossier
```

(remplacez `$dossier` par le chemin du dossier, par exemple `~/Lalf`
ou `C:\Lalf`)

Exécutez la commande suivante :

```bash
lalf
```

La progression du script est affichée dans le terminal.

Trois fichiers seront créés :

 - Le fichier `debug.log`, qui contient des informations qui pourront
   vous permettre de corriger d'éventuels problèmes par la suite.
 - Le fichier `phpbb.sql`, qui contient les données de votre forum
   converties pour être compatible avec phpbb.
 - Le fichier `save.pickle`, qui contient une sauvegarde des données
   exportées par le Lalf, et lui permettant de reprendre une
   exportation interrompue.

Il est également possible qu'un dossier `images` soit créé. Ce dossier
contient les émoticones que vous avez ajouté à votre forum.

En cas d'erreur critique, l'exportation sera interrompue et un message
sera affiché par le Lalf dans le terminal. Référez vous à l'annexe
[En cas de problème][erreurs].

Certaines erreurs non critiques seront détectées par le Lalf. Elles
seront indiquées par un avertissement (une ligne commençant par
`WARNING`) dans le fichier `debug.log`. Ces avertissements
n'empêcheront pas l'importation de votre forum dans phpbb, mais il
peut être intéressant de les relever pour pouvoir les corriger a
posteriori. Si vous trouvez de telles erreurs, vous pouvez vous
référer à l'annexe [En cas de problème][avertissements].

Une fois l'exportation effectuée avec succès, vous pouvez passer à
l'étape [Importation][].
