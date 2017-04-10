#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os

# from gi.repository import Gdk
# from gi.repository import Gio

tdlist = []


class ToDoListWindow(Gtk.Window):
    """Construction de la classe"""

    def __init__(self):
        # À partir du constructeur parent :
        Gtk.Window.__init__(self, title="Liste des tâches en cours")
        self.set_default_size(300, 250)
        self.set_border_width(5)

        # Instanciation d'une grille qui recevra les éléments de l'application :
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.grid.set_column_spacing(5)  # Espacement entre éléments (boutons, etc)
        self.add(self.grid)  # Ajout de la grille à la fenêtre maître définie par cette classe

        # Création de la liste des tâches et déclaration de son contenu :
        self.tdlist_store = Gtk.ListStore(bool, str)
        # Ajout des infos à cette liste :
        for tache in tdlist:
            self.tdlist_store.append([False, tache])
        self.current_filter_language = None

        # Instanciation du type de vue à partir du "ListStore" créé :
        self.tdview = Gtk.TreeView(model=self.tdlist_store)

        # Instanciation des cellules des cases à cocher :
        renderer_check = Gtk.CellRendererToggle()
        renderer_check.connect("toggled", self.on_task_check)

        # Instanciation d'une colonne contenant les cellules de cases à cocher :
        column_check = Gtk.TreeViewColumn("Finie", renderer_check,
                                          active=0)
        # Ajout de cette colonne à la vue "tdview" créée précédemment :
        self.tdview.append_column(column_check)

        # Instanciation des cellules recevant les tâches :
        renderer_task = Gtk.CellRendererText()
        renderer_task.set_property("editable", True)  # Ces cellules seront éditables...
        renderer_task.connect("edited", self.on_task_edit)  # ... et cette fonction exécutée à l'édition

        # Instanciation d'une colonne recevant les cellules des tâches :
        self.column_task = Gtk.TreeViewColumn("Description de la tâche",
                                              renderer_task, text=1)
        self.column_task.set_sort_column_id(1)  # Cette colonne sera triable.
        # Ajout de cette colonne à la vue "tdview" créée précédemment :
        self.tdview.append_column(self.column_task)

        # Par défaut les cellules ne seront pas sélectionnables (le mode "Édition" le permettra) :
        self.sel = self.tdview.get_selection()
        self.sel.set_mode(Gtk.SelectionMode.NONE)

        # Instanciation d'un conteneur (fenêtre) scrollable qui recevra la vue "tdview" :
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.scrollable_treelist.set_border_width(5)
        self.scrollable_treelist.add(self.tdview)  # Ainsi on peut scroller dans la vue "liste des tâches" (tdview)

        # Ajout des boutons :
        self.buttons = list()
        for action in ["Enregistrer",
                       "Nouvelle tâche",
                       "Supprimer",
                       "Quitter"]:
            button = Gtk.Button(action)
            self.buttons.append(button)
            button.connect("clicked", self.on_sel_action)  # Connexion des boutons à la fonc. de sélection des actions
        self.buttons[2].disconnect_by_func(self.on_sel_action)  # ... sauf "Supprimer" (activé par le mode "Édition")

        # Instanciation du label du switch du mode "Édition" :
        self.switch_label = Gtk.Label("Mode édition")
        # Instanciation du switch lui-même :
        self.switch_edit = Gtk.Switch()
        self.switch_edit.connect("notify::active", self.on_edit_active)  # Lorsque actif, lancer la fonction
        self.switch_edit.set_active(False)  # Switch inactif par défaut

        self.grid.attach(self.scrollable_treelist, 0, 0, 4, 5)  # Ajout du conteneur scrollable à la grille

        self.grid.attach_next_to(self.switch_label, self.scrollable_treelist,
                                 Gtk.PositionType.BOTTOM, 1, 1)  # Ajout du label du switch en dessous
        self.grid.attach_next_to(self.switch_edit, self.switch_label,
                                 Gtk.PositionType.RIGHT, 1, 1)  # Ajout du switch à droite de son label
        self.grid.attach_next_to(self.buttons[0], self.switch_label,
                                 Gtk.PositionType.BOTTOM, 1, 1)  # Ajout du 1er bouton sous le label
        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(button, self.buttons[i],
                                     Gtk.PositionType.RIGHT, 1, 1)  # Ajout successif des autres boutons à droite du 1er

        # Si fichier de données existe : le charger, sinon proposer création :
        self.on_startup_file_load()

        # Afficher la fenêtre définie par cette classe :
        self.show_all()

    def on_startup_file_load(self):
        """Au lancement de l'application, on essaye d'ouvrir le fichier des tâches"""
        self.share_dir = os.path.expanduser('~/.local/share/simpletodo')
        if not os.path.exists(self.share_dir):
            os.makedirs(self.share_dir, mode=0o775)
        if not os.path.exists(self.share_dir+"/todo.lst"):
            self.tdfile_creation_dialog()  # S'il n'existe pas, un dialogue propose sa création
        # Si le fichier est vide (taille == 0 ), ne pas chercher à le charger :
        elif os.path.getsize(self.share_dir+"/todo.lst") == 0:
            pass
        else:
            # S'il existe, on l'ouvre et ajoute ses entrées au ListStore (self.tdlist_store) :
            with open(self.share_dir+"/todo.lst", 'r') as file_in:
                for i, l in enumerate(file_in):
                    pass
            file_len = i + 1
            with open(self.share_dir+"/todo.lst", 'r') as file_in:
                c = 0
                while c < file_len:
                    entry = file_in.readline().split()
                    # Formatage de l'entrée avant ajout au ListStore :
                    cleaned_entry = (str(entry[0]).strip(','), str(' '.join(entry[1:])))
                    # print(str(entry[0]).strip(','))
                    self.tdlist_store.append(cleaned_entry)
                    # Bidouille pour les cases à cocher retrouver leur état précédent :
                    # todo : fixer ça aussi en même temps que le formatage des entrées
                    if entry[0] == "False,":  # Si l'état = à False (mal formaté)...
                        iter = self.tdlist_store.get_iter(c)  # ... récupérer l'adresse du "row" en cours d'édition
                        state = self.tdlist_store.get_value(iter, 0)  # ... récup la valeur de la 1ère colonne
                        self.tdlist_store.set_value(iter, 0, False)  # ... et la définir à False (bien formaté)
                    c += 1

    def tdfile_creation_dialog(self):
        """Dialogue si aucun fichier trouvé"""
        dialog = ConfirmDialog(self)  # Instanciation d'un objet de la classe "ConfirmDialog"
        dialog.label.set_text("Aucun fichier de tâches trouvé.\nFaut-il en créer un ?")  # Définition du texte
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            open(self.share_dir+"/todo.lst", 'w').close()  # Si "oui", créer un fichier
            dialog.destroy()
        else:
            dialog.destroy()  # Si "non", fermer le dialogue et continuer

    def on_sel_action(self, widget):
        """Sélection de l'action à mener en fonction du bouton cliqué"""
        if widget.get_label() == "Nouvelle tâche":
            self.on_launch_creation()
        elif widget.get_label() == "Enregistrer":
            self.on_save_list()
        elif widget.get_label() == "Supprimer":
            self.on_row_delete()
        elif widget.get_label() == "Quitter":
            self.on_save_list()
            Gtk.main_quit()

    def on_task_edit(self, widget, path, text):
        """Action à mener à l'édition des entrées de cellules"""
        self.tdlist_store[path][1] = text

    def on_edit_active(self, switch, gparam):
        """Action lors du passage en mode édition"""
        if self.switch_edit.get_active():  # Si le switch devient actif...
            self.buttons[2].connect("clicked", self.on_sel_action)  # ...rendre le bouton "Supprimer" actif...
            self.sel.set_mode(Gtk.SelectionMode.SINGLE)  # ...et permettre la sélection des "rows" (des tâches donc)
        else:  # S'il devient inactif...
            self.sel.set_mode(Gtk.SelectionMode.NONE)  # ...interdire la sélection

    def on_row_delete(self):
        """Sélection d'une ligne pour suppression"""
        # Obtenir "l'adresse" de(s) "row(s)" sélectionnés (sous forme d'un tuple(ListStore, "path" du "row")) :
        selection = self.tdview.get_selection()
        self.tdlist_store, paths = selection.get_selected_rows()

        # Obtenir le "TreeIter" des "rows" sélectionnés :
        for path in paths:
            iter = self.tdlist_store.get_iter(path)

        # Et on supprime le "row" référencé par l'iter obtenu :
        self.tdlist_store.remove(iter)

    def on_launch_creation(self):
        """Afficher la boîte de création d'une nouvelle tâche"""
        # Instanciation d'un objet de la classe "AddTaskEntry" et définition de sa fonction de callback
        self.ta = AddTaskEntry(self.on_create_new)
        self.ta.show()

    def on_create_new(self, text):
        """Ajouter la tâche au ListStore"""
        # L'objet de création de tâche renvoie une valeur qu'on ajoute en fin du ListStore :
        self.tdlist_store.insert_with_valuesv(-1, [1], [text])
        self.ta.close()

    def on_task_check(self, widget, path):
        """Action lorsque case à cocher activée"""
        self.tdlist_store[path][0] = not self.tdlist_store[path][0]  # Inverser l'état de la case

    def on_save_list(self):
        """Enregistrer la liste dans le fichier '.todo.lst'"""
        file_out = open(self.share_dir+"/todo.lst", 'w')
        for row in self.tdlist_store:
            # Ajout d'un retour à la ligne pour obtenir un fichier ligne à ligne
            file_out.write(str(row[0])+", "+str(''.join(row[1])) + "\n")
        file_out.close()


class AddTaskEntry(ToDoListWindow):
    """Fenêtre permettant d'ajouter une tâche"""

    def __init__(self, callback):  # Instanciation de la fenêtre avec sa fonction de callback
        Gtk.Window.__init__(self, title="Nouvelle tâche")
        self.callback = callback

        # Paramètre de taille et esthétiques :
        self.set_size_request(400, 70)
        self.set_border_width(10)

        # Instanciation d'une boîte pour organiser les éléments créés ci-dessous :
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.add(box)  # Ajout de la boîte à la fenêtre maîtresse

        # Instanciation d'une boîte de saisie :
        self.task_entry = Gtk.Entry()
        self.task_entry.set_text("Saisir une tâche")  # Texte par défaut
        self.task_entry.set_property("editable", True)  # Boîte de saisie bien entendu éditable par défaut
        self.task_entry.connect("activate", self.on_task_create)  # La touche <Entrée> lance la fonction de création
        box.pack_start(self.task_entry, True, True, 0)  # Ajout de la boîte de saisie au conteneur "box"

        # Instanciation d'un bouton permettant de valider l'entrée saisie :
        self.task_create_button = Gtk.Button("Ajouter")
        self.task_create_button.connect("clicked", self.on_task_create)  # Au clic, lancer fonction de création
        box.pack_start(self.task_create_button, True, True, 1)  # Ajout du bouton au conteneur "box"

        self.show_all()

    def on_task_create(self, button):
        """Action à mener lorsque le bouton de création est activé (ou <Entrée> est pressée,
        fait appel à la classe maîtresse"""
        nt = self.task_entry.get_text()  # Récupération de la valeur saisie dans "task_entry"
        self.callback(self.task_entry.get_text())  # Envoi de cette valeur à la fonction de callback définie
        # ici : "on_create_new" (définie via "on_launch_creation")


class ConfirmDialog(Gtk.Dialog):
    """Classe de dialogue Oui/Non simple"""

    def __init__(self, parent):
        # Instantiation du modèle depuis la classe parente :
        Gtk.Dialog.__init__(self, "Confirmation", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        # Paramètres de taille par défaut :
        self.set_default_size(150, 100)

        # Aucun label défini, il le sera à l'instanciation de l'objet depuis une autre fonction :
        self.label = Gtk.Label("")

        # Box = le contenu du widget dialog :
        box = self.get_content_area()
        box.set_border_width(10)  # Pour faire plus joli
        box.add(self.label)  # Ajout du label

        self.show_all()


### __Lancement du programme__ ###
if __name__ == '__main__':
    # Instanciation d'un objet depuis la classe maîtresse :
    win = ToDoListWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
