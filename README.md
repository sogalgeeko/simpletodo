**SimpleTodo** est un petit gestionnaire de liste de tâches simple avec onglet.
Il est écrit en Python3 et dispose d'une interface GTK3.

![https://code.eveha.fr/sebastien.poher/simpleTodo/raw/dev/capture.png](https://code.eveha.fr/sebastien.poher/simpleTodo/raw/dev/capture.png)

**Installation :**

Pour une installation rapide et basique, il suffit de récupérer le fichier *simpletodo* et de lancer le logiciel avec la commande :

`python3 simpletodo`

Un RPM est également disponible auprès de l'auteur pour une installation propre pour tout le système (fonctionne sur openSUSE et Fedora).

**Utilisation :**

Au premier lancement, un projet par défaut est proposé, il est possible de le renommer via l'entrée de menu « Renommer... » puis d'y ajouter des tâches.
La case à cocher devant la description de la tâches indique son état (finie / non finie).
À chaque « coche » ou « décoche » d'une tâche, un indicateur de pourcentage accompli est mis à jour et affiché.

Pour éditer ou supprimer une tâche, il faut passer en mode édition puis :
- double cliquer sur la tâche pour l'éditer ;
- cliquer une fois sur la tâche pour la sélectionner et cliquer sur « Supprimer » pour la supprimer.

Pour créer un nouveau projet, il suffit de cliquer sur le « + » dans la barre de titre.
De même, pour supprimer un projet, il suffit de cliquer sur le « - ». Toutes les tâches du projets sont évidemment supprimées avec lui.

L'application enregistre les projets dans des fichiers séparés dans le répertoire de l'utilisateur sous *$HOME/.local/share/simpletodo*.

Le bouton « Quitter » enregistre tous les projets et ferme l'application.

***Raccourcis clavier***

L'application utilise les raccourcis suivants :

- Ctrl + n : créer une nouvelle tâche ;
- Ctrl + e : basculer l'état du mode « Édition ».
