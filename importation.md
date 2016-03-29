---
layout: page
title: Importation
category: documentation
pos: 5
---

{% include links.md %}

Installez phpBB **3.0.x** en suivant la
[procédure habituelle][installation phpbb] (le Lalf n'est pas
compatible avec phpBB 3.1, vous pourrez effectuer la mise à jour à la
fin de l'importation).

<div class="information" markdown="1">
Soyez certain d'être déconnecté du forum avant de passer à la
suite. Si vous n'arrivez pas à vous connecter par la suite, essayez de
supprimer les cookies de votre navigateur.
</div>

Importez ensuite le fichier `phpbb.sql` généré par le script dans
votre base de donnée.

<div class="warning" markdown="1">
Le Lalf a été testé uniquement avec MySQL. Si vous utilisez un autre
type de base de donnée, créez un [rapport de bug][] pour signaler vos
problèmes ou pour m'indiquer que l'importation fonctionne.
</div>

Si un dossier `images` a été créé, copiez le à la racine de votre
installation de phpbb (fusionnez le avec le dossier `images`
existant).

Vous pouvez maintenant vous connecter à votre nouveau forum en
utilisant les identifiants que vous avez indiqué dans le fichier
`config.cfg`.

Dans le panneau d'administration, *Resynchronisez les sujets pointés*
et *Purgez le cache* :

![Capture d'écran]({{ site.baseurl }}/images/importation-1.png)

Vous pouvez maintenant accéder à votre nouveau forum. Vérifiez que les
messages importants sont bien formattés.

Comme indiqué en [Introduction][], certaines données n'ont pas pu être
exportées. Vous pouvez maintenant configurer manuellement :

- les permissions (par défaut, tous les forums sont publics)
- les règles et les icônes de vos forums
- le style

Pour se connecter au nouveau forum, vos utilisateurs devront
renouveler leur mot de passe :

![Capture d'écran]({{ site.baseurl }}/images/importation-2.png)

L'importation de votre forum est à présent terminée!

Si vous avez des suggestions d'amélioration du Lalf ou de sa
documentation, créez un [rapport de bug][], Si tout s'est bien passé,
n'hésitez pas à faire un [don][].
