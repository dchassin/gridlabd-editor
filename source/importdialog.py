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
# File import dialog
#
class ImportDialog(simpledialog.Dialog):

    def __init__(self,parent,inputname,outputname=None):
        Toplevel.__init__(self, parent)
        self.parent = parent
        self.transient(parent)
        self.title("Import options")

        self.inputname = inputname
        inputext = os.path.splitext(inputname)[1]
        if outputname:
            outputext = os.path.splitext(outputname)[1]
            self.outputname = outputname
        else:
            outputext = ".glm"
            outputname = inputname.replace(inputext,outputext)
        self.outputname = outputname
        self.inputtype = None
        self.outputtype = None
        self.result = None

        config = subprocess.run(f"/usr/local/bin/python3 {share_path}/{inputext[1:]}2{outputext[1:]}.py --config".split(),capture_output=True)
        Label(self,text=f"Input {self.inputname.split('/')[-1]} type:").grid(row=0,column=0)
        Label(self,text=f"Output {self.outputname.split('/')[-1]} type:").grid(row=1,column=0)
        if not config or config.returncode != 0:
            raise Exception("unable to get converter configuration options")
        else:
            options = json.loads(config.stdout.decode('utf-8'))
        try:
            from_options = options["from"]
            self.inputtype = StringVar()
            self.inputtype.set(from_options[0])
            item = OptionMenu(self,self.inputtype,*from_options)
            item.grid(row=0,column=1)
        except Exception as err:
            Label(self,text="None").grid(row=0,column=1)
            root.exception(err)
            self.inputtype = None
        try:
            to_options = options["type"]
            self.outputtype = StringVar()
            self.outputtype.set(to_options[0])
            item = OptionMenu(self,self.outputtype,*to_options)
            item.grid(row=1,column=1)
        except Exception as err:
            Label(self,text="None").grid(row=1,column=1)
            root.exception(err)
            self.outputtype = None

        Label(self,text=f"Convert {inputname.split('/')[-1]} to {outputname.split('/')[-1]}?").grid(row=2)
        Button(self, text="Cancel", width=10, command=self.on_cancel).grid(row=3,column=0,padx=10,pady=10)
        Button(self, text="OK", width=10, command=self.on_ok, default=ACTIVE).grid(row=3,column=1,padx=10,pady=10)

        self.bind("&lt;Return>", self.on_ok)
        self.bind("&lt;Escape>", self.on_cancel)        
        self.grab_set()
        self.wait_window(self)

    def on_ok(self,event=None):
        self.result = True
        self.inputtype = str(self.inputtype.get())
        self.outputtype = str(self.outputtype.get())
        self.destroy()

    def on_cancel(self,event=None):
        self.result = False
        self.inputtype = None
        self.outputtype = None
        self.destroy()
 