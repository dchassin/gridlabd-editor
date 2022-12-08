#
# Tkinter module
#
try:
    import tkinter as tk
    from tkinter import *
    from tkinter.font import Font
    from tkinter import Menu, messagebox, filedialog, simpledialog, ttk
except Exception as err:
    if system == 'Darwin':
        stderr(f"ERROR: {err}. Did you remember to run 'brew install python-tk'?",file=sys.stderr)
    else:
        stderr(f"ERROR: {err}. Did you remember to install tkinter support?",file=sys.stderr)
    quit(-1)

#
# File export dialog
#
class ExportDialog(simpledialog.Dialog):

    def __init__(self,parent,inputname,outputname=None):
        Toplevel.__init__(self, parent)
        self.parent = parent
        self.transient(parent)
        self.title("Import options")
        self.grab_set()
        self.wait_window(self)

