"""HiPAS GridLAB-D Weather Manager
Copyright (C) 2021 Regents of the Leland Stanford Junior University
See https://www.gridlabd.us/ for license, acknowledgments, credits, manuals, documentation, and tutorials.

"""
import sys, os
import timeit
from tkinter import *
from tkinter import Menu, messagebox, filedialog, simpledialog, ttk
import subprocess
from PIL import Image, ImageTk
import pandas
from edittable import PandasDataFrame
from tmy3 import TMY3

dialog_width = 600
dialog_height = 400
pad = 5
country = "US"

try:
    import gridlabd
except:
    stderr("ERROR: GridLAB-D is not installed for this python environment")
    quit(-1)

title = "Weather"
version = gridlabd.__version__.split('-')[0]
build = gridlabd.version()["build"]
branch = gridlabd.version()["branch"] 
python = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ({sys.version_info.releaselevel})"
system = f"{os.uname().sysname} {os.uname().release} ({os.uname().machine})"
library = gridlabd.__file__

icon_file = __file__.replace(".py",".ico")
if not os.path.exists(icon_file):
    icon_png = __file__.replace(".py",".png")
    icon = Image.open(icon_png)
    icon.save(icon_file,format="ICO",sizes=[(32,32),(64,64)])

if sys.platform == "darwin":
    from Foundation import NSBundle
    bundle = NSBundle.mainBundle()
    if bundle:
        info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
        if info and info['CFBundleName'] == 'Python':
            info['CFBundleName'] = title
            info['CFBundleShortVersionString'] = version
            info['CFBundleVersion'] = f"{build} {branch}"
            info['CFBundleIconFile'] = icon_file
            info['NSHumanReadableCopyright'] = gridlabd.copyright().split("\n\n")[1]

class Weather(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.title("HiPAS GridLAB-D Weather")
        self.configure()
        self.focus()

        self.style = ttk.Style(self)
        self.style.configure('gridlabd.Treeview',
            selectmode = 'browse',
            )
        self.style.configure('gridlabd.Label',
            )

        self.geometry(f'{dialog_width}x{dialog_height}')

        self.indexview = IndexView(self,height=int(dialog_height-20-2*pad))
        self.indexview.column('#0',width=int(dialog_width/2))
        self.indexview.grid(row=0, column=0, padx=pad, pady=pad, sticky="ew")
        self.indexview.heading('#0',text="Remote files")

        self.listview = ListView(self,height=int(dialog_height-20-2*pad))
        self.listview.column('#0',width=int(dialog_width/2))
        self.listview.grid(row=0, column=2, padx=pad, pady=pad, sticky="ew")
        self.listview.heading('#0',text="Local files")

        self.message = Label(self, text="Initializing...", width=9999, anchor="w")
        self.message.grid(row=1, column=0, columnspan=3, sticky="w")

        self.columnconfigure(0,weight=1)
        self.columnconfigure(2,weight=1)
        self.rowconfigure(0,weight=1)

        self.listview.reload()
        self.indexview.reload()
        self.status()

    def status(self,text="Ready"):
        self.message.config(text=text)
        self.update()

    def command(self,text):
        subcommand = ["gridlabd","weather"]
        subcommand.extend(text)
        # print("COMMAND:",subcommand,file=sys.stderr)
        self.config(cursor="wait")
        self.update()
        result = subprocess.run(subcommand,capture_output=True)
        self.config(cursor="")
        self.update()
        if result.returncode == 0:
            return result.stdout.decode('utf-8').strip().split('\n')
        else:
            messagebox.showerror(f"Weather error",result.stderr)
            return []

    def edit_settings(self,event=None):
        settings = Settings(self)
        self.wait_window(settings)
        if settings.changed:
            self.indexview.reload()

class Settings(Toplevel):

    settings = {
        "GITHUB" : {
            "dialog" : lambda title,prompt,value: simpledialog.askstring(title=title,prompt=prompt,initialvalue=value),
            "prompt" : "GitHub repo server"
            },
        "GITHUBUSERCONTENT" : {
            "dialog" : lambda title,prompt,value: simpledialog.askstring(title=title,prompt=prompt,initialvalue=value),
            "prompt" : "GitHub content server"
            },
        "COUNTRY" : {
            "dialog" : lambda title,prompt,value: simpledialog.askstring(title=title,prompt=prompt,initialvalue=value),
            "prompt" : "Country"
            },
        "GITUSER" : {
            "dialog" : lambda title,prompt,value: simpledialog.askstring(title=title,prompt=prompt,initialvalue=value),
            "prompt" : "GitHub user"
            },
        "GITREPO" : {
            "dialog" : lambda title,prompt,value: simpledialog.askstring(title=title,prompt=prompt,initialvalue=value),
            "prompt" : "GitHub repo"
            },
        "GITBRANCH" : {
            "dialog" : lambda title,prompt,value: simpledialog.askstring(title=title,prompt=prompt,initialvalue=value),
            "prompt" : "Weather repo branch"
            },
        "CACHEDIR" : {
            "dialog" : lambda title,prompt,value: filedialog.askdirectory(title=title,initialdir=value,mustexist=True),
            "prompt" : "Local cache folder"
            },
        "DATADIR" : {
            "dialog" : lambda title,prompt,value: filedialog.askdirectory(title=title,initialdir=value,mustexist=True),
            "prompt" : "Local data folder"
            },
    }
    def __init__(self, parent):
        super().__init__(parent,width=750,height=200)
        self.main = parent
        self.title("Remote settings")
        self.table = ttk.Treeview(self,columns=['value'],show='tree')
        self.table.column('#0',width=200)
        self.table.column('value',width=550,stretch=YES)
        self.table.grid(row=0, column=0, sticky='nsew')
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.reload()
        self.table.bind("<Double-1>",self.on_doubleclick)
        self.changed = False

    def reload(self):
        self.config(cursor="wait")
        for item in self.table.get_children():
            self.table.delete(item)
        info = self.main.command(["config","show"])
        self.index = {}
        for item in info:
            spec = item.split("=")
            if len(spec) > 1:
                prompt = self.settings[spec[0]]['prompt']
                self.table.insert('',END,text=prompt,values=[spec[1].replace('"','')])
                self.index[prompt] = spec[0]
        self.table.update()
        self.config(cursor="")

    def on_doubleclick(self,event):
        row = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)
        entry = TableEntryPopup(self.table,row,column)
        entry.wait_window()
        if entry.data:
            self.main.command(["config","set",self.index[entry.data['text']],entry.data['values'][0]])
            self.changed = True


class TableEntryPopup(Entry):
    def __init__(self,parent,row,column,**kwargs):
        super().__init__(parent,**kwargs)
        self.tv = parent
        self.row = row
        self.column = int(column[1:])-1
        self.data = parent.item(row)
        self.insert(0,self.data['values'][self.column])
        self['exportselection'] = False
        self.focus_force()
        self.bind("<Return>", self.on_return)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Escape>", self.on_cancel)
        self.bind("<FocusOut>", self.on_cancel)
        x,y,width,height = parent.bbox(row, column)
        pady = height//2
        self.place(x=x, y=y+pady, anchor="w", relwidth=1)
        self.select_all()

    def on_return(self, event):
        self.data['values'][self.column] = self.get()
        self.tv.item(self.row, values=self.data['values'])
        self.destroy()

    def on_cancel(self, event):
        self.data = None
        self.destroy()

    def select_all(self, *ignore):
        self.selection_range(0, 'end')
        return 'break'

class IndexView(ttk.Treeview):

    def __init__(self,main,*args,**kwargs):
        ttk.Treeview.__init__(self,*args,**kwargs)
        self.main = main
        self.index = {}
        self.bind("<Double-1>",self.download_file)
        self.bind("<Button-2>",self.show_popup)
        self.update()

    def reload(self):
        self.main.status("Loading remote index...")
        for item in self.get_children():
            self.delete(item)
        country_code = self.main.command("config get COUNTRY".split())
        country = self.insert('',END,text=country_code)
        files = self.main.command(["index"])
        states = []
        for file in files:
            state = file[0:2]
            if not state in states:
                states.append(state)
        items = {}
        for state in states:
            tag = items[state] = self.insert(country,END,text=state)
            self.index[tag] = f"^{state}"
        for file in files:
            state = file[0:2]
            tag = self.insert(items[state],END,text=file[3:].replace("_"," ").split(".")[0])
            self.index[tag] = file

    def show_popup(self,event):
        popup = Menu(self,tearoff=0);
        iid = self.identify_row(event.y)
        if iid:
            self.selection_set(iid)
            popup.add_command(label="Download",command=self.download_file)
            popup.add_separator()
        popup.add_command(label="Settings...",command=self.main.edit_settings)
        try:
            popup.tk_popup(event.x_root,event.y_root,0)
        finally:
            popup.grab_release()

    def download_file(self,event=None):
        tag = self.selection()[0]
        if tag in self.index.keys():
            file = self.index[tag]
            if file[0] == '^':
                self.main.status(f"Downloading all remote files for {file[1:]}...")
            else:
                self.main.status(f"Downloading remote file {file}...")
            self.main.listview.get_file(file)

class ListView(ttk.Treeview):

    def __init__(self,main,*args,**kwargs):
        ttk.Treeview.__init__(self,*args,**kwargs)
        self.main = main
        self.bind("<Double-1>",self.view_data)
        self.bind("<Button-2>",self.show_popup)
        self.update()

    def get_file(self,file):
        self.main.command(["get",file])
        self.main.listview.reload()

    def show_popup(self,event):
        popup = Menu(self,tearoff=0);
        iid = self.identify_row(event.y)
        if iid:
            self.selection_set(iid)
            popup.add_command(label="View data",command=self.view_data)
            popup.add_command(label="Show info",command=self.show_info)
            popup.add_command(label="Copy name",command=self.copy_name)
            popup.add_separator()
            popup.add_command(label="Delete",command=self.delete_item)
            popup.add_command(label="Delete all",command=self.delete_all)
            popup.add_separator()
        popup.add_command(label="Settings...",command=self.main.edit_settings)
        try:
            popup.tk_popup(event.x_root,event.y_root,0)
        finally:
            popup.grab_release()

    def copy_name(self):
        tag = self.selection()[0]
        file = self.item(tag,'text')
        if file:
            self.clipboard_clear()
            self.clipboard_append(file)
            self.update()

    def delete_item(self):
        tag = self.selection()[0]
        file = self.item(tag,'text')
        if file:
            self.main.status(f"Deleting local data for {file}...")
            self.main.command(["delete",file])
            self.reload()

    def delete_all(self):
        ans = messagebox.askokcancel("Delete all?","Are you sure you want to delete all local weather data?")
        if ans == True:
            self.main.status(f"Deleting all local data...")
            self.main.command(["delete"])
            self.reload()

    def reload(self):
        self.main.status("Reading local files...")
        for item in self.get_children():
            self.delete(item)
        for item in self.main.command(["list"]):
            self.insert('',END,text=item)
        self.main.status()

    def show_info(self,event=None):
        tag = self.selection()[0]
        file = self.item(tag,'text')
        if file:
            info = self.main.command(["info",file])
            names = info[0].split(",")
            values = info[1].split(",")
            msg = Tk()
            msg.title(file)
            table = ttk.Treeview(msg,columns=['value'],show='tree')
            for spec in list(zip(names,values)):
                table.insert('',END,text=spec[0],values=[spec[1].replace('"','')])
            table.column('#0',width=100)
            table.column('value',width=500)
            table.grid(row=0, column=0)

    def view_data(self,event=None):
        tag = self.selection()[0]
        file = self.item(tag,'text')
        if file:
            info = self.main.command(["info",file])
            names = info[0].split(",")
            values = info[1].split(",")
            index = names.index('Filepath')
            filename = values[index].replace('"','')
            tmy3 = TMY3(filename,coerce_year=2020)
            table = PandasDataFrame(title=file,data=tmy3.dataframe,parent=self)
            table.show()
            table.wait_window()

if __name__ == "__main__":

    root = Weather()
    try:
        ico = Image.open(__file__.replace(".py",".png"))
        photo = ImageTk.PhotoImage(ico)
        root.wm_iconphoto(True, photo)
    except Exception as err:
        print(f"ERROR [{__file__}]:",err)
    root.mainloop()
