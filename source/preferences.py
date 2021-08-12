"""Preferences"""

import os, json
import tkinter as tk
from tkinter import Menu, messagebox, filedialog, simpledialog, ttk

source_path = os.path.split(__file__)[0]
config_path = os.path.expanduser("~/.gridlabd")
os.makedirs(config_path,exist_ok=True)

default_filename = f"{config_path}/app-preferences.conf"
default_preferences = {
    "Welcome dialog enabled" : {
        "value" : True,
        "description" : "Show welcome dialog",
        },
    "Save output filename" : {
        "value" : "output.txt",
        "description" : "File name to save output on exit",
        },
    "Save output" : {
        "value" : True,
        "description" : "Enable saving output on exit",
        },
    "Reopen last file" : {
        "value" : True,
        "description" : "Enable reopening last file on initial open",
        },
    "Unused classes display enabled" : {
        "value" : False,
        "description" : "Enable display of unused classes in elements list",
        },
    "Class display enabled" : {
        "value" : True,
        "description" : "Enable display of classes in elements list",
        },
    "Traceback enabled" : {
        "value" : True,
        "description" : "Enable output of exception traceback data",
        },
    "GridLAB-D executable" : {
        "value" : "/usr/local/bin/gridlabd",
        "description" : "GridLAB-D executable",
        }
    }

class Preferences(simpledialog.Dialog):

    def __init__(self,filename=default_filename):
        """Create preferences object

        PARAMETERS:

        RETURNS:

            Preference object
        """
        self.load(None)
        if filename:
            try:
                self.load(filename)
            except FileNotFoundError:
                pass

    def load(self,filename):
        """Load preferences"

        PARAMETERS:

            filename (str or None)    preference filename, None resets to default

        RETURNS:

            None
        """
        if filename:
            with open(filename,"r") as f:
                self.preferences = json.load(f)
                self.filename = filename
        else:
            self.preferences = default_preferences
            self.filename = default_filename

    def save(self,filename=None):
        """Save preferences

        PARAMETERS:

            filename (str or None)   preference filename, None to user current filename

        RETURNS:

            None
        """
        if not filename:
            filename = self.filename
        if filename:
            with open(filename,"w") as f:
                json.dump(self.preferences,f,indent=4)

    def keys(self):
        return self.preferences.keys()

    def get(self,key):
        if not key in self.preferences.keys():
            raise KeyError(f"key '{key}' not a valid preference")
        return self.preferences[key]['value']

    def set(self,key,value):
        if not key in self.preferences.keys():
            raise KeyError(f"preference key '{key}' is not valid")
        elif type(value) not in [None,type(self.preferences[key]['value'])]:
            raise TypeError(f"preference type '{type(value)}' is not valid")
        last = self.preferences[key]['value']
        self.preferences[key]['value'] = value
        return last

    def dialog(self,parent=None):
        if not parent:
            tk.Tk().withdraw()
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.transient(parent)
        self.title("Preferences")

        tree = ttk.Treeview(self,columns=["value","description"])
        tree.heading("#0",text="Setting")
        tree.column("#0",width=250)
        tree.heading("value",text="Value")
        tree.column("value",width=200)
        tree.heading("description",text="Description")
        tree.column("description",width=350)
        tree.grid(row=0,column=1)
        for name in sorted(self.preferences.keys()):
            value = self.preferences[name]
            item = tree.insert('',tk.END,text=name,values=[str(value["value"]),value["description"]])

        self.tree = tree

        tk.Button(self, text="Save", width=10, command=self.on_save, default=tk.DISABLED).grid(row=3,column=1,padx=10,pady=10)

        self.bind("<Double-1>",self.on_doubleclick)

        self.grab_set()
        self.wait_window(self)

    def on_doubleclick(self,event=None):
        item = self.tree.selection()[0]
        name = self.tree.item(item)['text']
        pref = self.preferences[name]
        value = pref['value']
        description = pref['description']
        ptype = type(value)
        if ptype is bool:
            ask = messagebox.askquestion
            if value:
                kwds = dict(default="yes")
            else:
                kwds = dict(default="no")
            def answer(value): return bool(value=="yes")
        elif ptype is float:
            ask = simpliedialog.askfloat
            kwds = dict(initialvalue=value)
            def answer(value): return float(value)
        elif ptype is int:
            ask = simpledialog.askinteger
            kwds = dict(initialvalue=value)
            def answer(value): return int(value)
        else:
            ask = simpledialog.askstring
            kwds = dict(initialvalue=value)
            def answer(value): return str(value)
        value = answer(ask(name,description,**kwds))
        self.preferences[name]['value'] = value
        self.tree.item(item,values=[self.preferences[name]['value'],self.preferences[name]['description']])
        self.update()

    def on_save(self):
        self.save()
        self.destroy()

import unittest

class PreferencesTest(unittest.TestCase):

    def test_1_init(self):
        self.assertEqual(Preferences(filename=None).keys(),default_preferences.keys())

    def test_2_save(self):
        pref = Preferences(filename=None)
        pref.save("test.conf")

    def test_3_load(self):
        pref = Preferences(filename="test.conf")

    def test_4_get(self):
        pref = Preferences(filename="test.conf")
        self.assertEqual(pref.get("Save output filename"),"output.txt")

    def test_5_set(self):
        pref = Preferences(filename="test.conf")
        self.assertEqual(pref.set("Save output filename","alternate.txt"),"output.txt")
        self.assertEqual(pref.get("Save output filename"),"alternate.txt")

    def test_6_dialog(self):
        Preferences(filename="test.conf").dialog()

if __name__ == '__main__':
    unittest.main()
