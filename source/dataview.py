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

class DataView(ttk.Treeview):

    def __init__(self,main):
        columns = ['Property','Value','Description']
        widths = {'Property':150,'Value':250,'Description':main.dataview_layout['width']-306}
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

    def show_class(self,name):
        self.clear_table()
        self.object = name
        obj = self.main.model['classes'][name]
        for prop,specs in obj.items():
            if not type(specs) is dict:
                continue
            value = specs["type"]
            options = []
            if "access" in specs.keys():
                options.append(specs['access'])
            if "flags" in specs.keys():
                options.append(specs['flags'])
            if "default" in specs.keys():
                options.append(f"default \"{specs['default']}\"")
            options = ", ".join(options)
            if "descriptions" in specs.keys():
                description = specs["description"]
                description += f" ({options})"
            else:
                description = options
            self.insert('',END,prop,
                text=f"objects/{name}/{prop}",
                values=[prop,value,description])
        self.main.update()

    def show_object(self,name):
        self.clear_table()
        self.object = name
        obj = self.main.model['objects'][name]
        for prop,value in obj.items():
            oclass = self.main.model['classes'][obj['class']]
            if prop in oclass.keys() and 'description' in oclass[prop]:
                description = oclass[prop]['description']
            else:
                description = ""
            self.insert('',END,prop,
                text=f"objects/{name}/{prop}",
                values=[prop,value,description])
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

    def edit_object(self,item,info):
        objname = info[1]
        propname = info[2]
        if propname in ['id','class']:
            messagebox.showerror(f"Property set error",f"Property {propname} cannot be changed")
            return
        obj = self.main.model['objects'][objname]
        oclass = self.main.model['classes'][obj['class']]
        value = obj[propname]
        ptype = oclass[propname]['type']
        if ptype in ask_dialogs.keys():
            edit = ask_dialogs[ptype](title=f"Object {objname}",prompt=f"Enter new value for property '{propname}'",initialvalue=value)
        else:
            edit = simpledialog.askstring(title=f"Object {objname}",prompt=f"Enter new value for property '{propname}'",initialvalue=value)
        obj[propname] = edit
        self.set(propname,"#2",edit)

    def on_doubleclick(self,event):
        item = self.selection()[0]
        info = self.item(item)['text'].split('/')
        if not info:
            return
        elif info[0] == 'globals':
            self.edit_global(item,info)
        elif info[0] == 'objects':
            self.edit_object(item,info)

    def get_selected(self):
        tag = self.selection()[0]
        if tag:
            return {
                "file" : self.main.filename,
                "context" : self.item(tag,'text').split('/'),
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
 