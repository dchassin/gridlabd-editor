"""Pstatus"""

import os, json
import tkinter as tk
from tkinter import Menu, messagebox, filedialog, simpledialog, ttk, font

source_path = os.path.split(__file__)[0]
config_path = os.path.expanduser("~/.gridlabd")
os.makedirs(config_path,exist_ok=True)

import runner

class Pstatus(simpledialog.Dialog):

    def __init__(self,main=None):
        """Create pstatus viewer

        PARAMETERS:

        RETURNS:

            Preference object
        """
        if not main:
            self.main = tk.Tk()
            self.main.withdraw()
        else:
            self.main = main
        self.load()

    def load(self):
        """Load preferences"

        PARAMETERS:

            filename (str or None)    preference filename, None resets to default

        RETURNS:

            None
        """
        self.pstatus = runner.Runner("gridlabd --pstatus=json",output_format="json").get_output()

    def __del__(self):
        if self.main:
            self.main.destroy()

    def dialog(self,parent=None):
        if not parent:
            tk.Tk().withdraw()
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.transient(parent)
        self.title("Preferences")
        self.load()
        headings = list(self.pstatus["0"].keys())
        self.tree = ttk.Treeview(self,columns=headings)
        self.tree.heading("#0",text="Process")
        self.tree.column("#0",width=25)
        self.font = font.nametofont("TkDefaultFont")
        self.width = {"Process":self.font.measure("Process",self) + 10}
        for hdg in headings:
            self.width[hdg] = self.font.measure(hdg,self) + 10;
            self.tree.heading(hdg,text=hdg.title())
        self.refresh(clear=True)
        self.grab_set()
        self.wait_window(self)

    def refresh(self,clear=True):
        self.load()
        if clear:
            for item in self.tree.get_children():
                self.tree.delete(item)
        headings = list(self.pstatus["0"].keys())
        for process, values in self.pstatus.items():
            values = list(values.values())
            self.tree.insert('',tk.END,text=process,values=list(map(lambda x:str(x),values)))
            for hdg,value in zip(headings,values):
                width = self.font.measure(str(value),self) + 10
                if self.width[hdg] < width:
                    self.width[hdg] = width;
        self.tree.column("#0",width=self.width["Process"])
        for hdg in headings:
            self.tree.column(hdg,width=self.width[hdg])
        self.tree.grid(row=0,column=1)
        self.main.after(1000,self.refresh)

import unittest

class _unittest(unittest.TestCase):

    def test_1_load(self):
        self.assertEqual(type(Pstatus().pstatus["0"]["port"]),int)

    def test_2_dialog(self):
        Pstatus().dialog()

if __name__ == '__main__':
    unittest.main()
