**SimpleTodo** est un petit gestionnaire de liste de tâches simple avec onglet.
Il est écrit en Python3 et dispose d'une interface GTK3.

![https://code.eveha.fr/sebastien.poher/simpleTodo/raw/dev/capture.png](https://code.eveha.fr/sebastien.poher/simpleTodo/raw/dev/capture.png)

**Installation :**

Pour une installation rapide et basique, il suffit de récupérer le fichier *simpletodo* et de lancer le logiciel avec la commande :

`python3 simpletodo`

Un RPM est également disponible auprès de l'auteur pour une installation propre pour tout le système (fonctionne sur openSUSE et Fedora).

**Utilisation :**

***Gérer les projets :***

Au premier lancement, un projet par défaut est proposé, il est possible de le renommer via l'entrée de menu « Renommer... » puis d'y ajouter des tâches.
Pour créer un nouveau projet, il suffit de cliquer sur le « + » dans la barre de titre.
De même, pour supprimer un projet, il suffit de cliquer sur le « - ». Toutes les tâches du projets sont évidemment supprimées avec lui.

***Gérer les tâches :***

Pour ajouter une tâche, il suffit de cliquer sur « Nouvelle tâche » puis de saisir son nom ou sa description.
La case à cocher devant la description de la tâches indique son état (finie / non finie).
À chaque « coche » ou « décoche » d'une tâche, un indicateur de pourcentage accompli est mis à jour et affiché.

Pour éditer une tâche, il faut passer en mode édition (basculer l'état de l'interrupteur ou <Ctrl +e>).
Dans ce mode vous pouvez :

- double cliquer sur la tâche pour éditer sa description ;
- cliquer une fois sur la tâche pour la sélectionner et cliquer sur « Supprimer » pour la supprimer ;
- cliquer une fois sur la tâche pour la sélectionner puis choisir le nom d'un projet dans la liste déroulant pour la déplacer vers ce projet.

***Raccourcis clavier***

L'application utilise les raccourcis suivants :

- Ctrl + n : créer une nouvelle tâche ;
- Ctrl + e : basculer l'état du mode « Édition ».

**Quitter l'application :**

Le bouton « Quitter » enregistre tous les projets et ferme l'application.

**Fichiers :**

L'application enregistre les projets dans des fichiers séparés dans le répertoire de l'utilisateur sous *$HOME/.local/share/simpletodo*.
