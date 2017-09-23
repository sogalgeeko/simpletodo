#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  TreeView-TreeStore-Example.py
#  
#  Copyright 2017 Sébastien POHER <sogal@volted.net>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
#~ from gi.repository import Pango
import sys
import os

books = [["Tolstoy, Leo", ["War and Peace", True], ["Anna Karenina", False]],
         ["Shakespeare, William", ["Hamlet", False],
             ["Macbeth", True], ["Othello", False]],
         ["Tolkien, J.R.R.", ["The Lord of the Rings", False]]]


class MyWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, title="Library", application=app)
        self.set_default_size(250, 100)
        self.set_border_width(10)


        # Create the main box
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # the data are stored in the model
        # create a treestore with two columns
        self.store = Gtk.TreeStore(str, bool)
        # fill in the model
        for i in range(len(books)):
            # the iter piter is returned when appending the author in the first column
            # and False in the second
            piter = self.store.append(None, [books[i][0], False])
            # append the books and the associated boolean value as children of
            # the author
            j = 1
            while j < len(books[i]):
                self.store.append(piter, books[i][j])
                j += 1

        # the treeview shows the model
        # create a treeview on the model self.store
        self.view = Gtk.TreeView()
        self.view.set_model(self.store)
        self.box.add(self.view)
        # the cellrenderer for the second column - boolean rendered as a toggle
        renderer_in_out = Gtk.CellRendererToggle()
        # the second column is created
        column_in_out = Gtk.TreeViewColumn("Out?", renderer_in_out, active=1)
        # and it is appended to the treeself.view
        self.view.append_column(column_in_out)
        # connect the cellrenderertoggle with a callback function
        renderer_in_out.connect("toggled", self.on_toggled)

        # the cellrenderer for the first column - text
        renderer_books = Gtk.CellRendererText()
        # the first column is created
        column_books = Gtk.TreeViewColumn("Books", renderer_books, text=0)
        # and it is appended to the treeself.view
        self.view.append_column(column_books)

        # Add a horiz. box with 2 buttons to create a task and its subtask(s)
        bbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.new_task = Gtk.Button.new_with_label("Task")
        self.new_task.connect("clicked", self.on_task_create)
        self.new_subtask = Gtk.Button.new_with_label("SubTask")
        self.new_subtask.connect("clicked", self.on_subtask_create)
        self.delete_task = Gtk.Button.new_with_label("Supprimer")
        self.delete_task.connect("clicked", self.on_delete_task)
        self.save = Gtk.Button.new_with_label("Save")
        self.save.connect("clicked", self.on_save_list)
        bbox.add(self.new_task)
        bbox.add(self.new_subtask)
        bbox.add(self.delete_task)
        bbox.add(self.save)

        self.box.add(bbox)
        # add the treeview to the window
        self.add(self.box)

    def get_iter(self):
        """Get the iter in the selected row and return it"""
        siter = self.view.get_selection()
        model, paths = siter.get_selected_rows()
        for path in paths:
            treeiter = model.get_iter(path)
        return treeiter

    def get_tasks_amount(self):
        """Returns the number of tasks in project"""
        c = 0
        for row in self.tdlist_store:
            c += 1
        return c

    def get_tasks_done(self):
        """Returns the amount of completed tasks"""
        done = 0
        for row in self.store:
            (state, paths) = row
            if state is True:
                done += 1
        return done

    def get_percent_done(self):
        """Returns the percentage of completed tasks"""
        tasks = self.get_tasks_amount()
        if tasks != 0:
            done = self.get_tasks_done()
            percent_done = int(done * 100 / tasks)

            return percent_done
        else:
            return 0

    def on_task_create(self, widget):
        """create a dummy new task"""
        self.store.append(None, ["blabla", True])

    def on_subtask_create(self, widget):
        """create a subtask of the selected task"""
        treeiter = self.get_iter()
        self.store.append(treeiter, ["blibli", False])

    def on_delete_task(self, widget):
        """Delete selected task"""
        treeiter = self.get_iter()
        self.store.remove(treeiter)

    # callback function for the signal emitted by the cellrenderertoggle
    def on_toggled(self, widget, path):
        # the boolean value of the selected row
        current_value = self.store[path][1]
        # change the boolean value of the selected row in the model
        self.store[path][1] = not current_value
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
                self.store[citer][1] = current_value
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
                if self.store[citer][1] == False:
                    all_selected = False
                    break
                citer = self.store.iter_next(citer)
            # if they do, the author as well is selected; otherwise it is not
            self.store[piter][1] = all_selected

    def on_save_list(self, project_name):
        """Save list in a project named file,
        tasks are written row by row in file, line by line"""
        # TODO : compléter l'enregistrement du fichier au format :
        # [ auteur, [livre 1, livre2]]
        with open(share_dir + "/test", 'w') as file_out:
            for row in self.store:
                i = 0
                treeiter = self.store.get_iter(row.path)
                print(self.store.get_value(treeiter, 0))
                print(self.store.iter_n_children(treeiter))
                while i < self.store.iter_n_children(treeiter):
                    children = self.store.iter_nth_child(treeiter, i)
                    print(self.store.get_value(children, 0))
                    i += 1

                file_out.write("\n")

class MyApplication(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        win = MyWindow(self)
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

share_dir = os.path.expanduser('~/tmp')
app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
