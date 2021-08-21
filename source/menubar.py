import os, sys, json
import preferences

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
# Menu
#
class MenuBar(Menu):

    def __init__(self, main):
        Menu.__init__(self, main)

        # File menu
        self.file_menu = Menu(self, tearoff=False)
        self.file_menu.add_command(label="New", underline=0, command=main.file_new, accelerator="Command-N")  
        main.bind("<Meta_L><n>",main.file_new)
        self.file_menu.add_command(label="Open", command=main.file_open, accelerator="Command-O")
        main.bind("<Meta_L><o>",main.file_open)
        self.file_menu_recent = Menu(self, tearoff=False)
        for file in main.application_data["recent_files"]:
            self.file_menu_recent.add_command(label=file)
        self.file_menu.add_cascade(label="Open recent",menu=self.file_menu_recent)
        main.bind("<Meta_L><o>",main.file_open)
        self.file_menu.add_command(label="Import", command=main.file_import, accelerator="Shift-Command-O")
        main.bind("<Meta_L><O>",main.file_import)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Close", command=main.file_new, accelerator="Command-W")    
        main.bind("<Meta_L><w>",main.file_close)
        self.file_menu.add_command(label="Save", command=main.file_save, accelerator="Command-S")  
        main.bind("<Meta_L><s>",main.file_save)
        self.file_menu.add_command(label="Save as", command=main.file_saveas, accelerator="Command-A")    
        main.bind("<Meta_L><a>",main.file_saveas)
        self.file_menu.add_command(label="Export", command=main.file_new, accelerator="Shift-Command-S")    
        main.bind("<Meta_L><S>",main.file_new)
        if sys.platform != "darwin":
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Exit",command=main.file_exit, accelerator="Command-Q")
            main.bind("<Meta_L><q>",main.file_exit)
        self.add_cascade(label="File", menu=self.file_menu)
        
        # Edit menu
        self.edit_menu = Menu(self, tearoff=False)  
        self.edit_menu.add_command(label="Undo", accelerator="Command-Z", command=main.undo)  
        main.bind("<Meta_L><z>",main.redo)
        self.edit_menu.add_command(label="Redo", accelerator="Command-Y", command=main.redo)  
        main.bind("<Meta_L><y>",main.redo)
        self.edit_menu.add_separator()     
        self.edit_menu.add_command(label="Cut", accelerator="Command-X", command=main.cut)  
        main.bind("<Meta_L><x>",main.cut)
        self.edit_menu.add_command(label="Copy", accelerator="Command-C", command=main.copy)  
        main.bind("<Meta_L><c>",main.copy)
        self.edit_menu.add_command(label="Paste", accelerator="Command-V", command=main.paste)
        main.bind("<Meta_L><v>",main.paste)
        self.edit_menu.add_command(label="Paste special", accelerator="Shift-Command-V", command=main.paste_special)
        main.bind("<Meta_L><V>",main.copy)
        if sys.platform != "darwin":
            self.edit_menu.add_separator()     
            self.edit_menu.add_command(label="Preferences", accelerator="Command-,", command=main.preferences)
            main.bind("<Meta_L><,>",main.preferences)
        self.add_cascade(label="Edit", menu=self.edit_menu) 

        # Model menu
        self.model_menu = Menu(self, tearoff=False)
        self.model_menu.add_command(label="Build", command=main.model_build, accelerator="Command-B",)
        main.bind("<Meta_L><b>",main.model_build)

        self.model_menu.add_separator()     
        
        self.model_menu.add_command(label="Run", command=main.model_build, accelerator="Command-R",)
        main.bind("<Meta_L><r>",main.model_build)
        
        self.model_menu.add_separator()     
        self.model_menu.add_command(label="Clock", command=main.model_clock, accelerator="Command-K")
        main.bind("<Meta_L><k>",main.model_clock)

        self.model_menu.add_command(label="Configure", command=main.model_configure, accelerator="Command-D")
        main.bind("<Meta_L><d>",main.model_configure)

        self.model_menu.add_command(label="Modify", command=main.model_modify, accelerator="Command-M")
        main.bind("<Meta_L><m>",main.model_modify)

        self.model_library = Menu(self,tearoff=False)
        self.model_library.add_command(label="Manager...", command=main.model_library_manager)
        self.model_library.add_command(label="Choose...", command=main.model_library_choose)
        self.model_menu.add_cascade(label="Library", menu=self.model_library)

        self.model_template = Menu(self,tearoff=False)
        self.model_template.add_command(label="Manager...", command=main.model_template_manager)
        self.model_template.add_command(label="Choose...", command=main.model_template_choose)
        self.model_menu.add_cascade(label="Template", menu=self.model_template)

        # Model weather menu
        self.model_weather = Menu(self,tearoff=False)
        self.model_weather.add_command(label="Manager...", command=main.model_weather_manager)
        self.model_weather.add_command(label="Choose...", command=main.model_weather_choose)
        self.model_menu.add_cascade(label="Weather", menu=self.model_weather)
        
        self.model_menu.add_separator()     
        
        self.model_menu.add_command(label="Settings...", command=main.model_settings)

        self.add_cascade(label="Model", menu=self.model_menu)

        # View menu
        self.view_menu = Menu(self,tearoff=False)
        self.add_cascade(label="View", menu=self.view_menu)
        self.view_menu_elements = Menu(self,tearoff=False)
        # main.view_module = BooleanVar()
        # self.view_menu_elements.add_checkbutton(label = "Module", onvalue = True, offvalue = False, variable = main.view_module, command = main.on_view_elements)
        main.view_class = BooleanVar()
        main.view_class.set(preferences.get("Class display enabled"))
        self.view_menu_elements.add_checkbutton(label="Class", onvalue=True, offvalue=False, variable=main.view_class, command = main.on_view_elements)
        # main.view_group = BooleanVar()
        # self.view_menu_elements.add_checkbutton(label="Group", onvalue=True, offvalue=False, variable=main.view_group, command = main.on_view_elements)
        self.view_menu.add_cascade(label="Elements",menu=self.view_menu_elements)

        # Help menu
        self.help_menu = Menu(self, tearoff=False)
        if sys.platform != "darwin":
            self.help_menu.add_command(label="About", command=main.help_about)
        self.help_menu.add_command(label="License", command=main.help_license)
        self.help_menu.add_command(label="Documentation", command=main.help_documentation)
        self.help_menu.add_command(label="Report issue", command=main.help_reportissue)
        self.add_cascade(label="Help", menu=self.help_menu)  

        main.config(menu=self)

        main.bind_all("<Key>",self.key_event)

        self.main = main

    def key_event(self,event):
        # stderr("Key event: ",event)
        return

