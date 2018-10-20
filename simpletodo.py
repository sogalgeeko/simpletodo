#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO: connect Echap to "hade new task pane"
# TODO: connect Enter to new task name entry in new task pane
# TODO: connect Enter to text entries in project burger menu
# TODO: implement task search functionnality accross all projects and switch to
# project where task is found

import os
import sys
import json
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio
from datetime import datetime, date

class HeaderBarWindow(Gtk.ApplicationWindow):
    """ Initialize window with HeaderBar """

    def __init__(self, *args, **kwargs):
        super().__init__(title="Simple Todo", *args, **kwargs)

        self.set_size_request(850, 530)
        self.set_icon_name("simpletodo")

        # START HEADERBAR :
        headerb = Gtk.HeaderBar()
        headerb.set_show_close_button(True)
        headerb.props.title = "Simple Todo"
        headerb.set_has_subtitle = True
        d = date.today()
        subtitle = d.strftime("%A %d. %B %Y")
        headerb.props.subtitle = str.capitalize(subtitle)
        self.set_titlebar(headerb)

        # Box receiving project management buttons :
        projects_nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(
            projects_nav_box.get_style_context(), "linked")
        projects_mgt_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(
            projects_mgt_box.get_style_context(), "linked")

        # Empty label, will receive percentage done later :
        self.percent_label = Gtk.Label()
        self.percent_label.set_margin_start(5)
        projects_nav_box.add(self.percent_label)

        # "Add project" button and popover :
        new_project_button = Gtk.Button()
        img = Gtk.Image.new_from_icon_name("list-add-symbolic",
                                           Gtk.IconSize.MENU)
        new_project_button.set_image(img)
        projects_nav_box.add(new_project_button)
        # Popover for new project creation dialog :
        self.new_project_popover = Gtk.Popover()
        self.new_project_popover.set_relative_to(headerb)
        new_project_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                  spacing=5, border_width=5)
        new_project_box.set_size_request(240, -1)
        self.new_project_popover.add(new_project_box)
        self.new_project_entry = Gtk.Entry()
        self.new_project_entry.set_text("Nouvel élément")
        self.new_project_entry.set_property("editable", True)
        self.new_project_entry.connect("activate", self.on_project_new_or_clone)
        new_project_box.pack_start(self.new_project_entry, True, True, 0)
        self.new_project_create_button = Gtk.Button("Créer")
        self.new_project_create_button.connect(
            "clicked", self.on_project_new_or_clone)
        new_project_box.pack_start(
            self.new_project_create_button, True, True, 1)
        new_project_button.connect("clicked", self.on_visible_toggle,
                                   self.new_project_popover,
                                   self.new_project_entry)

        # "Remove project" button :
        delete_project_button = Gtk.Button()
        img = Gtk.Image.new_from_icon_name("list-remove-symbolic",
                                           Gtk.IconSize.MENU)
        delete_project_button.set_image(img)
        delete_project_button.connect("clicked", self.on_project_delete)
        projects_nav_box.add(delete_project_button)

        # Other project mgt actions in a menu :
        self.main_menu = Gtk.Button()
        img = Gtk.Image.new_from_icon_name("open-menu-symbolic",
                                           Gtk.IconSize.BUTTON)
        self.main_menu.add(img)
        projects_mgt_box.add(self.main_menu)
        # Define popover :
        self.main_menu_popover = Gtk.PopoverMenu()
        # Make it relative to "menu" button :
        self.main_menu_popover.set_relative_to(self.main_menu)
        # Create a box that will go inside the popover :
        popover_box = Gtk.Box(border_width=5)
        popover_box.set_spacing(5)
        popover_box.set_orientation(Gtk.Orientation.VERTICAL)
        # Put all necessary buttons in the box :
        # Create a box for renaming widgets :
        rename_popover_box = Gtk.Grid(border_width=5,
                                      row_spacing=5,
                                      column_spacing=5)
        # Add "go back" widget :
        go_back0 = Gtk.ModelButton()
        go_back0.props.text = "Retour"
        go_back0.props.inverted = True
        go_back0.props.centered = True
        go_back0.props.menu_name = "main"
        rename_popover_box.attach(go_back0, 0, 0, 2, 1)
        # Add it renaming widgets :
        self.new_prj_name_entry = Gtk.Entry()
        self.new_prj_name_entry.set_text("Nouveau nom du projet")
        rename_button = Gtk.Button.new_with_label("Ok")
        rename_button.connect("clicked", self.on_project_rename)
        rename_popover_box.attach(self.new_prj_name_entry, 0, 1, 1, 1)
        rename_popover_box.attach(rename_button, 1, 1, 1, 1)
        # Add button in the parent popover :
        rename_to_button = Gtk.ModelButton()
        rename_to_button.props.text = "Renommer en..."
        # Link it to the rename_popover_box :
        rename_to_button.props.menu_name = "rename_popover_box"
        rename_to_button.set_relief(2)
        rename_to_button.props.centered = False
        rename_to_button.connect("clicked", self.entry_grab_focus, self.new_prj_name_entry)
        popover_box.add(rename_to_button)
        # Define box to be shown in slided popover :
        clone_name_box = Gtk.Grid(border_width=5,
                                  row_spacing=5,
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
        self.clone_name_button = Gtk.Button.new_with_label("Ok")
        self.clone_name_button.connect("clicked", self.on_project_new_or_clone)
        clone_name_box.attach(self.clone_name_entry, 0, 1, 1, 1)
        clone_name_box.attach(self.clone_name_button, 1, 1, 1, 1)
        # Add button that will show submenu :
        clone_to_button = Gtk.ModelButton.new()
        clone_to_button.connect("clicked", self.entry_grab_focus, self.clone_name_entry)
        # And set the name of the widget it will slides to :
        clone_to_button.props.menu_name = "clone_name_box"
        # Set its properties :
        clone_to_button.props.text = "Cloner vers..."
        clone_to_button.set_relief(2)
        clone_to_button.props.centered = False
        popover_box.add(clone_to_button)
        # Add the clone and renaming box to the popover, not directly but... :
        self.main_menu_popover.add(clone_name_box)
        self.main_menu_popover.add(rename_popover_box)
        # ... in a submenu :
        self.main_menu_popover.child_set_property(
            clone_name_box, "submenu", "clone_name_box")
        self.main_menu_popover.child_set_property(
            rename_popover_box, "submenu", "rename_popover_box")
        # Add other buttons :
        for button_label, action in zip(("Enregistrer",
                                         "À propos",
                                         "Quitter"), (self.on_save_all,
                                                      AboutDialog,
                                                      app.on_quit)):
            b = Gtk.ModelButton.new()
            b.props.text = str(button_label)
            b.set_relief(2)
            b.props.centered = False
            b.connect("clicked", action)
            popover_box.add(b)
        # Add the box inside the popover :
        self.main_menu_popover.add(popover_box)
        self.main_menu.connect("clicked", self.on_visible_toggle,
                               self.main_menu_popover,
                               None)
        self.main_menu_popover.props.modal = True

        headerb.pack_start(projects_nav_box)
        headerb.pack_end(projects_mgt_box)
        # END HEADERBAR

        # START MAIN CONTAINER
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
        # Make sure percentage label is filled at startup
        self.tnotebook.newpage.callback_percent()

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
        self.new_task_dialog = NewTaskWin()
        self.new_task_dialog.set_vexpand(True)
        # This button trigger the task creation process :
        self.new_task_button = Gtk.Button(label="Créer",
                                          margin_left=5,
                                          margin_right=5,
                                          margin_bottom=5)
        self.new_task_button.connect("clicked", self.launch_task_creation)
        sidebar_box.add(self.new_task_dialog)
        sidebar_box.add(self.new_task_button)
        self.overlay.add_overlay(self.sidebar)

        # Below notebook, add tasks management buttons box :
        self.buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                   margin_left=5,
                                   margin_bottom=5,
                                   margin_right=5,
                                   spacing=5)
        self.main_box.add(self.buttons_box)

        # Create tasks check action menu:
        tasks_check_menu_button = Gtk.Button()
        tasks_menu_icon = Gtk.Image.new_from_icon_name("view-more-symbolic",
                                                       Gtk.IconSize.BUTTON)
        tasks_check_menu_button.add(tasks_menu_icon)
        self.buttons_box.pack_start(tasks_check_menu_button, False, True, 0)
        # Define popover for "tasks check" actions :
        self.tasks_check_menu_popover = Gtk.Popover()
        # Make it relative to "menu" button :
        self.tasks_check_menu_popover.set_relative_to(tasks_check_menu_button)
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
        self.tasks_check_menu_popover.add(popover_box)
        tasks_check_menu_button.connect("clicked",
                                        self.on_visible_toggle,
                                        self.tasks_check_menu_popover, None)

        # Create tasks management (add,rm,move) buttons :
        self.task_mgt_buttons = []
        for i, icon in enumerate(["list-add-symbolic",
                                  "list-remove-symbolic",
                                  "go-up-symbolic",
                                  "go-down-symbolic"]):
            img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
            button = Gtk.Button()
            self.task_mgt_buttons.append(button)
            self.task_mgt_buttons[i].set_image(img)
            # Connect them all to an action define later by on_sel_action :
            button.connect("clicked", self.on_sel_action)
            self.buttons_box.pack_start(
                self.task_mgt_buttons[i], False, True, 0)

        # Create ComboxBox of target to move selected task to :
        projects_list_button = Gtk.Button.new_with_label("Déplacer vers")
        projects_list_button.set_margin_start(5)
        # Define popover for projects list (task move) :
        self.projects_list_popover = Gtk.Popover()
        self.projects_list_popover.set_relative_to(projects_list_button)
        self.projects_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        for project_name in all_projects:
            tb = Gtk.ToggleButton(project_name,
                                  relief=Gtk.ReliefStyle.NONE,
                                  halign=Gtk.Align.START)
            tb.connect("toggled", self.launch_task_move, project_name)
            self.projects_list_box.add(tb)
        self.projects_list_popover.add(self.projects_list_box)
        self.buttons_box.pack_end(projects_list_button, False, True, 0)
        projects_list_button.connect("clicked",
                                     self.on_visible_toggle,
                                     self.projects_list_popover,
                                     self.projects_list_box)
        # END MAIN CONTAINER

        # Add tooltips to buttons that use icon :
        tasks_check_menu_button.set_tooltip_text("Gérer les tâches")
        self.task_mgt_buttons[0].set_tooltip_text("Nouvelle tâche")
        self.task_mgt_buttons[1].set_tooltip_text("Supprimer la tâche")
        self.task_mgt_buttons[2].set_tooltip_text(
            "Déplacer la tâche vers le haut")
        self.task_mgt_buttons[3].set_tooltip_text(
            "Déplacer la tâche vers le bas")

        # Keyboard shortcuts :
        accel = Gtk.AccelGroup()
        accel.connect(Gdk.keyval_from_name('n'),
                      Gdk.ModifierType.CONTROL_MASK,
                      Gtk.AccelFlags.VISIBLE,
                      self.on_sidebar_toggle)
        accel.connect(Gdk.keyval_from_name('w'),
                      Gdk.ModifierType.CONTROL_MASK,
                      Gtk.AccelFlags.VISIBLE,
                      self.on_project_delete)
        accel.connect(Gdk.keyval_from_name('Page_Down'),
                      Gdk.ModifierType.CONTROL_MASK,
                      Gtk.AccelFlags.VISIBLE,
                      self.on_page_nav_next)
        accel.connect(Gdk.keyval_from_name('Page_Up'),
                      Gdk.ModifierType.CONTROL_MASK,
                      Gtk.AccelFlags.VISIBLE,
                      self.on_page_nav_prev)
        self.add_accel_group(accel)

    def entry_grab_focus(self, widget, entry):
        """This is used to give focus to text entries in main_menu_popover"""
        self.set_focus(entry)

    def get_project_current(self):
        """Returns the current project"""
        page_index = self.tnotebook.get_current_page()
        return self.tnotebook.get_nth_page(page_index)

    def get_project_name(self):
        """Returns the current project name (get it from its tab label)"""
        current_todolist = self.get_project_current()
        return str(self.tnotebook.get_tab_label_text(current_todolist))

    def launch_task_creation(self, widget):
        """Get active instance of ToDoListBox from self.tnotebook
        and pass it args from active instance of NewTaskWin (the one
        in sidebar)"""
        current_todolist = self.get_project_current()
        task, date, is_subtask = self.new_task_dialog.get_task_props()
        current_todolist.on_task_create(task, date, is_subtask)
        self.on_visible_toggle(self.task_mgt_buttons[0], self.sidebar, None)

    def launch_task_move(self, widget, target_name):
        """Get selected task content, remove the row and
        recreate it in target project"""
        if widget.get_active():
            current_todolist = self.get_project_current()
            task_content = current_todolist.get_selected_task()
            if task_content:
                current_todolist.on_row_delete()
                self.update_percent_on_check()
                for child in self.tnotebook:
                    project_name = self.tnotebook.get_tab_label_text(child)
                    page_index = self.tnotebook.page_num(child)
                    if project_name == target_name:
                        self.tnotebook.set_current_page(page_index)
                        new_todolist = self.get_project_current()
                        new_todolist.tree_loader([task_content])
                        widget.set_active(False)
        self.projects_list_popover.hide()

    def launch_tasks_check_all(self, widget, new_state):
        """Change "checked" stated of all tasks of current project"""
        self.get_project_current().on_tasks_check_all(new_state)

    def on_page_nav_next(self, tnotebook, *args):
        """Switch to next tab"""
        self.tnotebook.next_page()

    def on_page_nav_prev(self, tnotebook, *args):
        """Switch to previous tab"""
        self.tnotebook.prev_page()

    def on_project_new_or_clone(self, widget):
        """This function can be used to create a new page from TodoListBox class,
        name is set from project creation dialog, or create a clone of current
        project"""
        text = ""
        if widget == self.clone_name_button:
            clone = True
            current_project = self.get_project_name()
            text = self.clone_name_entry.get_text()
            self.get_project_current().on_tasks_save(current_project)
            self.main_menu_popover.hide()
        else:
            clone = False
            text = self.new_project_entry.get_text()
        newpage = ToDoListBox(self.update_percent_on_check)
        self.tnotebook.append_page(newpage, Gtk.Label(text))
        self.tnotebook.show_all()
        self.tnotebook.set_current_page(-1)
        # When project is created and named, create its file on disk :
        newpage.project_name = self.tnotebook.get_tab_label_text(newpage)
        newpage.on_tasks_save(newpage.project_name)
        self.tnotebook.set_tab_reorderable(newpage, True)
        # And add it to "move task" projects list popover :
        b = Gtk.ToggleButton(text, relief=Gtk.ReliefStyle.NONE,
                             halign=Gtk.Align.START)
        b.connect("toggled", self.launch_task_move, text)
        if clone:
            self.get_project_current().on_tasks_load_from_file(current_project)
        # Hide popover when done :
        self.new_project_popover.hide()

    def on_project_delete(self, tnotebook, *args):
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
        old_name = self.get_project_name()
        new_name = self.new_prj_name_entry.get_text()
        # Rename appropriate button in projects list popover :
        for button in self.projects_list_box.get_children():
            if button.get_label() == old_name:
                button.set_label(new_name)
        # Then rename project file on disk and change tab label :
        os.rename(share_dir + "/" + self.get_project_name(),
                  share_dir + "/" + new_name)
        self.tnotebook.set_tab_label_text(self.get_project_current(), new_name)
        # Hide popover when done :
        self.main_menu_popover.hide()

    def on_save_all(self, *args):
        """Iterate through todolists in notebook, for each todolist
        launch save function then give focus back to active todolist"""
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
        if widget == self.task_mgt_buttons[0]:
            self.on_sidebar_toggle()
        elif widget == self.task_mgt_buttons[1]:
            target.on_row_delete()
            self.percent_label.set_text(str(target.get_percent_done()) + "%")
        elif widget == self.task_mgt_buttons[2]:
            target.on_task_reorder("up")
        elif widget == self.task_mgt_buttons[3]:
            target.on_task_reorder("down")

    def on_sidebar_toggle(self, *args):
        """Show sidebar and give focus to task description entry"""
        self.on_visible_toggle(self.task_mgt_buttons[
                               0], self.sidebar, self.new_task_dialog.task_entry)

    def on_visible_toggle(self, widget, container, entry):
        """Toggle container visibility, if container has an Entry widget,
        let it grab the focus"""
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

    def do_delete_event(self, *args):
        """Get user confirmation before leaving"""
        # Show our message dialog :
        d = ConfirmDialog(self, "Vraiment quitter ?")
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
            page1 = ToDoListBox(callback)
            self.append_page(page1, Gtk.Label('Nouveau projet'))
            page1.on_tasks_save('Nouveau projet')
        else:
            # Otherwise load project files in newly created pages :
            print(all_projects)
            for file in all_projects:
                self.newpage = ToDoListBox(callback)
                self.append_page(self.newpage, Gtk.Label(file))
                self.set_tab_reorderable(self.newpage, True)
                self.show_all()
                self.newpage.on_tasks_load_from_file(file)
                self.next_page()


class ToDoListBox(Gtk.Box):
    """ Create a box that will contain tasks """

    def __init__(self, callback):
        Gtk.Box.__init__(self)

        self.callback_percent = callback
        # Create tasks store and declare its future content :
        self.store = Gtk.TreeStore(bool, str, str)
        self.current_filter_language = None
        # Then create a treeview from tasks store :
        self.view = Gtk.TreeView(model=self.store,
                                 enable_tree_lines=True)
        #~ self.set_size_request(300, 150)

        # Create "task done" check box :
        renderer_check = Gtk.CellRendererToggle()
        renderer_check.connect("toggled", self.on_task_check)
        # Create check boxes column...
        column_check = Gtk.TreeViewColumn("Finie", renderer_check,
                                          active=0)
        column_check.set_sort_column_id(0)
        # ... and add it to the treeview :
        self.view.append_column(column_check)

        # Create "task name" cells...
        renderer_task = Gtk.CellRendererText()
        renderer_task.set_property("editable", True)
        # ... and launch 'on_task_edit' when edited :
        renderer_task.connect("edited", self.on_task_edit, 1)
        # Create tasks name column...
        self.column_task = Gtk.TreeViewColumn("Description de la tâche",
                                              renderer_task, text=1)
        self.column_task.set_sort_column_id(1)
        self.column_task.set_expand(True)
        self.column_task.set_resizable(True)
        # ... and add it to the treeview :
        self.view.append_column(self.column_task)
        # Create "task due date" cells...
        renderer_date = Gtk.CellRendererText()
        renderer_date.set_property("editable", True)
        renderer_date.connect("edited", self.on_task_edit, 2)
        self.column_date = Gtk.TreeViewColumn("Échéance", renderer_date, text=2)
        self.column_date.set_sort_column_id(2)
        self.column_date.set_resizable(True)
        self.view.append_column(self.column_date)
        self.view.set_hexpand(True)

        # Allow selection by single click, double-click launches edition mode :
        self.sel = self.view.get_selection()
        self.sel.set_mode(Gtk.SelectionMode.BROWSE)

        # Create a scrollable container that will receive the treeview :
        scrollable_treelist = Gtk.ScrolledWindow()
        scrollable_treelist.set_vexpand(True)
        # Needed to fix Gtk Warnings about size allocation :
        grid = Gtk.Grid()
        grid.attach(self.view, 0, 0 ,1, 1)
        scrollable_treelist.add(grid)
        # Add this container to the todo list box :
        self.add(scrollable_treelist)
        self.set_child_packing(scrollable_treelist, True, True, 0, 0)

    def get_selected_iter(self):
        """Get the iter in the selected row and return it"""
        selection = self.view.get_selection()
        (model, pathlist) = selection.get_selected_rows()
        if len(pathlist) != 0:
            for path in pathlist:
                treeiter = model.get_iter(path)
            return treeiter
        else:
            return False

    def get_selected_task(self):
        """Get the task selected"""
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
        # the boolean value of the selected row :
        current_value = self.store[path][0]
        # change the boolean value of the selected row in the model :
        self.store[path][0] = not current_value
        # new current value!
        current_value = not current_value
        # if length of the path is 1 (parent row) :
        if len(path) == 1:
            # get the iter associated with the path (parent task in that row) :
            piter = self.store.get_iter(path)
            # get the iter associated with its first child :
            citer = self.store.iter_children(piter)
            # while there are children, change the state of their boolean value
            # to the value of the parent task :
            while citer is not None:
                self.store[citer][0] = current_value
                citer = self.store.iter_next(citer)
        # if the length of the path is not 1 (a parent task is selected) :
        elif len(path) != 1:
            # get the first subtask of this parent task :
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
            # if they do, the parent task as well is selected (completed) :
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
            if not parent:
                self.store.append(None, [False, text, date])
            elif self.store.iter_depth(parent) == 0:
                self.store.append(parent, [False, text, date])
            else:
                parent = self.store.iter_parent(parent)
                self.store.append(parent, [False, text, date])

    def on_task_edit(self, widget, path, text, cell):
        """What to do when cell (task) is edited ?
        if cell is date, check its format (must be dd/mm/yyyy)"""
        if cell == 2:
                if self.validate(text):
                    self.store[path][cell] = text
                else:
                    self.store[path][cell] = ""
        else:
            self.store[path][cell] = text

    def on_task_reorder(self, direction):
        """Move selected task up or down"""
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
            path = self.store.get_path(iter)
            if not self.store.iter_has_child(iter):
                if new_state is False:
                    self.store[iter][0] = False
                elif new_state is True:
                    self.store.set(iter, 0, [new_state])
                else:
                    self.store[iter][0] = not self.store[iter][0]
            elif self.store.iter_has_child(iter):
                citer = self.store.iter_children(iter)
                while citer is not None:
                    if new_state == False:
                        self.store[citer][0] = False
                    elif new_state == True:
                        self.store[citer][0] = True
                    else:
                        self.store[citer][0] = not self.store[citer][0]
                    break
                    citer = self.store.iter_next(citer)
                self.on_task_check(None, path)
        self.callback_percent()

    def on_tasks_save(self, project_name):
        """Save list in a project named file,
        tasks are written row by row in a json object then written to file"""
        with open(share_dir + "/" + project_name, 'w') as file_out:
            tree = []
            for row in self.store:
                tree.append(self.tree_dumper(self.store, row.path))
            json.dump(tree, file_out, indent=4)

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
        """Dump the task content in json format :
        {task_name : [{"state":bool},{"date":str}],
            [{"subtask1_name":[bool,"subtask_date"]}]}"""
        treeiter = treemodel.get_iter(path)
        parent = treemodel.get_value(treeiter, 1)
        parent_list, pstate_list = [], []
        parent_state = {"State": treemodel.get_value(treeiter, 0)}
        parent_date = {"Date": treemodel.get_value(treeiter, 2)}
        pstate_list.append(parent_state)
        pstate_list.append(parent_date)
        parent_list.append(pstate_list)
        children_list = []
        j = 0
        while j < treemodel.iter_n_children(treeiter):
            children_dict = {}
            child = treemodel.iter_nth_child(treeiter, j)
            children_dict[treemodel.get_value(child, 1)] = \
                [treemodel.get_value(child, 0), treemodel.get_value(child, 2)]
            children_list.append(children_dict)
            j += 1
        parent_list.append(children_list)
        parentd = {parent: parent_list}

        return parentd

    def tree_loader(self, tree):
        """Load the tree, insert parent values in a row then
        append its children if any"""
        for i in tree:
            # Load elements a the list (tree) :
            for k, v in i.items():
                # Append 'task state', 'task description', 'task due date' :
                state = v[0]
                piter = self.store.append(None, [v[0][0]['State'], k,
                                                 v[0][1]['Date']])
                children = v[1]
                # Load children from list (v[1]) :
                for j in children:
                    # For each child, append 'task state', 'task description'
                    # to parent iter :
                    for task in j.keys():
                        self.store.append(piter, [j[task][0], task, j[task][1]])

    def validate(self, date):
        try:
            datetime.strptime(date, "%d/%m/%Y")
            return True
        except ValueError:
            warn = Gtk.MessageDialog(buttons=Gtk.ButtonsType.CLOSE, text="Erreur, la date doit être au format jj/mm/aaaa")
            warn.set_transient_for(app.window)
            response = warn.run()
            if response == Gtk.ResponseType.CLOSE:
                warn.destroy()


class NewTaskWin(Gtk.Grid):
    """Initialize a grid with all widgets needed for tasks creation.
    This grid is included in a popover."""

    def __init__(self):
        Gtk.Grid.__init__(self)

        # Create main container:
        box = Gtk.Grid(column_spacing=20, row_spacing=10, border_width=5)
        self.add(box)

        label1 = Gtk.Label("Tâche")
        box.add(label1)
        self.task_entry = Gtk.Entry()
        self.task_entry.set_text("Nouvelle tâche")
        self.task_entry.set_property("editable", True)
        box.attach(self.task_entry, 1, 0, 2, 1)
        # Create the task as subtask of selected row ?
        self.checkbox_create_subtask = Gtk.CheckButton.new_with_label(
            "Créer en tant que sous-tâche")
        # If we create a subtask, we don't need date (will use parent date) :
        #~ self.checkbox_create_subtask.connect("toggled",
                                             #~ self.disable_calendar)
        box.attach(self.checkbox_create_subtask, 0, 4, 3, 1)
        label2 = Gtk.Label("Échéance")
        box.attach(label2, 0, 1, 1, 1)
        self.cal_entry = Gtk.Entry()
        self.cal_entry.set_property("editable", False)
        self.cal_entry.set_sensitive(False)
        box.attach(self.cal_entry, 1, 1, 2, 1)
        # Create a calendar to select due date by double click :
        self.calendar = Gtk.Calendar()
        box.attach(self.calendar, 0, 2, 3, 1)
        self.calendar.connect("day-selected", self.get_cal_date,
                              self.calendar)
        self.calendar.select_day(int(date.today().strftime("%d")))

        self.show_all()

    def disable_calendar(self, widget):
        """Make calendar unsensitive if it is a subtask"""
        if self.calendar.get_sensitive():
            self.calendar.set_sensitive(False)
        else:
            self.calendar.set_sensitive(True)

    def get_cal_date(self, widget, calendar):
        """Returns selected date in calendar"""
        year, month, day = calendar.get_date()
        date = str(day) + "/" + str(month+1) + "/" + str(year)
        self.cal_entry.set_text(date)

    def get_task_props(self):
        """Send entry text to parent class object (here : HeaderBarWindow)
        callback function"""
        if self.task_entry.get_text() != "":
            task = self.task_entry.get_text()
            date = self.cal_entry.get_text()
            is_subtask = self.checkbox_create_subtask.get_active()
            # Reset all entries (clear their content) :
            self.task_entry.set_text("Nouvelle tâche")
            self.cal_entry.set_text("")
            self.checkbox_create_subtask.set_active(False)
            return (task, date, is_subtask)


class ConfirmDialog(Gtk.MessageDialog):
    """A generic Ok/Cancel dialog"""

    def __init__(self, parent, label):
        Gtk.MessageDialog.__init__(self, transient_for=parent,
                                   modal=True,
                                   buttons=Gtk.ButtonsType.OK_CANCEL,
                                   text=label)


class Shortcuts(Gtk.ShortcutsWindow):
    """Window displayong app shortcuts"""
    def __init__(self, *args):
        builder = Gtk.Builder.new_from_file("shortcuts.ui")
        window = builder.get_object("shortcuts-clocks")
        window.set_transient_for(app.window)
        window.set_modal(True)
        window.show_all()


class Prefs(Gtk.Window):
    """Pref dialog to set save folder"""

    def __init__(self, *args):
        Gtk.Window.__init__(self)
        self.set_application(app)
        self.set_type_hint(1)
        self.set_transient_for(app.window)
        self.set_modal(True)
        self.set_title("Choisir l'emplacement du dossier de sauvegarde")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                      spacing=5, border_width=5)
        self.choose = Gtk.FileChooserButton.new(
            "Enregistrer les projets sous...", 2)
        validate = Gtk.Button.new_with_label("Valider")
        validate.connect("clicked", self.get_save_path)

        box.add(self.choose)
        box.add(validate)
        self.add(box)
        self.show_all()

    def get_save_path(self, widget):
        """Get choosen folder path and save it in a config file"""
        path = self.choose.get_filename()
        with open(conf_dir + "/conf", 'w') as f:
            f.write("save_dir=" + path)
        self.hide()


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
        self.set_version("2.0b")
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

        action = Gio.SimpleAction.new("prefs", None)
        action.connect("activate", Prefs)
        self.add_action(action)

        action = Gio.SimpleAction.new("shortcuts", None)
        action.connect("activate", Shortcuts)
        self.add_action(action)

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

    def on_quit(self, *args):
        self.window.do_delete_event()
        self.quit()


if __name__ == '__main__':
    # Create an app instance from the win instance :
    app = Application()
    conf_dir = os.path.expanduser('~/.config/simpletodo')
    if not os.path.isdir(conf_dir):
        os.mkdir(conf_dir)
    conf_file = os.path.expanduser('~/.config/simpletodo/conf')
    all_projects = []
    if os.path.isfile(conf_file):
        with open(conf_file, 'r') as f:
            configured_dir = f.read().split("=")[1]
            if os.path.exists(configured_dir):
                share_dir = configured_dir
            else:
                dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CANCEL, "Erreur de configuration")
                dialog.format_secondary_text(
                    "Vérifier le chemin d'enregistrement des fichiers de projets")
                dialog.run()
                share_dir = os.path.expanduser('~/.local/share/simpletodo')
                dialog.destroy()
    else:
        share_dir = os.path.expanduser('~/.local/share/simpletodo')
        if not os.path.isdir(share_dir):
            os.mkdir(share_dir)
    for file in os.listdir(share_dir):
        try:
            with open(share_dir + "/" + file, 'r') as f:
                try:
                    json.load(f)
                except StopIteration:
                    pass
                else:
                    all_projects.append(file)
        except:
            print("Warning: " + share_dir + "/" + file + " n'a pas été chargé.")
    app.run()
