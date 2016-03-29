---
layout: page
title: Utiliser un thème temporaire
category: annexes
pos: 2
---

Ouvrez la partie *Thèmes temporaires* de l'onglet *Affichage* du panneau d'administration :

![Capture d'écran]({{ site.baseurl }}/images/theme-temporaire-1.png)

Cliquez sur le lien *Créer un nouveau thème temporaire* :

![Capture d'écran]({{ site.baseurl }}/images/theme-temporaire-2.png)

Sélectionnez la version *phpBB2* et cliquez sur *Ajouter* :

![Capture d'écran]({{ site.baseurl }}/images/theme-temporaire-3.png)

Notez le numéro du thème temporaire :

![Capture d'écran]({{ site.baseurl }}/images/theme-temporaire-4.png)

et modifiez la valeur `temporary_theme` dans le fichier `config.cfg` :

```conf
# Numéro du thème temporaire (optionnel)
temporary_theme=1
```
