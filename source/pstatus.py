"""Pstatus"""

import os, json, datetime
import tkinter as tk
from tkinter import Menu, messagebox, filedialog, simpledialog, ttk, font

source_path = os.path.split(__file__)[0]
config_path = os.path.expanduser("~/.gridlabd")
os.makedirs(config_path,exist_ok=True)

import runner

class Pstatus(simpledialog.Dialog):

    def __init__(self):
        """Create pstatus viewer

        PARAMETERS:

        RETURNS:

            Preference object
        """
        self.main = None
        self.load()

    def load(self,raw=False):
        """Load preferences"

        PARAMETERS:

            filename (str or None)    preference filename, None resets to default

        RETURNS:

            None
        """
        self.pstatus = runner.Runner("gridlabd --pstatus=json",output_format="json").get_output()
        if not raw:
            for item, values in self.pstatus.items():
                if values["status"] in ["RUNNING","PAUSED"]:
                    try:
                        start = datetime.datetime.strptime(values["starttime"],"%Y-%m-%d %H:%M:%S %Z")
                        stop = datetime.datetime.strptime(values["stoptime"],"%Y-%m-%d %H:%M:%S %Z")
                        now = datetime.datetime.strptime(values["progress"],"%Y-%m-%d %H:%M:%S %Z")
                        values["progress"] = f"{(now-start).total_seconds()/(stop-start).total_seconds()*100:.0f}%"
                    except:
                        values["progress"] = ""
                    try:
                        since = datetime.datetime.strptime(values["start"],"%Y-%m-%d %H:%M:%S %Z")
                        values["runtime"] = f"{datetime.datetime.now()-since}"
                    except:
                        values["runtime"] = ""
                else:
                    values["progress"] = "-"
                    values["runtime"] = "-"
                    values["pid"] = "-"
                    values["port"] = "-"
                del values["starttime"]
                del values["stoptime"]
                del values["start"]

    def __del__(self):
        if self.main:
            self.main.destroy()

    def dialog(self,parent=None):
        if not parent:
            self.main = tk.Tk()
            self.main.withdraw()
        else:
            self.main = parent
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.title("Preferences")
        headings = list(self.pstatus["0"].keys())
        self.tree = ttk.Treeview(self,columns=headings)
        self.tree.heading("#0",text="Job")
        self.tree.column("#0",width=25)
        self.font = font.nametofont("TkDefaultFont")
        self.refresh(clear=True)
        self.width = {"#0":50,"pid":50,"progress":50,"status":75,"model":250,"port":50,"runtime":125}
        for hdg in headings:
            self.tree.heading(hdg,text=hdg.title())
            self.tree.column(hdg,width=self.width[hdg],stretch=(hdg=="model"))
        self.tree.column("#0",width=self.width["#0"],stretch=False)
        self.tree.pack(side="left",fill="both",expand=True)
        self.main.after(1000,self.refresh)
        self.tree.bind("<Button-2>",self.show_popup)
        self.grab_set()
        self.wait_window(self)

    def refresh(self,clear=True):
        self.load()
        if clear:
            for item in self.tree.get_children():
                self.tree.delete(item)
        for job, values in self.pstatus.items():
            values = list(values.values())
            self.tree.insert('',tk.END,text=job,values=list(map(lambda x:str(x),values)))

    def show_popup(self,event):
        iid = self.tree.identify_row(event.y)
        pid = self.tree.item(iid,"values")[0]
        if pid != "-" and int() > 0:
            popup = Menu(self,tearoff=0);
            if iid:
                self.tree.selection_set(iid)
                popup.add_command(label="Kill",command=self.pkill)
            try:
                popup.tk_popup(event.x_root,event.y_root,0)
            finally:
                popup.grab_release()

    def pkill(self,idlist=None):
        if not idlist:
            idlist = self.tree.selection()
        for iid in idlist:
            runner.Runner(f"gridlabd --pkill {iid}")


import unittest

class _unittest(unittest.TestCase):

    def test_dialog(self):
        Pstatus().dialog()

if __name__ == '__main__':
    unittest.main()
