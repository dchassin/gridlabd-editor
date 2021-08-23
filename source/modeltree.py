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
# Editor model tree
#
class ModelTree(ttk.Treeview):

    def load_dict(self,parent,elements):
        for key,values in elements.items():
            iid = self.insert(parent,END,text=key)
            self.item_index[iid] = values

    tags = {
        "clock" : {
            "label" : "Clock",
            "single" : True,
        },
        "input" : {
            "label" : "Input files",
            "loader" : load_dict,
        },
        "output" : {
            "label" : "Output files",
            "loader" : load_dict,
        },
        "globals" : {
            "label" : "Global variables",
        },
        "include" : {
            "label" : "Include files",
            "loader" : load_dict,
        },
        "filter" : {
            "label" : "Filters",
            "loader" : load_dict,
        },
        "schedule" : {
            "label" : "Schedules",
            "loader" : load_dict,
        },
        "class" : {
            "label" : "Classes",
            "loader" : load_dict,
        },
        "template" : {
            "label" : "Templates",
            "loader" : load_dict,
        },
        "module" : {
            "label" : "Modules",
            "loader" : load_dict,
        },
        "object" : {
            "label" : "Objects",
            "loader" : load_dict,
        },
        "python" : {
            "label" : "Python code",
        },
        "python_file" : {
            "label" : "Python file",
        },
        "comment" : {
            "label" : "Annotation",
        },
        #
        # Modules
        #
        "assert" :
        {
            "label" : "Validators",
            "loader" : load_dict,
        },
        "climate" :
        {
            "label" : "Weather",
            "loader" : load_dict,
        },
        "commercial" : {
            "label" : "Offices",
            "loader" : load_dict,
        },
        "generators" : {
            "label" : "Generation",
            "loader" : load_dict,
        },
        "industrial" : {
            "label" : "Industry",
            "loader" : load_dict,
        },
        "influxdb" : {
            "label" : "Influx Database",
            "loader" : load_dict,
        },
        "market" : {
            "label" : "Retail market",
            "loader" : load_dict,
        },
        "optimize" : {
            "label" : "Optimizers",
            "loader" : load_dict,
        },
        "mysql" : {
            "label" : "MySQL Database",
            "loader" : load_dict,
        },
        "reliability" : {
            "label" : "Reliability",
            "loader" : load_dict,            
        },
        "resilience" : {
            "label" : "Resilience",
            "loader" : load_dict,            
        },
        "powerflow" : {
            "label" : "Network",
            "loader" : load_dict,
        },
        "residential" : {
            "label" : "Residences",
            "loader" : load_dict,
        },
        "revenue" : {
            "label" : "Tariffs",
            "loader" : load_dict,
        },
        "tape" :
        {
            "label" : "CSV Files",
            "loader" : load_dict,
        },
    }

    def __init__(self,main):
        ttk.Treeview.__init__(self,main,style='gridlabd.Treeview',
            height = main.modelview_layout['height'],
            )
        self.main = main
        self.bind("<ButtonRelease-1>",self.on_select)
        self.bind("<Button-2>",self.show_popup)
        self.update_model()

    def show_popup(self,event):
        iid = self.identify_row(event.y)
        popup = Menu(self,tearoff=0);
        insert = Menu(self,tearoff=0);
        for item,values in self.tags.items():
            state = None
            if self.main.model and "single" in values.keys() and values["single"] \
                    and item in list(map(lambda x: x["type"],self.main.model)):
                state = DISABLED
            insert.add_command(label=values["label"],command=self.main.insert,state=state)
        popup.add_cascade(label="Insert",menu=insert)
        if iid:
            self.selection_set(iid)
            popup.add_command(label="Copy",command=self.main.copy)
            popup.add_command(label="Cut",command=self.main.cut)
            popup.add_command(label="Paste",command=self.main.paste)
            popup.add_command(label="Delete",command=self.main.delete)
        try:
            popup.tk_popup(event.x_root,event.y_root,0)
        finally:
            popup.grab_release()

    def clear_tree(self):
        self.heading('#0',text='Element')
        for item in self.get_children(""):
            self.delete(item)
        self.item_index = {}

    def update_model(self):
        """styles in ['name','rank','class','parent']"""
        self.clear_tree()
        if self.main.model:
            self.insert_model()
        self.main.update()

    def get_label(self,tag):
        if tag not in self.tags.keys():
            raise Exception(f"Model component '{tag}' not recognized")
        return self.tags[tag]["label"]

    def insert_model(self,root=""):
        self.heading('#0',text='Model Components')
        for item in self.main.model:
            iid = self.insert(root,END,text=self.get_label(item["type"]))
            self.load_values(iid,item)

    def load_values(self,iid,item):
        itype = item["type"]
        if "loader" in self.tags[itype]:
            self.tags[itype]["loader"](self,iid,item["values"])
            self.item_index[iid] = item

    def on_select(self,event):
        if self.main.model:
            idlist = self.get_selected()
            if len(idlist) == 1:
                self.main.show_modelitem(idlist[0])

    def get_selected(self):
        result = []
        for iid in self.selection():
            result.append(self.item_index[iid])
        return result

