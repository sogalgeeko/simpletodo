#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class HeaderBarWindow(Gtk.Window):

    def __init__(self):
        """Initialisation d'une classe Window"""

        Gtk.Window.__init__(self, title="Simple Todo")
        self.set_border_width(10)
        self.set_default_size(600, 350)

        headerb = Gtk.HeaderBar()
        headerb.set_show_close_button(True)
        headerb.props.title = "Simple Todo"
        self.set_titlebar(headerb)

        navbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(navbox.get_style_context(), "linked")

        prjbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(prjbox.get_style_context(), "linked")

        prevb = Gtk.Button()
        prevb.add(Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE))
        prevb.connect("clicked", self.on_page_prev)
        navbox.add(prevb)

        nextb = Gtk.Button()
        nextb.add(Gtk.Arrow(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE))
        nextb.connect("clicked", self.on_page_next)
        navbox.add(nextb)

        newtab = Gtk.Button()
        img = Gtk.Image.new_from_icon_name("list-add-symbolic",
                                           Gtk.IconSize.MENU)
        newtab.set_image(img)
        newtab.connect("clicked", self.on_new_project)
        prjbox.add(newtab)

        deltab = Gtk.Button()
        img = Gtk.Image.new_from_icon_name("list-remove-symbolic",
                                           Gtk.IconSize.MENU)
        deltab.set_image(img)
        deltab.connect("clicked", self.on_del_project)
        prjbox.add(deltab)

        headerb.pack_start(navbox)
        headerb.pack_end(prjbox)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.main_box)

        self.tnotebook = TaskNoteBook()
        self.main_box.add(self.tnotebook)

        self.buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.main_box.add(self.buttons_box)

        # Ajout des boutons :
        self.buttons = list()
        for action in ["Enregistrer",
                       "Nouvelle tâche",
                       "Supprimer",
                       "Quitter"]:
            button = Gtk.Button(action)
            self.buttons.append(button)
            button.connect("clicked", self.tnotebook.page1.on_sel_action)  # Connexion des boutons à la fonc. de sélection des actions
        #self.buttons[2].disconnect_by_func(self.on_sel_action)  # ... sauf "Supprimer" (activé par le mode "Édition")

        # Instanciation du label du switch du mode "Édition" :
        self.switch_label = Gtk.Label("Mode édition")
        # Instanciation du switch lui-même :
        self.switch_edit = Gtk.Switch()
        self.switch_edit.connect("notify::active", self.on_edit_active)  # Lorsque actif, lancer la fonction
        self.switch_edit.set_active(False)  # Switch inactif par défaut


        self.buttons_box.add(self.switch_label)  # Ajout du label du switch en dessous
        self.buttons_box.add(self.switch_edit)   # Ajout du switch à droite de son label
        #self.main_box.add(self.buttons[0])    # Ajout du 1er bouton sous le label
        for i, button in enumerate(self.buttons):
            self.buttons_box.add(self.buttons[i])  # Ajout successif des autres boutons à droite du 1er


    def on_page_next(self, tnotebook):
        """Switch to next tab"""
        self.tnotebook.next_page()

    def on_page_prev(self, tnotebook):
        """Switch to previous tab"""
        self.tnotebook.prev_page()

    def on_new_project(self, tnotebook):
        """Initialize input window with 'on_new_tab' as callback function"""
        self.pjr_name_input = InputWin("Nouveau projet", self.on_new_tab)
        self.pjr_name_input.show()

    def on_new_tab(self, text):
        """Actually append page to notebook"""
        newpage = ToDoListBox()
        newpage.add(Gtk.Label('Nouvelle page'))
        self.tnotebook.append_page(newpage, Gtk.Label(text))
        self.tnotebook.show_all()
        self.pjr_name_input.close()
        self.tnotebook.set_current_page(-1)

    def on_del_project(self, tnotebook):
        """Remove page from notebook"""
        #TODO : insure that all tasks in page are removed too
        self.tnotebook.remove_page(self.tnotebook.get_current_page())

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


class TaskNoteBook(Gtk.Notebook):

    def __init__(self):
        """Initialize Notebook class instance"""
        Gtk.Notebook.__init__(self)
        self.set_border_width(3)

        # Append 2 default pages for testing purpose
        # TODO : remove second page
        self.page1 = ToDoListBox()
        #self.page1.set_border_width(10)
        #self.page1.add(ToDoListBox())
        self.append_page(self.page1, Gtk.Label('Titre test'))

        self.page2 = Gtk.Box()
        self.page2.set_border_width(10)
        self.page2.add(Gtk.Label('Test 02'))
        self.append_page(self.page2, Gtk.Label('Titre DEUX'))

class ToDoListBox(Gtk.Box):
    """Construction de la classe"""

    def __init__(self):
        # À partir du constructeur parent :
        Gtk.Box.__init__(self)

        # Instanciation d'une grille qui recevra les éléments de l'application :
        #self.grid = Gtk.Grid()
        #self.grid.set_column_homogeneous(True)
        #self.grid.set_row_homogeneous(True)
        #self.grid.set_column_spacing(5)  # Espacement entre éléments (boutons, etc)
        #self.add(self.grid)  # Ajout de la grille à la Box maître définie par cette classe

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
        #renderer_task.connect("edited", self.on_task_edit)  # ... et cette fonction exécutée à l'édition

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

        self.add(self.scrollable_treelist)  # Ajout du conteneur scrollable à la grille
        self.set_child_packing(self.scrollable_treelist, True, True, 0, 0)

                # Si fichier de données existe : le charger, sinon proposer création :
        self.on_startup_file_load()


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


class InputWin(Gtk.Window):

    def __init__(self, title, callback):
        """Initialize simple input box window"""
        Gtk.Window.__init__(self, title=title)
        self.callback = callback

        # Paramètre de taille et esthétiques :
        self.set_size_request(300, 70)
        self.set_border_width(10)

        # Instanciation d'une boîte pour organiser les éléments créés ci-dessous :
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.add(box)  # Ajout de la boîte à la fenêtre maîtresse

        # Instanciation d'une boîte de saisie :
        self.task_entry = Gtk.Entry()
        self.task_entry.set_text("Nom du projet")  # Texte par défaut
        self.task_entry.set_property("editable", True)  # Boîte de saisie bien entendu éditable par défaut
        self.task_entry.connect("activate", self.on_create_tab)  # La touche <Entrée> lance la fonction de création
        box.pack_start(self.task_entry, True, True, 0)  # Ajout de la boîte de saisie au conteneur "box"

        # Instanciation d'un bouton permettant de valider l'entrée saisie :
        self.task_create_button = Gtk.Button("Créer")
        self.task_create_button.connect("clicked", self.on_create_tab)  # Au clic, lancer fonction de création
        box.pack_start(self.task_create_button, True, True, 1)  # Ajout du bouton au conteneur "box"

        self.show_all()

    def on_create_tab(self, button):
        """Send entry text to parent class object (here : HeaderBarWindow)"""
        self.callback(self.task_entry.get_text())  # Envoi de cette valeur à la fonction de callback définie


tdlist = []
win = HeaderBarWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
