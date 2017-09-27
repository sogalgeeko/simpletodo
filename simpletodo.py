#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio


class HeaderBarWindow(Gtk.ApplicationWindow):
    """ Initialize window with HeaderBar """

    def __init__(self, *args, **kwargs):
        super().__init__(title="Simple Todo", *args, **kwargs)

        self.set_size_request(850, 530)
        self.set_icon_name("simpletodo")

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
        self.percent_label.set_margin_start(5)
        navbox.add(self.percent_label)

        # Project add/suppr buttons :
        newtab = Gtk.Button()
        img = Gtk.Image.new_from_icon_name("list-add-symbolic",
                                           Gtk.IconSize.MENU)
        newtab.set_image(img)
        prjbox.add(newtab)
        # Popover for new project creation dialog :
        self.newtab_popover = Gtk.Popover()
        self.newtab_popover.set_relative_to(headerb)
       # Create main container:
        newproject_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, 
                                        spacing=5, border_width=5)
        newproject_box.set_size_request(240, -1)
        self.newtab_popover.add(newproject_box)
        # Create input box :
        self.newproject_entry = Gtk.Entry()
        self.newproject_entry.set_text("Nouvel élément")
        # Make inputbox editable :
        self.newproject_entry.set_property("editable", True)
        # Allow <Entrée> button to launch action :
        self.newproject_entry.connect("activate", self.on_project_new,)
        newproject_box.pack_start(self.newproject_entry, True, True, 0)
        # This button launch the project creation function :
        self.newproject_create_button = Gtk.Button("Créer")
        self.newproject_create_button.connect("clicked", self.on_project_new)
        newproject_box.pack_start(self.newproject_create_button, True, True, 1)
        # Connect newtab button to "show popover" function :
        newtab.connect("clicked", self.on_visible_toggle, 
                                        self.newtab_popover,
                                        self.newproject_entry)
        # Tab removal button :
        deltab = Gtk.Button()
        img = Gtk.Image.new_from_icon_name("list-remove-symbolic",
                                           Gtk.IconSize.MENU)
        deltab.set_image(img)
        deltab.connect("clicked", self.on_project_delete)
        prjbox.add(deltab)

        # Advanced project mgt actions in a menu :
        self.prj_menu = Gtk.Button()
        prj_menu_img = Gtk.Image.new_from_icon_name("open-menu-symbolic",
                                                    Gtk.IconSize.BUTTON)
        self.prj_menu.add(prj_menu_img)
        prjbox.add(self.prj_menu)

        # Define popover :
        self.menu_popover = Gtk.PopoverMenu()
        self.menu_popover.set_modal(True)
        # Make it relative to "menu" button :
        self.menu_popover.set_relative_to(self.prj_menu)
        # Create a box that will go inside the popover :
        popover_box = Gtk.Box(border_width=5)
        popover_box.set_spacing(5)
        popover_box.set_orientation(Gtk.Orientation.VERTICAL)

        # Put all necessary buttons in the box :
        # Create a box for renaming widgets :
        rename_popover_box = Gtk.Grid(border_width=5, 
                                        row_spacing = 5,
                                        column_spacing=5)
        # Add "go back" widget :
        go_back0 = Gtk.ModelButton()
        go_back0.props.text = "Retour"
        go_back0.props.inverted = True
        go_back0.props.centered = True
        go_back0.props.menu_name = "main"
        rename_popover_box.attach(go_back0, 0, 0, 2, 1)
        # Add it renaming widgets :
        self.rename_prj_entry = Gtk.Entry()
        rename_button = Gtk.Button.new_with_label("Ok")
        rename_button.connect("clicked", self.on_project_rename)
        rename_popover_box.attach(self.rename_prj_entry, 0, 1, 1, 1)
        rename_popover_box.attach(rename_button, 1, 1, 1, 1)
        # Add button in the parent popover :
        rename_to_button = Gtk.ModelButton()
        rename_to_button.props.text = "Renommer en..."
        # Link it to the rename_popover_box :
        rename_to_button.props.menu_name = "rename_popover_box"
        rename_to_button.set_relief(2)
        rename_to_button.props.centered = False
        popover_box.add(rename_to_button)
      
        # Define box to be shown in slided popover :
        clone_name_box = Gtk.Grid(border_width=5, 
                                        row_spacing = 5,
                                        column_spacing=5)
        # Add "go back" widget :
        go_back1 = Gtk.ModelButton()
        go_back1.props.text = "Retour"
        go_back1.props.inverted = True
        go_back1.props.centered = True
        go_back1.props.menu_name = "main"
        clone_name_box.attach(go_back1, 0, 0, 2, 1)
        # Added cloning widgets :
        self.clone_name_entry = Gtk.Entry()
        self.clone_name_entry.set_text("Nom du projet cloné")
        clone_name_button = Gtk.Button.new_with_label("Ok")
        clone_name_button.connect("clicked", self.on_project_clone)
        clone_name_box.attach(self.clone_name_entry, 0, 1, 1, 1)
        clone_name_box.attach(clone_name_button, 1, 1, 1, 1)
        
        # Add button that will show submenu :
        clone_to_button = Gtk.ModelButton.new()
        # And set the name of the widget it will slides to :
        clone_to_button.props.menu_name = "clone_name_box"
        # Set its properties :
        clone_to_button.props.text = "Cloner vers..."
        clone_to_button.set_relief(2)
        clone_to_button.props.centered = False
        popover_box.add(clone_to_button)
        
        # Add the clone and renaming box to the popover, not directly but... :
        self.menu_popover.add(clone_name_box)
        self.menu_popover.add(rename_popover_box)
        # ... in a submenu :
        self.menu_popover.child_set_property(clone_name_box, "submenu", "clone_name_box")
        self.menu_popover.child_set_property(rename_popover_box, "submenu", "rename_popover_box")
        
        # Add other buttons :
        for button_label, action in zip(("Enregistrer",
                             "À propos"), (self.on_save_all,
                                            AboutDialog)):
            b = Gtk.ModelButton.new()
            b.props.text = str(button_label)
            b.set_relief(2)
            b.props.centered = False
            b.connect("clicked", action)
            popover_box.add(b)

        # Add the box inside the popover :
        self.menu_popover.add(popover_box)
        self.prj_menu.connect("clicked", self.on_visible_toggle,
                                            self.menu_popover,
                                            None)

        headerb.pack_start(navbox)
        headerb.pack_end(prjbox)

        # Main container for tabbed widget (notebook) :
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.main_box)
        
        # Add horizontal container for sidebar revealer and notebook :
        self.overlay = Gtk.Overlay()
        self.main_box.add(self.overlay)
        
        # Create notebook from class :
        self.tnotebook = TaskNoteBook(self.update_percent_on_check)
        self.tnotebook.set_hexpand(True)
        self.tnotebook.set_border_width(5)
        self.tnotebook.set_size_request(550, -1)
        self.tnotebook.popup_enable()
        self.tnotebook.set_scrollable(True)
        self.tnotebook.connect("switch-page", self.update_percent_on_change)
        self.overlay.add(self.tnotebook)

        # Create revealer :
        self.sidebar = Gtk.Revealer()
        self.sidebar.set_margin_bottom(5)
        self.sidebar.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
        self.sidebar.set_transition_duration(10000)
        self.sidebar.set_reveal_child(True)
        self.sidebar.set_vexpand(True)
        self.sidebar.set_valign(Gtk.Align.FILL)
        self.sidebar.set_halign(Gtk.Align.START)
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.override_background_color(0, Gdk.RGBA(
                                red=0.1, green=0.1, blue=0.1, alpha=0.9))
        self.sidebar.add(sidebar_box)
        self.t = NewTaskWin()
        self.t.set_vexpand(True)
        # This button trigger the task creation process :
        self.new_task_button = Gtk.Button(label="Créer",
                                            margin_left=5,
                                            margin_right=5,
                                            margin_bottom=5)
        self.new_task_button.connect("clicked", self.launch_task_creation)
        sidebar_box.add(self.t)
        sidebar_box.add(self.new_task_button)
        self.overlay.add_overlay(self.sidebar)
        
        # Below notebook, add tasks management buttons box :
        self.buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                    margin_left=5,
                                    margin_bottom=5,
                                    margin_right=5,
                                    spacing=5)
        self.main_box.add(self.buttons_box)

        # Create tasks mgt menu:
        tasks_menu_button = Gtk.Button()
        tasks_menu_icon = Gtk.Image.new_from_icon_name("view-more-symbolic",
                                                       Gtk.IconSize.BUTTON)
        tasks_menu_button.add(tasks_menu_icon)
        self.buttons_box.pack_start(tasks_menu_button, False, True, 0)

        # Define popover :
        self.tasks_menu_popover = Gtk.Popover()
        # Make it relative to "menu" button :
        self.tasks_menu_popover.set_relative_to(tasks_menu_button)
        # Create a box that will go inside the popover :
        popover_box = Gtk.Box(border_width=5)
        popover_box.set_spacing(5)
        popover_box.set_orientation(Gtk.Orientation.VERTICAL)
        # Put all necessary buttons in the box :
        for button_label, state in zip(("Cocher tous", "Décocher tous",
                                         "Inverser tous"),
                                        (True, False, "Toggle")):
            b = Gtk.ModelButton.new()
            b.props.text = str(button_label)
            b.set_relief(2)
            b.props.centered = False
            b.connect("clicked", self.launch_tasks_check_all, state)
            popover_box.add(b)
        # Add the box inside the popover :
        self.tasks_menu_popover.add(popover_box)
        tasks_menu_button.connect("clicked",
                                  self.on_visible_toggle,
                                  self.tasks_menu_popover, None)

        # Create tasks management buttons :
        self.buttons = []
        for i, icon in enumerate(["list-add-symbolic",
                                  "list-remove-symbolic",
                                  "go-up-symbolic",
                                  "go-down-symbolic"]):
            img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
            button = Gtk.Button()
            self.buttons.append(button)
            self.buttons[i].set_image(img)
            # Connect them all to an action define later by on_sel_action :
            button.connect("clicked", self.on_sel_action)

        # Pack check_all/uncheck_all buttons on the left :
        for i, button in enumerate(self.buttons):
            self.buttons_box.pack_start(self.buttons[i], False, True, 0)


        # Create ComboxBox of target to move selected task to :
        projects_list_button = Gtk.Button.new_with_label("Déplacer vers")
        projects_list_button.set_margin_start(5)
        # Define popover for projects list (task move) :
        self.prj_popover = Gtk.Popover()
        self.prj_popover.set_relative_to(projects_list_button)
        self.projects_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        for project_name in os.listdir(share_dir):
            rbx = Gtk.ToggleButton(project_name, relief=Gtk.ReliefStyle.NONE,
                                    halign=Gtk.Align.START)
            rbx.connect("toggled", self.launch_task_move, project_name)
            self.projects_list_box.add(rbx)
        self.prj_popover.add(self.projects_list_box)
        self.buttons_box.pack_end(projects_list_button, False, True, 0)
        projects_list_button.connect("clicked",
                                        self.on_visible_toggle,
                                        self.prj_popover,
                                        self.projects_list_box)

        # Add tooltips to buttons that use icon :
        tasks_menu_button.set_tooltip_text("Gérer les tâches")
        self.buttons[0].set_tooltip_text("Nouvelle tâche")
        self.buttons[1].set_tooltip_text("Supprimer la tâche")
        self.buttons[2].set_tooltip_text("Déplacer la tâche vers le haut")
        self.buttons[3].set_tooltip_text("Déplacer la tâche vers le bas")

        # Keyboard shortcuts :
        accel = Gtk.AccelGroup()
        accel.connect(Gdk.keyval_from_name('n'),
                      Gdk.ModifierType.CONTROL_MASK,
                      Gtk.AccelFlags.VISIBLE,
                      self.on_sidebar_toggle)
        self.add_accel_group(accel)
        


    def get_project_name(self):
        """Returns the project name"""
        page_index = self.tnotebook.get_current_page()
        child = self.tnotebook.get_nth_page(page_index)
        return str(self.tnotebook.get_tab_label_text(child))

    def get_project_current(self):
        """ Returns the current todolist """
        page_index = self.tnotebook.get_current_page()
        return self.tnotebook.get_nth_page(page_index)

    def launch_task_creation(self, widget):
        """Get active instance of ToDoListBox from self.tnotebook
        and pass it args from active instance of NewTaskWin (the one
        in sidebar)"""
        child = self.get_project_current()
        task, date, is_subtask = self.t.get_task_props()
        child.on_task_create(task, date, is_subtask)
        self.on_visible_toggle(self.buttons[0], self.sidebar, None)

    def launch_task_move(self, widget, target_name):
        """Move the selected task by moving its content
        to target then removing it"""
        if widget.get_active():
            task_content = self.get_project_current().get_selected_task()
            if task_content:
                self.get_project_current().on_row_delete()
                self.update_percent_on_check()
                for child in self.tnotebook:
                    project_name = self.tnotebook.get_tab_label_text(child)
                    page_index = self.tnotebook.page_num(child)
                    if project_name == target_name:
                        self.tnotebook.set_current_page(page_index)
                        self.get_project_current().tree_loader(task_content)
                        widget.set_active(False)
                        

    def launch_tasks_check_all(self, widget, new_state):
        print(locals())
        """Check all tasks of current project"""
        self.get_project_current().on_tasks_check_all(new_state)
        
    def on_page_next(self, tnotebook):
        """Switch to next tab"""
        self.tnotebook.next_page()

    def on_page_prev(self, tnotebook):
        """Switch to previous tab"""
        self.tnotebook.prev_page()

    def on_project_new(self, widget):
        """Create a new page from TodoListBox class,
        name is set from project creation dialog"""
        text = self.newproject_entry.get_text()
        newpage = ToDoListBox(self.update_percent_on_check)
        self.tnotebook.append_page(newpage, Gtk.Label(text))
        self.tnotebook.show_all()
        #~ self.pjr_name_input.close()
        self.tnotebook.set_current_page(-1)
        # When project is created and named, create its file on disk :
        newpage.project_name = self.tnotebook.get_tab_label_text(newpage)
        newpage.on_tasks_save(newpage.project_name)
        self.tnotebook.set_tab_reorderable(newpage, True)
        # And add it to "move task" comboxbox :
        b = Gtk.ToggleButton(text, relief=Gtk.ReliefStyle.NONE,
                                    halign=Gtk.Align.START)
        b.connect("toggled", self.launch_task_move, text)
        self.projects_list_box.add(b)
        # Hide popover when done :
        self.newtab_popover.hide()

    def on_project_clone(self, widget):
        """Duplicate a project, create a new file with "-COPIE" suffix"""
        text = self.clone_name_entry.get_text()
        newpage = ToDoListBox(self.update_percent_on_check)
        current_project = self.get_project_name()
        self.get_project_current().on_tasks_save(current_project)
        self.tnotebook.append_page(newpage, Gtk.Label(text))
        self.tnotebook.show_all()
        self.tnotebook.set_current_page(-1)
        self.get_project_current().on_tasks_load_from_file(current_project)
        # When project is created and named, create its file on disk :
        newpage.project_name = self.tnotebook.get_tab_label_text(newpage)
        newpage.on_tasks_save(newpage.project_name)
        self.tnotebook.set_tab_reorderable(newpage, True)
        # And add it to "move task" comboxbox :
        self.projects_list_box.append(None, text)
        # Hide popover when done :
        self.menu_popover.hide()
        
    def on_project_delete(self, tnotebook):
        """Remove page from notebook"""
        name = self.get_project_name()
        
        def update_projects_list_popover():
            for button in self.projects_list_box.get_children():
                if button.get_label() == name:
                    self.projects_list_box.remove(button)

        dialog = ConfirmDialog(self, "Supprimer le projet « " +
                               name + " » ?")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # Remove project file from disk :
            os.remove(share_dir + "/" + name)
            self.tnotebook.remove_page(self.tnotebook.get_current_page())
            update_projects_list_popover()
            if len(os.listdir(share_dir)) == 0:
                self.tnotebook.page1 = ToDoListBox(
                    self.update_percent_on_check)
                self.tnotebook.append_page(self.tnotebook.page1, Gtk.Label(
                    'Nouveau projet'))
                self.tnotebook.page1.on_tasks_save('Nouveau projet')
                self.tnotebook.show_all()
            dialog.destroy()
        else:
            dialog.destroy()

    def on_project_rename(self, widget):
        """Change tab label (rename project)"""
        text = self.rename_prj_entry.get_text()
        os.rename(share_dir + "/" + self.get_project_name(),
                  share_dir + "/" + text)
        self.tnotebook.set_tab_label_text(self.get_project_current(), text)
        # Hide popover when done :
        self.newtab_popover.hide()

    def on_save_all(self, *args):
        """Save current (with focus) list"""
        current_page = self.tnotebook.get_current_page()
        i = 0
        for child in self.tnotebook:
            self.tnotebook.set_current_page(i)
            child.on_tasks_save(self.get_project_name())
            i += 1
        self.tnotebook.set_current_page(current_page)

    def on_sel_action(self, widget):
        """ Launch action depending on clicked button """
        project_name = self.get_project_name()
        target = self.get_project_current()
        if widget == self.buttons[0]:
            self.on_sidebar_toggle()
        elif widget == self.buttons[1]:
            target.on_row_delete()
            self.percent_label.set_text(str(target.get_percent_done()) + "%")
        elif widget == self.buttons[2]:
            target.on_task_reorder("up")
        elif widget == self.buttons[3]:
            target.on_task_reorder("down")
            
    def on_sidebar_toggle(self, *args):
        """Show sidebar and give focus to task description entry"""
        self.on_visible_toggle(self.buttons[0], self.sidebar, self.t.task_entry)

    def on_visible_toggle(self, widget, container, entry):
        #Toggle popover
        if container.get_visible():
            container.hide()
        else:
            container.show_all()
            if entry:
                entry.grab_focus()

    def update_percent_on_change(self, *args):
        """Calculate percentage of done tasks
        based on presence of 'True' in child's store"""
        target_child = locals()['args'][2]
        percent_done = self.tnotebook.get_nth_page(
            target_child).get_percent_done()
        self.percent_label.set_text(str(percent_done) + "%")

    def update_percent_on_check(self):
        tasks_total = self.get_project_current().get_tasks_count()
        if tasks_total != 0:
            tasks_done = self.get_project_current().get_tasks_done()
            percent_done = int(tasks_done * 100 / tasks_total)
            self.percent_label.set_text(str(percent_done) + "%")

    def do_delete_event(self, event):
        """Get user confirmation before leaving"""
        # Show our message dialog :
        d = Gtk.MessageDialog(transient_for=self,
                              modal=True,
                              buttons=Gtk.ButtonsType.OK_CANCEL)
        d.props.text = "Vraiment quitter ?"
        response = d.run()
        d.destroy()

        # We only terminate when the user presses the OK button :
        if response == Gtk.ResponseType.OK:
            self.on_save_all()
            return False
        # Otherwise we keep the application open :
        return True


class TaskNoteBook(Gtk.Notebook):
    """ Initialize custom Notebook class instance """

    def __init__(self, callback):
        Gtk.Notebook.__init__(self)
        self.set_border_width(0)

        # If there is no project file in app data dir, create empty project
        # and create its file on disk :
        if len(os.listdir(share_dir)) == 0:
            self.page1 = ToDoListBox(callback)
            self.append_page(self.page1, Gtk.Label('Nouveau projet'))
            self.page1.on_tasks_save('Nouveau projet')
        else:
            # Otherwise load project files in newly created pages :
            for file in os.listdir(share_dir):
                self.newpage = ToDoListBox(callback)
                self.append_page(self.newpage, Gtk.Label(file))
                self.show_all()
                self.newpage.on_tasks_load_from_file(file)
                self.next_page()
                self.set_tab_reorderable(self.newpage, True)


class ToDoListBox(Gtk.Box):
    """ Create a box that will contain tasks """

    def __init__(self, callback):
        Gtk.Box.__init__(self)

        self.callback_percent = callback
        # Create tasks list and declare its future content :
        self.store = Gtk.TreeStore(bool, str, str)
        self.current_filter_language = None

        # Create a treeview from tasks list :
        self.view = Gtk.TreeView(model=self.store,
                                enable_tree_lines=True)

        # Create "task done" check box :
        renderer_check = Gtk.CellRendererToggle()
        renderer_check.connect("toggled", self.on_task_check)
        # Create check boxes column...
        column_check = Gtk.TreeViewColumn("Finie", renderer_check,
                                          active=0)
        # ... and add it to the treeview :
        self.view.append_column(column_check)

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
        self.column_task.set_expand(True)
        self.column_task.set_resizable(True)
        # ... and add it to the treeview :
        self.view.append_column(self.column_task)

        # Create "task due date" cells...
        renderer_date = Gtk.CellRendererText()
        self.column_date = Gtk.TreeViewColumn("Échéance", renderer_date, text=2)
        self.column_date.set_sort_column_id(1)  # Cette colonne sera triable.
        self.column_date.set_resizable(True)
        self.view.append_column(self.column_date)
        
        # By default, we can't select cells
        # (only active Selection mode allows it) :
        self.sel = self.view.get_selection()
        self.sel.set_mode(Gtk.SelectionMode.BROWSE)

        # Create a scrollable container that will receive the treeview :
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        #~ self.scrollable_treelist.set_border_width(5)
        self.scrollable_treelist.add(self.view)
        # Add this container to the todo list box :
        self.add(self.scrollable_treelist)
        self.set_child_packing(self.scrollable_treelist, True, True, 0, 0)

    def get_selected_iter(self):
        """Get the iter in the selected row and return it"""
        selection = self.view.get_selection()
        (model, pathlist) = selection.get_selected_rows()
        for path in pathlist:
            treeiter = model.get_iter(path)
        return treeiter

    def get_selected_task(self):
        selection = self.view.get_selection()
        try:
            (model, pathlist) = selection.get_selected_rows()
            for path in pathlist:
                return self.tree_dumper(model, path)
        except UnboundLocalError:
            return False

    def get_tasks_count(self):
        """Returns the number of tasks in project"""
        c = 0
        for row in self.store:
            c += 1
        return c

    def get_tasks_done(self):
        """Returns the amount of completed tasks"""
        c = 0
        for row in self.store:
            (state, pathlist, date) = row
            if state is True:
                c += 1
        return c

    def get_percent_done(self):
        """Returns the percentage of completed tasks"""
        tasks = self.get_tasks_count()
        if tasks != 0:
            done = self.get_tasks_done()
            percent_done = int(done * 100 / tasks)

            return percent_done
        else:
            return 0

    def on_task_check(self, widget, path):
        """What to do when checkbox is un/activated"""
        # Toggle check box state :
        # the boolean value of the selected row
        current_value = self.store[path][0]
        # change the boolean value of the selected row in the model
        self.store[path][0] = not current_value
        # new current value!
        current_value = not current_value
        # if length of the path is 1 (that is, if we are selecting an author)
        if len(path) == 1:
            # get the iter associated with the path
            piter = self.store.get_iter(path)
            # get the iter associated with its first child
            citer = self.store.iter_children(piter)
            # while there are children, change the state of their boolean value
            # to the value of the author
            while citer is not None:
                self.store[citer][0] = current_value
                citer = self.store.iter_next(citer)
        # if the length of the path is not 1 (that is, if we are selecting a
        # book)
        elif len(path) != 1:
            # get the first child of the parent of the book (the first book of
            # the author)
            citer = self.store.get_iter(path)
            piter = self.store.iter_parent(citer)
            citer = self.store.iter_children(piter)
            # check if all the children are selected
            all_selected = True
            while citer is not None:
                if self.store[citer][0] == False:
                    all_selected = False
                    break
                citer = self.store.iter_next(citer)
            # if they do, the author as well is selected; otherwise it is not
            self.store[piter][0] = all_selected
        self.callback_percent()

    def on_task_create(self, text, date, is_subtask):
        """Append task at the end of ListStore, if it is a subtask
        append it to the selected iter as long as it is not a subtask
        itself. In which case, append it to its parent"""
        if not is_subtask:
            self.store.append(None, [False, text, date])
        else:
            parent = self.get_selected_iter()
            if self.store.iter_depth(parent) == 0:
                self.store.append(parent, [False, text, date])
            else:
                parent = self.store.iter_parent(parent)
                self.store.append(parent, [False, text, date])

    def on_task_edit(self, widget, path, text):
        """What to do when cell (task) is edited"""
        self.store[path][1] = text

    def on_task_reorder(self, direction):
        """Move selected task up"""
        try:
            selection = self.view.get_selection()
            self.store, paths = selection.get_selected_rows()
            # Get selected task treeiter :
            for path in paths:
                iter = self.store.get_iter(path)
            # And move it :
            if direction == "up":
                self.store.move_before(iter, self.store.iter_previous(iter))
            elif direction == "down":
                self.store.move_after(iter, self.store.iter_next(iter))
        except UnboundLocalError:
            return False

    def on_tasks_check_all(self, new_state):
        """Change task state according to variable"""
        for i, row in enumerate(self.store):
            (current_state, task, date) = row
            iter = self.store.get_iter(i)
            if new_state is False:
                self.store[i][0] = False
            elif new_state is True:
                self.store.set(iter, 0, [new_state])
            else:
                self.store[i][0] = not self.store[i][0]

        self.callback_percent()
        
    def on_tasks_save(self, project_name):
        """Save list in a project named file,
        tasks are written row by row in file, line by line"""
        with open(share_dir + "/" + project_name, 'w') as file_out:
            for row in self.store:
                json.dump(self.tree_dumper(self.store), file_out, indent=4)

    def on_tasks_load_from_file(self, project_name):
        """On app launch, load project file and format entries"""
        if not os.path.exists(share_dir):
            os.makedirs(share_dir, mode=0o775)
        # If file is empty, there's no need to load it :
        if os.path.getsize(share_dir + "/" + project_name) == 0:
            pass
        else:
            # If it exists, load its entries into self.store :
            with open(share_dir + "/" + project_name, 'r') as f:
                self.tree_loader(json.load(f))
 
    def on_row_delete(self):
        """Select line and remove it"""
        try:
            # Get selected row coordinates
            # (as a tuple(ListStore, "row path")) :
            selection = self.view.get_selection()
            self.store, paths = selection.get_selected_rows()
            # Get selected task (row) treeiter :
            for path in paths:
                iter = self.store.get_iter(path)
            # And remove it :
            self.store.remove(iter)
        except UnboundLocalError:
            return False
                
    def tree_dumper(self, treemodel, path=0):
        tree = []
        treeiter = treemodel.get_iter(path)
        parent = treemodel.get_value(treeiter, 1)
        parent_list, pstate_list = [], []
        parent_state = { "State" : treemodel.get_value(treeiter, 0)}
        parent_date = { "Date" : treemodel.get_value(treeiter, 2)}
        pstate_list.append(parent_state)
        pstate_list.append(parent_date)
        parent_list.append(pstate_list)
        children_list = []
        j = 0
        while j < treemodel.iter_n_children(treeiter):
            children_dict = {}
            child = treemodel.iter_nth_child(treeiter, j)
            children_dict[treemodel.get_value(child, 0)] = \
                            treemodel.get_value(child, 1)
            children_list.append(children_dict)
            j += 1
        parent_list.append(children_list)
        parentd = { parent : parent_list }
        tree.append(parentd)
        return tree

    def tree_loader(self, tree):
        """Load the tree, insert parent values in a row then 
        append its children if any"""
        for i in tree:
            for k, v in i.items():
                state = v[0]
                piter = self.store.append(None, [v[0][0]['State'], k,
                                                v[0][1]['Date']])
                enfants = v[1]
                for j in enfants:
                    for task in j.keys():
                        self.store.append(piter, [task, j[task], ""])


class NewTaskWin(Gtk.Grid):
    """Initialize a grid with all widgets needed for tasks creation.
    This grid is included in a popover."""

    def __init__(self):
        Gtk.Grid.__init__(self)
              
        # Create main container:
        box = Gtk.Grid(column_spacing=20, row_spacing=10, border_width=5)
        self.add(box)

        # Task description label :
        label1 = Gtk.Label("Tâche")
        box.add(label1)
        # Create input box :
        self.task_entry = Gtk.Entry()
        self.task_entry.set_text("Nouvel élément")
        # Make inputbox editable :
        self.task_entry.set_property("editable", True)
        box.attach(self.task_entry, 1, 0, 2, 1)
        # Create due date label :
        label2 = Gtk.Label("Échéance")
        box.attach(label2, 0, 1, 1, 1)
        # And due date entry (not editable) :
        self.cal_entry = Gtk.Entry()
        self.cal_entry.set_property("editable", False)
        box.attach(self.cal_entry, 1, 1, 2, 1)
        # Create a calendar to select due date by double click :
        self.calendar = Gtk.Calendar()
        box.attach(self.calendar, 0, 2, 3, 1)
        # Allow <double click> button to select date :
        self.calendar.connect("day-selected-double-click", self.get_cal_date,
                                                        self.calendar)
        
        # Create the task as subtask of selected row ?
        self.checkbox_create_subtask = Gtk.CheckButton.new_with_label(
                                        "Créer en tant que sous-tâche")
        box.attach(self.checkbox_create_subtask, 0, 4, 3, 1)
        
        self.show_all()

    def get_cal_date(self, widget, calendar):
        """Returns selected date in calendar"""
        year, month, day = calendar.get_date()
        date = str(day) + "/" + str(month) + "/" + str(year)
        self.cal_entry.set_text(date)

    def get_task_props(self):
        """Send entry text to parent class object (here : HeaderBarWindow)
        callback function"""
        if self.task_entry.get_text() != "":
            task = self.task_entry.get_text()
            date = self.cal_entry.get_text()
            is_subtask = self.checkbox_create_subtask.get_active()
            return (task, date, is_subtask)


class ConfirmDialog(Gtk.Dialog):
    """A generic yes/no dialog"""

    def __init__(self, parent, label):
        Gtk.Dialog.__init__(self, "Confirmation", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_transient_for(app.window)
        self.props.modal = True
        # Dialog box size params :
        self.set_default_size(150, 80)
        # Label text is set by parent calling function :
        self.label = Gtk.Label(label)
        box = self.get_content_area()
        box.set_border_width(10)
        box.add(self.label)

        self.show_all()


class AboutDialog(Gtk.AboutDialog):
    """Dialog showing tips and info about the app"""

    def __init__(self, *args):
        super().__init__(self)
        self.set_icon_name("simpletodo")
        logo = GdkPixbuf.Pixbuf.new_from_file("simpletodo-96px.png")
        self.set_transient_for(app.window)
        self.set_modal(True)

        self.set_authors(["Sébastien POHER"])
        self.set_comments("""SimpleTodo est un gestionnaire
de tâches simple avec onglets.
Il permet de gérer des projets et de réordonner simplement les tâches.""")
        self.set_copyright("Copyright © Sébastien Poher")
        self.set_license("""
Ce programme est un logiciel libre, vous pouvez donc le redistribuer
et/ou le modifier dans le respect des termes de GNU General Public License
telle que publiée par la Free Software Foundation dans sa version 3
ou ultérieure.""")
        self.set_logo(logo)
        self.set_program_name("SimpleTodo")
        self.set_version("1.4")
        self.set_website("https://git.volted.net/sogal/simpleTodo")

        self.show_all()


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.seb.SimpleTodo",
                         flags=0, **kwargs)

        self.window = None
        self.show_menubar = True

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", AboutDialog)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        builder = Gtk.Builder.new_from_file("menu.ui")
        self.set_app_menu(builder.get_object("app-menu"))

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = HeaderBarWindow(application=self)

        self.window.show_all()
        self.window.sidebar.hide()

    def on_quit(self, action, param):
        self.window.on_save_all()
        self.quit()


share_dir = os.path.expanduser('~/.local/share/simpletodo')
if not os.path.isdir(share_dir):
    os.mkdir(share_dir)


if __name__ == '__main__':
    # Create an app instance from the win instance :
    app = Application()
    app.run()
