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

class GlobalView(ttk.Treeview):

    def __init__(self,main):
        columns = ['Variable','Value','Description']
        widths = {'Variable':150,'Value':250,'Description':main.dataview_layout['width']-306}
        ttk.Treeview.__init__(self,main,style='gridlabd.Treeview',
            height = main.dataview_layout['height'],
            columns = columns,
            )
        self['show'] = 'headings'
        for item in columns:
            self.heading(item,text=item)
            self.column(item,width=widths[item])
        self.bind("<Double-1>",self.on_doubleclick)
        self.target = None
        self.main = main

    def clear_table(self):
        self.heading('#0',text='(none)')
        for item in self.get_children():
            self.delete(item)

    def show_globals(self):
        self.clear_table()
        self.object = None
        for name,data in self.main.model['globals'].items():
            if 'description' in data.keys():
                description = data['description']
            else:
                description = ''
            self.insert('',END,
                text=f"globals/{name}",
                values=[name,data['value'],description])
        self.main.update()

    def edit_global(self,item,info):
        varname = info[1]
        var = self.main.model['globals'][varname]
        if var['access'] != 'PUBLIC':
            messagebox.showerror(f"Global set error",f"Global {varname} cannot be changed")
            return
        value = var['value']
        edit = simpledialog.askstring(title=f"Model global",prompt=f"Enter new value for global '{varname}'",initialvalue=value)
        var['value'] = edit
        self.set(item,"#2",edit)

    def on_doubleclick(self,event):
        item = self.selection()[0]
        info = self.item(item)['text'].split('/')
        self.edit_global(item,info)

    def get_selected(self):
        tag = self.selection()[0]
        if tag:
            return {
                "type" : "global",
                "value" : self.item(tag,'value')[1],
                }

#
# Property editing dialogs
#
class AskSetDialog(simpledialog.Dialog):

    def __init__(self,parent,title,prompt,text):
        Toplevel.__init__(self, parent)
        self.parent = parent
        self.transient(parent)
        self.title(title)
        Label(text=prompt).pack(side=TOP)
        Text(text=text).pack(side=TOP)
        Button(text="Save").pack(side=TOP)
        self.grab_set()
        self.wait_window(self)

ask_dialogs = {
    "set" : AskSetDialog,
}
 