======
 Lalf
======

Note importante
===============

Ce programme est un logiciel libre ; vous pouvez le redistribuer et/ou
le modifier au titre des clauses de la Licence Publique Générale GNU,
telle que publiée par la Free Software Foundation ; soit la version 3
de la Licence.

Ce programme est distribué dans l'espoir qu'il sera utile, mais SANS
AUCUNE GARANTIE ; sans même une garantie implicite de COMMERCIABILITE
ou DE CONFORMITE A UNE UTILISATION PARTICULIERE. Voir la Licence
Publique Générale GNU pour plus de détails. Vous devriez avoir reçu
un exemplaire de la Licence Publique Générale GNU avec ce programme.
Les auteurs déclinent toutes responsabilités quant à l'utilisation
qui pourrait en être faite.

Documentation
=============

Prérequis
---------

- Vous devez être administrateur du forum que vous souhaitez exporter.

- Le forum doit être hébergé par forumactif, et doit utiliser la
  version phpbb2 du thème. Dans le cas contraire, vous pouvez créer
  un thème temporaire utilisant la version phpbb2 (dans le panneau
  d'administration, onglet "Affichage", "Thèmes temporaires").

- Le format des dates de votre forum doit-être "jour J mois AAAA -
  HH:MM" (par exemple: Lun 1 Jan 2009 - 00:01), vous devez modifier
  cela dans le profil de l'administrateur.

Exportation
-----------

Vous pouvez installer le lalf avec le gestionnaire de paquets pip (qui
installera automatiquement toutes les dépendances nécessaires) en
suivant la `méthode 1`_ ou sans pip (auquel cas vous devrez
installer les dépendances manuellement) en suivant la `méthode 2`_.

.. _méthode 1:

Méthode 1 (avec pip)
~~~~~~~~~~~~~~~~~~~~

Installez python 3 et `pip
<http://www.pip-installer.org/en/latest/installing.html>`_, puis
exécutez (l'option ``--user`` est optionnelle, elle permet d'installer
le lalf sans droits d'administrateurs)::

  pip install [--user] -U git+https://github.com/Roromis/Lalf-Forumactif.git@v3

Pour désintaller le lalf, il suffira d'exécuter::

  pip uninstall lalf

Créez un nouveau dossier (l'emplacement importe peu), et créez y le
fichier de configuration ``config.cfg`` en vous inspirant du fichier
``config.example.cfg``.

Si vous souhaitez utiliser la reconnaissance de caractères pour la
récupération des adresses e-mail (conseillé), installez `gocr
<http://jocr.sourceforge.net/>`_ (sous windows, téléchargez
l'exécutable dans le même dossier que le fichier ``config.cfg``).

Placez vous dans le dossier contenant le fichier de configuration, et
lancez::

  lalf

.. _méthode 2:

Méthode 2 (sans pip)
~~~~~~~~~~~~~~~~~~~~

Installez les dépendances suivantes :

- `PyQuery <https://bitbucket.org/olauzanne/pyquery/>`_
- `Requests <http://docs.python-requests.org/en/latest/>`_
- `Pillow <http://python-pillow.org/>`_

Téléchargez la dernière version du lalf et extrayez l'archive.

Créez le fichier de configuration ``config.cfg`` en vous inspirant du
fichier ``config.example.cfg``.

Si vous souhaitez utiliser la reconnaissance de caractères pour la
récupération des adresses e-mail (conseillé), installez `gocr
<http://jocr.sourceforge.net/>`_ (sous windows, téléchargez
l'exécutable dans le même dossier que le fichier ``config.cfg``).

Placez vous dans le dossier contenant le fichier de configuration, et
lancez::

  ./lalf.py

Importation
-----------

- Installez un forum PhpBB 3.0.x en suivant la procédure habituelle
  (cette version n'est pas compatible avec phpBB 3.1, vous pourrez
  effectuer la mise à jour à la fin de l'exportation).

- Déconnectez vous.

- Importez le fichier ``phpbb.sql`` généré par le script dans votre
  base de donnée. Ce fichier se trouve dans le même dossier que le
  fichier ``config.cfg``.

- Copiez le dossier ``images`` (s'il existe) à la racine de votre
  installation de phpbb (fusionnez le avec le dossier ``images``
  existant). Ce dossier contient les icônes de vos forums.

Resynchronisation
-----------------

- Connectez vous au panneau d'administration en utilisant les
  identifiants de l'administrateur de votre ancien forum et
  resynchronisez les statistiques, les compteurs de messages et les
  sujets pointés (Onglet Général).

- Créez les index de recherche (Onglet Maintenance -> Base de donnée
  -> Index de recherche, cliquez sur les deux boutons "Supprimer
  l'index de recherche" (s'ils sont présent) puis sur les boutons
  "Créer l'index de recherche").

- Modifiez les permissions de vos forums (par défaut, ils sont
  visibles par tous les utilisateurs et les invités), ajoutez les
  modérateurs, co-administrateurs manuellement.

- (Optionnel) Si vous constatez des erreurs dans les compteurs de
  sujets de messages ou de sujets, resynchronisez les forums touchés
  par ce problème (Onglet Forums, Bouton orange "Resynchroniser" à
  droite de chaque forum).

- (Optionnel) Il est possible qu'il y ait eut des erreurs lors de la
  transcription des messages en bbcodes. Si vous constatez un tel
  problème (messages incomplets, bbcodes non traités, ...), essayez
  d'éditer le message en question pour vérifier que le bbcode est
  correct.

  - Si le bbcode est incorrect, créez un `rapport d'erreur
    <https://github.com/Roromis/Lalf-Forumactif/issues>`_, en
    fournissant les codes du message original et du nouveau.

  - Si le bbcode est correct, réenvoyer le message devrait corriger le
    formatage. Si plusieurs messages sont affecté, il est possible de
    les corriger tous : téléchargez le Support Toolkit (et
    éventuellement la traduction française) sur
    http://www.phpbb.com/support/stk/ et extrayez le dossier stk/stk à
    la racine de votre forum. Ouvrez ce dossier dans votre navigateur
    (http://phpbb/stk) et réanalysez les BBCodes (onglet Outils pour
    les administrateurs, cochez "Réanalyser tous les BBCodes" et
    cliquez sur Envoyer).

Crédits
=======

Programmé en python en utilisant :

- `PyQuery <https://bitbucket.org/olauzanne/pyquery/>`_
- `Requests <http://docs.python-requests.org/en/latest/>`_
- `Pillow <http://python-pillow.org/>`_
- `gocr <http://jocr.sourceforge.net/>`_

En s'inspirant des `Crawler Converters
<http://www.phpbb.com/community/viewtopic.php?f=65&t=1761395>`_ de
nneonneo.

Merci aux contributeurices :

- `jeancf <https://github.com/jeancf>`_
- `vikbez <https://github.com/vikbez>`_
