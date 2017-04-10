#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

        self.tnotebook = TaskNoteBook()
        self.add(self.tnotebook)

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
        newpage = Gtk.Box()
        newpage.add(Gtk.Label('Nouvelle page'))
        self.tnotebook.append_page(newpage, Gtk.Label(text))
        self.tnotebook.show_all()
        self.pjr_name_input.close()
        self.tnotebook.set_current_page(-1)

    def on_del_project(self, tnotebook):
        """Remove page from notebook"""
        #TODO : insure that all tasks in page are removed too
        self.tnotebook.remove_page(self.tnotebook.get_current_page())


class TaskNoteBook(Gtk.Notebook):

    def __init__(self):
        """Initialize Notebook class instance"""
        Gtk.Notebook.__init__(self)
        self.set_border_width(3)

        # Append 2 default pages for testing purpose
        # TODO : remove second page
        self.page1 = Gtk.Box()
        self.page1.set_border_width(10)
        self.page1.add(Gtk.Label('Test 01'))
        self.append_page(self.page1, Gtk.Label('Titre test'))

        self.page2 = Gtk.Box()
        self.page2.set_border_width(10)
        self.page2.add(Gtk.Label('Test 02'))
        self.append_page(self.page2, Gtk.Label('Titre DEUX'))


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


win = HeaderBarWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
