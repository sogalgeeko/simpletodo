#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class HeaderBarWindow(Gtk.Window):
    """ Initialize window with HeaderBar """

    def __init__(self):
        Gtk.Window.__init__(self, title="Simple Todo")
        self.set_border_width(10)
        self.set_default_size(650, 380)
        # self.set_icon_from_file(
        # "/home/sogal/Projets/simpletodo/simpletodo.png")
        self.set_icon_name("gtg")

        headerb = Gtk.HeaderBar()
        headerb.set_show_close_button(True)
        headerb.props.title = "Simple Todo"
        self.set_titlebar(headerb)

        # Ajout de box destinées recevant les boutons de gestion des projets :
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

        self.percent_label = Gtk.Label()
        navbox.add(self.percent_label)

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

        prj_menu = Gtk.MenuButton()
        prj_menu_img = Gtk.Image.new_from_icon_name("open-menu-symbolic",
                                                Gtk.IconSize.BUTTON)
        prj_menu.add(prj_menu_img)
        menu_entries = Gtk.Menu()
        i1 = Gtk.MenuItem("Renommer...")
        i1.connect("activate", self.rename_prj_dialog)
        i2 = Gtk.MenuItem("Enregistrer")
        i2.connect("activate", self.on_save_notebook)
        menu_entries.append(i1)
        menu_entries.append(i2)
        menu_entries.show_all()
        prj_menu.set_popup(menu_entries)
        prj_menu.show_all()
        prjbox.add(prj_menu)

        headerb.pack_start(navbox)
        headerb.pack_end(prjbox)

        # Conteneur principal recevant le widget à onglet :
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.main_box)

        # Ajout du widget à onglet :
        self.tnotebook = TaskNoteBook(self.get_percent_done)
        self.main_box.add(self.tnotebook)
        self.tnotebook.popup_enable()
        self.tnotebook.set_scrollable(True)
        self.tnotebook.connect("switch-page", self.on_page_change)

        # En dessous, ajout de la box pour boutons de contrôle :
        self.buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.main_box.add(self.buttons_box)

        # Création séquentielle des boutons :
        self.buttons = list()
        for action in ["Nouvelle tâche",
                       "Supprimer",
                       "Quitter"]:
            button = Gtk.Button(action)
            self.buttons.append(button)
            # Connexion des boutons à la fonc. de sélection des actions
            button.connect("clicked", self.on_sel_action)
        # ... sauf "Supprimer" (activé par le mode "Édition")
        self.buttons[1].disconnect_by_func(self.on_sel_action)
        self.buttons[1].set_sensitive(False)

        # Instanciation du label du switch du mode "Édition" :
        self.switch_label = Gtk.Label("Mode édition")
        # Instanciation du switch lui-même :
        self.switch_edit = Gtk.Switch()
        # Lorsque actif, lancer la fonction
        self.switch_edit.connect("notify::active",
                                 self.on_edit_active)
        self.switch_edit.set_active(False)  # Switch inactif par défaut

        self.buttons_box.pack_start(self.switch_label, True, True, 0)
        self.buttons_box.pack_start(self.switch_edit, True, True, 0)
        for i, button in enumerate(self.buttons):
            # Ajout successif des autres boutons à droite du 1er
            self.buttons_box.pack_start(self.buttons[i], True, False, 0)

        self.task_up = Gtk.Button()
        img = Gtk.Image.new_from_icon_name("go-up-symbolic",
                Gtk.IconSize.BUTTON)
        self.task_up.set_image(img)
        self.task_up.connect("clicked", self.on_sel_action)
        self.buttons_box.pack_start(self.task_up, True, True, 0)
        self.task_down = Gtk.Button()
        img = Gtk.Image.new_from_icon_name("go-down-symbolic",
                Gtk.IconSize.BUTTON)
        self.task_down.set_image(img)
        self.task_down.connect("clicked", self.on_sel_action)
        self.buttons_box.pack_start(self.task_down, True, True, 0)

        # Keyboard shortcuts :
        accel = Gtk.AccelGroup()
        accel.connect(Gdk.keyval_from_name('o'),
                Gdk.ModifierType.CONTROL_MASK,
                Gtk.AccelFlags.VISIBLE,
                self.accel_new_task)
        self.add_accel_group(accel)

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
        # Créer une instance de todolist :
        newpage = ToDoListBox()
        self.tnotebook.append_page(newpage, Gtk.Label(text))
        self.tnotebook.show_all()
        self.pjr_name_input.close()
        self.tnotebook.set_current_page(-1)
        # Dès la création de la nouvelle todolist, créer son fichier :
        newpage.project_name = self.tnotebook.get_tab_label_text(newpage)
        newpage.on_save_list(newpage.project_name)

    def rename_prj_dialog(self, tnotebook):
        self.new_name_input = InputWin("Renommer le projet « " +
                                           self.get_project_name() + " »",
                                           self.on_rename_project)

    def on_rename_project(self, text):
        """Change page label (rename project)"""
        os.rename(share_dir + "/" + self.get_project_name(),
                  share_dir + "/" + text)
        self.tnotebook.set_tab_label_text(self.get_current_child(), text)
        self.new_name_input.close()

    def on_save_notebook(self, widget):
        self.get_current_child().on_save_list(self.get_project_name())

    def get_percent_done(self, **kwargs):
        """Calculate percentage of done tasks
        based on presence of 'True' in project file"""
        project_name = self.get_project_name()
        self.get_current_child().on_save_list(project_name)
        tasks_list = []
        tasks_total = 0
        with open(share_dir + "/" + project_name, 'r') as file:
            for line in file:
                tasks_total += 1
                line = line.strip().split(',')
                tasks_list.append(line)
        tasks_done = 0
        for i in tasks_list:
            tasks_done += i.count('True')

        percent_done = int(tasks_done * 100 / tasks_total)
        self.percent_label.set_text(str(percent_done) + "%")

    def on_del_project(self, tnotebook):
        """Remove page from notebook"""
        dialog = ConfirmDialog(self, "Supprimer le projet « " +
                               self.get_project_name() + " » ?")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # Supprimer le fichier contenant le projet :
            os.remove(share_dir + "/" + self.get_project_name())
            self.tnotebook.remove_page(self.tnotebook.get_current_page())
            if len(os.listdir(share_dir)) == 0:
                self.tnotebook.page1 = ToDoListBox()
                self.tnotebook.append_page(self.tnotebook.page1, Gtk.Label(
                    'Nouveau projet'))
                self.tnotebook.page1.on_save_list('Nouveau projet')
                self.tnotebook.show_all()
            dialog.destroy()
        else:
            dialog.destroy()

    def get_project_name(self):
        """Returns the project name"""
        page_index = self.tnotebook.get_current_page()
        child = self.tnotebook.get_nth_page(page_index)
        return str(self.tnotebook.get_tab_label_text(child))

    def get_current_child(self):
        """ Returns the current todolist """
        page_index = self.tnotebook.get_current_page()
        return self.tnotebook.get_nth_page(page_index)

    def on_sel_action(self, widget):
        """ Launch action depending on clicked button """
        project_name = self.get_project_name()
        if widget.get_label() == "Nouvelle tâche":
            self.get_current_child().on_launch_creation(
                self.get_project_name())
            self.get_percent_done()
        elif widget.get_label() == "Supprimer":
            self.get_current_child().on_row_delete()
        elif widget.get_label() == "Quitter":
            self.get_current_child().on_save_list(project_name)
            Gtk.main_quit()
        elif widget == self.task_up:
            self.get_current_child().on_task_up()
        elif widget == self.task_down:
            self.get_current_child().on_task_down()

    def on_edit_active(self, switch, gparam):
        """ What to do when edit switch becomes active """
        if self.switch_edit.get_active():  # Si le switch devient actif...
            # ...rendre le bouton "Supprimer" actif...
            self.buttons[1].connect("clicked", self.on_sel_action)
            self.buttons[1].set_sensitive(True)
            # ...et permettre la sélection des "rows" (des tâches donc)
            self.get_current_child().sel.set_mode(Gtk.SelectionMode.SINGLE)
        else:  # S'il devient inactif interdire la sélection
            self.buttons[1].disconnect_by_func(self.on_sel_action)
            self.get_current_child().sel.set_mode(Gtk.SelectionMode.NONE)
            self.buttons[1].set_sensitive(False)

    def on_page_change(self, notebook, page, page_num):
        """If edit switch is active then all todolists can be edited"""
        if self.switch_edit.get_active():
            notebook.get_nth_page(page_num).sel.set_mode(
                Gtk.SelectionMode.SINGLE)
        else:
            notebook.get_nth_page(page_num).sel.set_mode(
                Gtk.SelectionMode.NONE)
        self.percent_label.set_text("")

    def accel_new_task(self, *args):
        self.get_current_child().on_launch_creation(
                self.get_project_name())


class TaskNoteBook(Gtk.Notebook):
    """ Initialize custom Notebook class instance """

    def __init__(self, callback):
        Gtk.Notebook.__init__(self)
        self.set_border_width(3)

        # Si aucun projet n'existe, en démarrer un vierge :
        if len(os.listdir(share_dir)) == 0:
            self.page1 = ToDoListBox(callback)
            self.append_page(self.page1, Gtk.Label('Nouveau projet'))
            self.page1.on_save_list('Nouveau projet')
        else:
            # Si oui, les charger chacun dans un onglet :
            for file in os.listdir(share_dir):
                self.newpage = ToDoListBox(callback)
                self.append_page(self.newpage, Gtk.Label(file))
                self.show_all()
                self.newpage.on_startup_file_load(file)
                self.next_page()
                self.set_tab_reorderable(self.newpage, True)


class ToDoListBox(Gtk.Box):
    """ Create a box that will contain tasks """

    def __init__(self, callback):
        # À partir du constructeur parent :
        Gtk.Box.__init__(self)

        self.callback_percent = callback
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

        # Colonne contenant les cellules de cases à cocher :
        column_check = Gtk.TreeViewColumn("Finie", renderer_check,
                                          active=0)
        # Ajout de cette colonne à la vue "tdview" créée précédemment :
        self.tdview.append_column(column_check)

        # Instanciation des cellules recevant les tâches :
        renderer_task = Gtk.CellRendererText()
        # Ces cellules seront éditables...
        renderer_task.set_property("editable", True)
        # ... et cette fonction exécutée à l'édition
        renderer_task.connect("edited", self.on_task_edit)

        # Instanciation d'une colonne recevant les cellules des tâches :
        self.column_task = Gtk.TreeViewColumn("Description de la tâche",
                                              renderer_task, text=1)
        self.column_task.set_sort_column_id(1)  # Cette colonne sera triable.
        # Ajout de cette colonne à la vue "tdview" créée précédemment :
        self.tdview.append_column(self.column_task)

        # Par défaut les cellules ne seront pas sélectionnables
        # (le mode "Édition" le permettra) :
        self.sel = self.tdview.get_selection()
        self.sel.set_mode(Gtk.SelectionMode.NONE)

        # Instanciation d'un conteneur (fenêtre) scrollable
        # qui recevra la vue "tdview" :
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.scrollable_treelist.set_border_width(5)
        # Ainsi on peut scroller dans la vue "liste des tâches" (tdview)
        self.scrollable_treelist.add(self.tdview)

        # Ajout du conteneur scrollable à la grille
        self.add(self.scrollable_treelist)
        self.set_child_packing(self.scrollable_treelist, True, True, 0, 0)

    def on_startup_file_load(self, project_name):
        """On app launch, load project file and format entries"""
        if not os.path.exists(share_dir):
            os.makedirs(share_dir, mode=0o775)
        if not os.path.exists(share_dir + "/" + project_name):
            # S'il n'existe pas, un dialogue propose sa création
            self.tdfile_creation_dialog()
        # Si le fichier est vide (taille == 0 ), ne pas chercher à le charger :
        elif os.path.getsize(share_dir + "/" + project_name) == 0:
            pass
        else:
            # S'il existe, l'ouvrir et ajouter ses entrées à self.tdlist_store
            # :
            with open(share_dir + "/" + project_name, 'r') as file_in:
                for i, l in enumerate(file_in):
                    pass
            file_len = i + 1
            with open(share_dir + "/" + project_name, 'r') as file_in:
                c = 0
                while c < file_len:
                    entry = file_in.readline().split()
                    # Formatage de l'entrée avant ajout au ListStore :
                    cleaned_entry = (str(entry[0]).strip(','),
                                     str(' '.join(entry[1:])))
                    # print(str(entry[0]).strip(','))
                    self.tdlist_store.append(cleaned_entry)
                    # Bidouille pour que les cases à cocher
                    # retrouvent leur état précédent :
                    # Si l'état = à False (mal formaté)...
                    if entry[0] == "False,":
                        # ... récupérer l'adresse du "row" en cours d'édition
                        iter = self.tdlist_store.get_iter(c)
                        # ... récup la valeur de la 1ère colonne
                        # state = self.tdlist_store.get_value(iter, 0)
                        # ... et la définir à False (bien formaté)
                        self.tdlist_store.set_value(iter, 0, False)
                    c += 1

    def on_task_check(self, widget, path):
        """What to do when checkbox is un/activated"""
        # Inverser l'état de la case
        self.tdlist_store[path][0] = not self.tdlist_store[path][0]
        self.callback_percent()

    def on_task_edit(self, widget, path, text):
        """What to do when cell (task) is edited"""
        self.tdlist_store[path][1] = text

    def on_save_list(self, project_name):
        """Save list in a project named file"""
        file_out = open(share_dir + "/" + project_name, 'w')
        for row in self.tdlist_store:
            # Ajout d'un retour à la ligne pour obtenir un fichier ligne à
            # ligne
            file_out.write(str(row[0]) + ", " + str(''.join(row[1])) + "\n")
        file_out.close()

    def on_task_up(self):
        """Move selected task up"""
        selection = self.tdview.get_selection()
        self.tdlist_store, paths = selection.get_selected_rows()

        # Obtenir le "TreeIter" des "rows" sélectionnés :
        for path in paths:
            iter = self.tdlist_store.get_iter(path)

        # Déplacement :
        self.tdlist_store.move_before(iter,
                self.tdlist_store.iter_previous(iter))

    def on_task_down(self):
        """Move selected task up"""
        selection = self.tdview.get_selection()
        self.tdlist_store, paths = selection.get_selected_rows()

        # Obtenir le "TreeIter" des "rows" sélectionnés :
        for path in paths:
            iter = self.tdlist_store.get_iter(path)

        # Déplacement :
        self.tdlist_store.move_after(iter,
                self.tdlist_store.iter_next(iter))

    def on_row_delete(self):
        """Select line and remove it"""
        # Obtenir "l'adresse" de(s) "row(s)" sélectionnés
        # (sous forme d'un tuple(ListStore, "path" du "row")) :
        selection = self.tdview.get_selection()
        self.tdlist_store, paths = selection.get_selected_rows()

        # Obtenir le "TreeIter" des "rows" sélectionnés :
        for path in paths:
            iter = self.tdlist_store.get_iter(path)

        # Et on supprime le "row" référencé par l'iter obtenu :
        self.tdlist_store.remove(iter)

    def on_launch_creation(self, parent_project):
        """Show input box to create new task"""
        # Instanciation d'un objet de la classe "InputWin"
        # et définition de sa fonction de callback
        self.ta = InputWin("Créer une nouvelle tâche dans « " + parent_project
                           + " »", self.on_create_new)
        self.ta.show()

    def on_create_new(self, text):
        """Append task to ListStore"""
        # L'objet de création de tâche renvoie une valeur
        # qu'on ajoute en fin du ListStore :
        self.tdlist_store.insert_with_valuesv(-1, [1], [text])
        self.ta.close()


class InputWin(Gtk.Window):
    """Initialize a generic input box window"""

    def __init__(self, title, callback):
        Gtk.Window.__init__(self, title=title)
        self.callback = callback

        # Paramètre de taille et esthétiques :
        self.set_size_request(500, 70)
        self.set_border_width(10)

        # Instanciation d'une boîte organisant les éléments créés ci-dessous :
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.add(box)  # Ajout de la boîte à la fenêtre maîtresse

        # Instanciation d'une boîte de saisie :
        self.object_entry = Gtk.Entry()
        self.object_entry.set_text("Nouvel élément")  # Texte par défaut
        # Boîte de saisie bien entendu éditable par défaut
        self.object_entry.set_property("editable", True)
        # La touche <Entrée> lance la fonction de création :
        self.object_entry.connect("activate", self.on_create_object)
        # Ajout de la boîte de saisie au conteneur "box" :
        box.pack_start(self.object_entry, True, True, 0)

        # Instanciation d'un bouton permettant de valider l'entrée saisie :
        self.object_create_button = Gtk.Button("Créer")
        # Au clic, lancer fonction de création
        self.object_create_button.connect("clicked", self.on_create_object)
        # Ajout du bouton au conteneur "box"
        box.pack_start(self.object_create_button, True, True, 1)

        self.show_all()

    def on_create_object(self, button):
        """Send entry text to parent class object (here : HeaderBarWindow)"""
        # Envoi de cette valeur à la fonction de callback définie
        self.callback(self.object_entry.get_text())


class ConfirmDialog(Gtk.Dialog):
    """A generic yes/no dialog"""

    def __init__(self, parent, label):
        # Instantiation du modèle depuis la classe parente :
        Gtk.Dialog.__init__(self, "Confirmation", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        # Paramètres de taille par défaut :
        self.set_default_size(150, 80)

        # Ajouter label défini par la fonction appelante :
        self.label = Gtk.Label(label)

        # Box = le contenu du widget dialog :
        box = self.get_content_area()
        box.set_border_width(10)  # Pour faire plus joli
        box.add(self.label)  # Ajout du label

        self.show_all()


tdlist = []
share_dir = os.path.expanduser('~/.local/share/simpletodo')
if not os.path.isdir(share_dir):
    os.mkdir(share_dir)
win = HeaderBarWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

sys.exit(0)
