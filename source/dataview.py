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

import utilities

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
        for name,data in self.main.elements['globals'].items():
            if 'description' in data:
                description = data['description']
            else:
                description = ''
            self.insert('',END,
                text=f"globals/{name}",
                values=[name,data['value'],description])
        self.main.update()

    def edit_global(self,item,info):
        varname = info[1]
        var = self.main.elements['globals'][varname]
        if var['access'] != 'PUBLIC':
            messagebox.showerror(f"Global set error",f"Global {varname} cannot be changed")
            return
        value = var['value']
        edit = simpledialog.askstring(title=f"Model global",prompt=f"Enter new value for global '{varname}'",initialvalue=value)
        var['value'] = edit
        self.set(item,"#2",edit)

    def show_class(self,name):
        self.clear_table()
        self.object = name
        obj = self.main.elements['objects'][name]
        for prop,specs in obj.items():
            if not type(specs) is dict:
                continue
            value = specs["type"]
            options = []
            if "access" in specs:
                options.append(specs['access'])
            if "flags" in specs:
                options.append(specs['flags'])
            if "default" in specs:
                options.append(f"default \"{specs['default']}\"")
            options = ", ".join(options)
            if "descriptions" in specs:
                description = specs["description"]
                description += f" ({options})"
            else:
                description = options
            self.insert('',END,prop,
                text=f"objects/{name}/{prop}",
                values=[prop,value,description])
        self.main.update()

    def show_object(self,name,data):
        self.clear_table()
        self.object = name
        print(f"{self}.show_object({name},{data})",flush=True)
        if data["class"] in self.main.elements["classes"]:
            oclass = self.main.elements['classes'][data['class']]
        elif "." in data["class"]:
            class_spec = data["class"].split(".")
            module = class_spec[0]
            oclass = utilities.classes(module)[class_spec[1]]
        else:
            oclass = {} # no info on this object's class
        for prop,value in data.items():
            if prop in oclass and 'description' in oclass[prop]:
                info = oclass[prop]
                description = info['description'][0].upper() + info['description'][1:]
                description += " (" + ' '.join([info['flags'].lower(),info['access'].lower(),info['type'].lower()])
                if "unit" in info:
                    description += " in " + info["unit"]
                description += ")"
            else:
                description = ""
            self.insert('',END,prop,
                text=f"objects/{name}/{prop}",
                values=[prop.title(),value,description])
        self.main.update()

    def edit_object(self,item,info):
        objname = info[1]
        propname = info[2]
        if propname in ['id','class']:
            messagebox.showerror(f"Property set error",f"Property {propname} cannot be changed")
            return
        obj = self.main.elements['objects'][objname]
        oclass = self.main.elements['classes'][obj['class']]
        value = obj[propname]
        ptype = oclass[propname]['type']
        if ptype in ask_dialogs:
            edit = ask_dialogs[ptype](title=f"Object {objname}",prompt=f"Enter new value for property '{propname}'",initialvalue=value)
        else:
            edit = simpledialog.askstring(title=f"Object {objname}",prompt=f"Enter new value for property '{propname}'",initialvalue=value)
        obj[propname] = edit
        self.set(propname,"#2",edit)

    def on_doubleclick(self,event):
        row = self.identify_row(event.y)
        if not row in ["class"]:
            column = self.identify_column(event.x)
            entry = StringEdit(self,row,column)
            entry.wait_window()
            if entry.data:
                specs = entry.data["text"].split("/")
                values = entry.data["values"]
                self.main.elements[specs[0]][specs[1]][specs[2]] = values[1]

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

class StringEdit(Entry):
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


ask_dialogs = {
    "set" : AskSetDialog,
}
 