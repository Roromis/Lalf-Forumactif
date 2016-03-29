---
layout: page
title: Introduction
category: documentation
pos: 1
---

{% include links.md %}

Le Lalf est un logiciel permettant de convertir les données d'un forum
hébergé par Forumactif et de les importer dans un forum phpBB.

Le Lalf permet actuellement d'exporter :

- les forums et catégories
- les sujets et messages
- les émoticones
- les utilisateurs
- les groupes

L'export est malheureusement partiel, et la transition vers votre
nouveau forum ne pourra pas se faire de manière transparente, ni pour
vous, ni pour les membres de votre forum.

<div class="warning" markdown="1">
Après une exportation, il sera nécessaire de configurer manuellement :

- les permissions
- les icônes et règlements des forums
- le thème

Familiarisez vous avec l'administration de phpBB avant d'exporter
votre forum.
</div>

Il est possible (mais rare) que quelques messages soient mal convertis
(phpBB ne supporte pas l'utilisation d'html dans les messages, la
balise bbcode `[hide]` n'est pas supportée, et la balise `[table]` ne
l'est que partiellement).

Les profils des utilisateurs (avatars, signatures, ...) ne sont pour
l'instant pas exportés.

Finalement, certaines données ne peuvent pas exportées :

- les messages privés
- les mots de passe des utilisateurs
- les sondages

<div class="information" markdown="1">
Il est vivement conseillé de tester l'exportation avant de l'effectuer
de manière définitive. Créez un forum phpBB sur un serveur de test ou
sur votre machine, et assurez-vous que tout fonctionne bien. En cas de
problème, créez un [rapport de bug][], j'essayerai de vous aider
dans la mesure du possible.
</div>

Si vous êtes toujours décidé à exporter votre forum, vous pouvez
passer à l'étape d'[Installation][].
