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

        # Box receiving project management buttons :
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

        # Empty label, will receive percentage done later :
        self.percent_label = Gtk.Label()
        navbox.add(self.percent_label)
        
        # Project add/suppr buttons :
        newtab = Gtk.Button()
        img = Gtk.Image.new_from_icon_name("list-add-symbolic",
                                           Gtk.IconSize.MENU)
        newtab.set_image(img)
        newtab.connect("clicked", self.new_project_dialog)
        prjbox.add(newtab)

        deltab = Gtk.Button()
        img = Gtk.Image.new_from_icon_name("list-remove-symbolic",
                                           Gtk.IconSize.MENU)
        deltab.set_image(img)
        deltab.connect("clicked", self.on_del_project)
        prjbox.add(deltab)

        # Advanced project mgt actions in a menu :
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

        # Main container for tabbed widget (notebook) :
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.main_box)

        # Create notebook from class :
        self.tnotebook = TaskNoteBook(self.get_percent_done)
        self.main_box.add(self.tnotebook)
        self.tnotebook.popup_enable()
        self.tnotebook.set_scrollable(True)
        self.tnotebook.connect("switch-page", self.on_page_change)

        # Below notebook, add tasks management buttons box :
        self.buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.main_box.add(self.buttons_box)

        # Create tasks management buttons :
        self.buttons = list()
        for action in ["Nouvelle tâche",
                       "Supprimer",
                       "Quitter"]:
            button = Gtk.Button(action)
            self.buttons.append(button)
            # Connect them all to an action define later by on_sel_action :
            button.connect("clicked", self.on_sel_action)
        # ... except "Supprimer" (toggled by "Édition")
        self.buttons[1].disconnect_by_func(self.on_sel_action)

        # Create "Édition" mode switch:
        self.switch_label = Gtk.Label("Mode édition")
        self.switch_edit = Gtk.Switch()
        # When switch become active :
        self.switch_edit.connect("notify::active",
                                 self.on_edit_active)
        self.switch_edit.set_active(False)  # Switch not active by default

        self.buttons_box.pack_start(self.switch_label, True, True, 0)
        self.buttons_box.pack_start(self.switch_edit, True, True, 0)
        for i, button in enumerate(self.buttons):
            # Pack each button on the right :
            self.buttons_box.pack_start(self.buttons[i], True, False, 0)

        # Add task order mgt buttons :
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
        
        # As long as "Édition" mode not active,
        # some buttons remain inactive :
        self.buttons[1].set_sensitive(False)
        self.task_up.set_sensitive(False)
        self.task_down.set_sensitive(False)

        # Keyboard shortcuts :
        accel = Gtk.AccelGroup()
        accel.connect(Gdk.keyval_from_name('n'),
                Gdk.ModifierType.CONTROL_MASK,
                Gtk.AccelFlags.VISIBLE,
                self.accel_new_task)
        accel.connect(Gdk.keyval_from_name('e'),
                Gdk.ModifierType.CONTROL_MASK,
                Gtk.AccelFlags.VISIBLE,
                self.accel_edit_mode_on)
        self.add_accel_group(accel)

    def on_page_next(self, tnotebook):
        """Switch to next tab"""
        self.tnotebook.next_page()

    def on_page_prev(self, tnotebook):
        """Switch to previous tab"""
        self.tnotebook.prev_page()

    def new_project_dialog(self, tnotebook):
        """Launch project creation dialog : 
        initialize input window with 'on_new_tab' as callback function"""
        self.pjr_name_input = InputWin("Nouveau projet", self.on_new_tab)
        self.pjr_name_input.show()
        # TODO : check name length, if == 0, refuse to create project...
        # TODO : as file creation will fail

    def on_new_tab(self, text):
        """Create a new page from TodoListBox class,
        name is set from project creation dialog"""
        newpage = ToDoListBox()
        self.tnotebook.append_page(newpage, Gtk.Label(text))
        self.tnotebook.show_all()
        self.pjr_name_input.close()
        self.tnotebook.set_current_page(-1)
        # When project is created and named, create its file on disk :
        newpage.project_name = self.tnotebook.get_tab_label_text(newpage)
        newpage.on_save_list(newpage.project_name)

    def rename_prj_dialog(self, tnotebook):
        """Open InputWin class instance to rename project,
        on_rename_project will be called to actually change
        project tab label text"""
        self.new_name_input = InputWin("Renommer le projet « " +
                                           self.get_project_name() + " »",
                                           self.on_rename_project)

    def on_rename_project(self, text):
        """Change tab label (rename project)"""
        os.rename(share_dir + "/" + self.get_project_name(),
                  share_dir + "/" + text)
        self.tnotebook.set_tab_label_text(self.get_current_child(), text)
        self.new_name_input.close()

    def on_save_notebook(self, widget):
        """Save current (with focus) list"""
        # TODO : on_save_notebook should save ALL pages
        self.get_current_child().on_save_list(self.get_project_name())

    def get_percent_done(self, **kwargs):
        """Calculate percentage of done tasks
        based on presence of 'True' in project file content"""
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
            # Remove project file from disk :
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

    def on_edit_active(self, switch, gparam, *args):
        """ What to do when edit switch becomes active """
        if self.switch_edit.get_active():  # If switch becomes active...
            # ...make "Supprimer" button active...
            self.buttons[1].connect("clicked", self.on_sel_action)
            self.buttons[1].set_sensitive(True)
            self.task_up.set_sensitive(True)
            self.task_down.set_sensitive(True)
            # ...and allow rows (i.e taks) muose selection :
            self.get_current_child().sel.set_mode(Gtk.SelectionMode.SINGLE)
        else:  # If switch becomes inactive, forbid selection...
            # and deactivate "Supprimer" button :
            #~ self.buttons[1].disconnect_by_func(self.on_sel_action)
            self.get_current_child().sel.set_mode(Gtk.SelectionMode.NONE)
            self.buttons[1].set_sensitive(False)
            self.task_up.set_sensitive(False)
            self.task_down.set_sensitive(False)

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
        """Define action to perform on keyboard shortcut,
        here Ctrl + n launches task creation in active page list"""
        self.get_current_child().on_launch_creation(
                self.get_project_name())
                
    def accel_edit_mode_on(self, *args):
        """On keyboard shortcut, toggle switch state,
        this will activate edit mode"""
        if self.switch_edit.get_active() == False:
            self.switch_edit.set_active(True)
        else:
            self.switch_edit.set_active(False)

class TaskNoteBook(Gtk.Notebook):
    """ Initialize custom Notebook class instance """

    def __init__(self, callback):
        Gtk.Notebook.__init__(self)
        self.set_border_width(3)

        # If there is no project file in app data dir, create empty project
        # and create its file on disk :
        if len(os.listdir(share_dir)) == 0:
            self.page1 = ToDoListBox(callback)
            self.append_page(self.page1, Gtk.Label('Nouveau projet'))
            self.page1.on_save_list('Nouveau projet')
        else:
            # Otherwise load project files in newly created pages :
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
        Gtk.Box.__init__(self)

        self.callback_percent = callback
        # Create tasks list and declare its future content :
        self.tdlist_store = Gtk.ListStore(bool, str)
        for tache in tdlist:
            self.tdlist_store.append([False, tache])
        self.current_filter_language = None

        # Create a treeview from tasks list :
        self.tdview = Gtk.TreeView(model=self.tdlist_store)

        # Create "task done" check box :
        renderer_check = Gtk.CellRendererToggle()
        renderer_check.connect("toggled", self.on_task_check)
        # Create check boxes column...
        column_check = Gtk.TreeViewColumn("Finie", renderer_check,
                                          active=0)
        # ... and add it to the treeview :
        self.tdview.append_column(column_check)

        # Create "task name" cells...
        renderer_task = Gtk.CellRendererText()
        # ... make them editable...
        renderer_task.set_property("editable", True)
        # ... and launch 'on_task_edit' when edited :
        renderer_task.connect("edited", self.on_task_edit)
        # Create tasks name column...
        self.column_task = Gtk.TreeViewColumn("Description de la tâche",
                                              renderer_task, text=1)
        self.column_task.set_sort_column_id(1)  # Cette colonne sera triable.
        # ... and add it to the treeview :
        self.tdview.append_column(self.column_task)

        # By default, we can't select cells
        # (only active Selection mode allows it) :
        self.sel = self.tdview.get_selection()
        self.sel.set_mode(Gtk.SelectionMode.NONE)

        # Create a scrollable container that will receive the treeview :
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.scrollable_treelist.set_border_width(5)
        self.scrollable_treelist.add(self.tdview)
        # Add this container to the todo list box :
        self.add(self.scrollable_treelist)
        self.set_child_packing(self.scrollable_treelist, True, True, 0, 0)

    def on_startup_file_load(self, project_name):
        """On app launch, load project file and format entries"""
        if not os.path.exists(share_dir):
            os.makedirs(share_dir, mode=0o775)
        # If file is empty, there's no need to load it :
        if os.path.getsize(share_dir + "/" + project_name) == 0:
            pass
        else:
            # If it exists, load its entries into self.tdlist_store :
            file_len, c = 0, 0
            with open(share_dir + "/" + project_name, 'r') as file_in:
                for line in file_in:
                    file_len += 1
                    line = line.strip().split(',')
                    # Format tasks name and append them to treestore :
                    entry = (str(line[0]).strip(','),
                                     str(' '.join(line[1:])))
                    self.tdlist_store.append(entry)
                    # Restore check boxes state according to line[0] content :
                    if entry[0] == "False":
                        iter = self.tdlist_store.get_iter(c)
                        self.tdlist_store.set_value(iter, 0, False)
                    c += 1

    def on_task_check(self, widget, path):
        """What to do when checkbox is un/activated"""
        # Toggle check box state :
        self.tdlist_store[path][0] = not self.tdlist_store[path][0]
        self.callback_percent()

    def on_task_edit(self, widget, path, text):
        """What to do when cell (task) is edited"""
        self.tdlist_store[path][1] = text

    def on_save_list(self, project_name):
        """Save list in a project named file,
        tasks are written row by row in file, line by line"""
        with open(share_dir + "/" + project_name, 'w') as file_out:
            for row in self.tdlist_store:
                file_out.write(str(row[0]) + ',' + str(''.join(row[1])) + "\n")

    def on_task_up(self):
        """Move selected task up"""
        selection = self.tdview.get_selection()
        self.tdlist_store, paths = selection.get_selected_rows()
        # Get selected task treeiter :
        for path in paths:
            iter = self.tdlist_store.get_iter(path)
        # And move it before the previous iter :
        self.tdlist_store.move_before(iter,
                self.tdlist_store.iter_previous(iter))

    def on_task_down(self):
        """Move selected task up"""
        selection = self.tdview.get_selection()
        self.tdlist_store, paths = selection.get_selected_rows()
        # Get selected task treeiter :
        for path in paths:
            iter = self.tdlist_store.get_iter(path)
        # And move it after the next iter :
        self.tdlist_store.move_after(iter,
                self.tdlist_store.iter_next(iter))

    def on_row_delete(self):
        """Select line and remove it"""
        # Get selected row coordinates
        # (as a tuple(ListStore, "row path")) :
        selection = self.tdview.get_selection()
        self.tdlist_store, paths = selection.get_selected_rows()
        # Get selected task (row) treeiter :
        for path in paths:
            iter = self.tdlist_store.get_iter(path)
        # And remove it :
        self.tdlist_store.remove(iter)

    def on_launch_creation(self, parent_project):
        """Show input box to create new task
        defined by 'project_name'. The new task will be
        created by the callback function"""
        self.ta = InputWin("Créer une nouvelle tâche dans « " + parent_project
                           + " »", self.on_create_new)
        self.ta.show()

    def on_create_new(self, text):
        """Append task at the end of ListStore"""
        self.tdlist_store.insert_with_valuesv(-1, [1], [text])
        self.ta.close()


class InputWin(Gtk.Window):
    """Initialize a generic input box window"""

    def __init__(self, title, callback):
        Gtk.Window.__init__(self, title=title)
        self.callback = callback

        # Inputbox size params :
        self.set_size_request(500, 70)
        self.set_border_width(10)

        # Create main container:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.add(box)

        # Create input box :
        self.object_entry = Gtk.Entry()
        self.object_entry.set_text("Nouvel élément")
        # Make inputbox editable :
        self.object_entry.set_property("editable", True)
        # Allow <Entrée> button to launch action :
        self.object_entry.connect("activate", self.on_create_object)
        box.pack_start(self.object_entry, True, True, 0)

        # This button launch the action :
        self.object_create_button = Gtk.Button("Créer")
        self.object_create_button.connect("clicked", self.on_create_object)
        box.pack_start(self.object_create_button, True, True, 1)

        self.show_all()

    def on_create_object(self, button):
        """Send entry text to parent class object (here : HeaderBarWindow)
        callback function"""
        self.callback(self.object_entry.get_text())


class ConfirmDialog(Gtk.Dialog):
    """A generic yes/no dialog"""

    def __init__(self, parent, label):
        Gtk.Dialog.__init__(self, "Confirmation", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        # Dialog box size params :
        self.set_default_size(150, 80)
        # Label text is set by parent calling function :
        self.label = Gtk.Label(label)
        box = self.get_content_area()
        box.set_border_width(10)
        box.add(self.label)

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
