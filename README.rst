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

Installation
============

Méthode 1 (avec pip)
--------------------

Installez python 3 et `pip
<http://www.pip-installer.org/en/latest/installing.html>`_, puis
exécutez::

  pip install lalf --pre

Si vous souhaitez utiliser la reconnaissance de caractères pour la
récupération des adresses e-mail (conseillé), installez `gocr
<http://jocr.sourceforge.net/>`_ (sous windows, téléchargez
l'exécutable dans le même dossier que le fichier lalf.py).

Méthode 2 (sans pip)
--------------------

Installez les dépendances suivantes :

- `PyQuery <https://bitbucket.org/olauzanne/pyquery/>`_
- `Requests <http://docs.python-requests.org/en/latest/>`_
- `pypng <https://github.com/drj11/pypng>`_

Téléchargez la dernière version du lalf.

Si vous souhaitez utiliser la reconnaissance de caractères pour la
récupération des adresses e-mail (conseillé), installez `gocr
<http://jocr.sourceforge.net/>`_ (sous windows, téléchargez
l'exécutable dans le même dossier que le fichier lalf.py).

Utilisation
===========

Prérequis
---------

- Vous devez être administrateur du forum que vous souhaitez exporter.
 
- Le forum doit être hébergé par forumactif, et doit utiliser le 
  template (style) phpbb2.
   
- Le format des dates de votre forum doit-être "jour J mois AAAA - 
  HH:MM" (par exemple: Lun 1 Jan 2009 - 00:01), vous devez modifier 
  cela dans le profil de l'administrateur.

Exportation
-----------

- Créez le fichier de configuration config.cfg en vous inspirant du
  fichier config.example.cfg. Vous pouvez placer ce fichier dans le
  même dossier que le script, ou dans le dossier ~/Lalf.

- Lancez le script ``lalf.py``.
  Il est possible que vous ayez des erreurs de connection pendant
  l'exécution du script, dans ce cas essayez de le relancer.

Importation
-----------

- Installez un forum PhpBB3 en suivant la procédure habituelle.

- Déconnectez vous.

- Importez le fichier phpbb.sql généré par le script dans votre base
  de donnée. Ce fichier se trouve dans le même dossier que le fichier
  config.cfg.

- Copiez le dossier images (s'il existe) à la racine de votre
  installation de phpbb (fusionnez le avec le dossier images
  existant). Ce dossier contient les icônes de vos forums.

Resynchronisation
-----------------

- Connectez vous au panneau d'administration en utilisant les
  identifiants de l'administrateur de votre ancien forum et
  resynchronisez les statistiques, les compteurs de messages et les
  sujets pointés (Onglet Général).
   
- Resynchronisez tous les forums/sous-forums (Onglet Forums, Bouton 
  orange "Resynchroniser" à droite de chaque forum).
   
- Créez les index de recherche (Onglet Maintenance -> Base de donnée 
  -> Index de recherche, cliquez sur les deux boutons "Supprimer 
  l'index de recherche" (s'ils sont présent) puis sur les boutons 
  "Créer l'index de recherche").
   
- Téléchargez le Support Toolkit (et éventuellement la traduction 
  française) sur http://www.phpbb.com/support/stk/ et extrayez le 
  dossier stk/stk à la racine de votre forum. Ouvrez ce dossier dans 
  votre navigateur (http://phpbb/stk) et réanalysez les 
  BBCodes (onglet Outils pour les administrateurs, cochez "Réanalyser 
  tous les BBCodes" et cliquez sur Envoyer).
   
- Modifiez les permissions de vos forums (par défaut, ils sont 
  visibles par tous les utilisateurs et les invités), ajoutez les 
  modérateurs, co-administrateurs manuellement.

Crédits
=======

Programmé en python en utilisant :

- `PyQuery <https://bitbucket.org/olauzanne/pyquery/>`_
- `Requests <http://docs.python-requests.org/en/latest/>`_
- `pypng <https://github.com/drj11/pypng>`_
- `gocr <http://jocr.sourceforge.net/>`_

En s'inspirant des `Crawler Converters <http://www.phpbb.com/community/viewtopic.php?f=65&t=1761395>`_
de nneonneo.
