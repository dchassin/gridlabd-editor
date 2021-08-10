"""Copyright (C) 2021 Regents of the Leland Stanford Junior University
See https://www.gridlabd.us/ for license, acknowledgments, credits, manuals, documentation, and tutorials.

"""

#
# Python modules
#
import sys, os
import timeit
import json
import subprocess
import webbrowser

#
# Console output
#
def stdout(*msg,file=sys.stdout):
    print(*msg,file=file)

def stderr(*msg,file=sys.stderr):
    print(*msg,file=file)

#
# GridLAB-D link
#
result = subprocess.run("/usr/local/bin/gridlabd --version=install".split(),capture_output=True)
if not result:
    stderr("ERROR: GridLAB-D is not installed on this system")
    quit(-1)
install_path = result.stdout.decode("utf-8").strip()
try:
    import gridlabd
except:
    stderr("ERROR: GridLAB-D is not installed for this python environment")
    quit(-1)

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

def TODO(msg="function not implemented yet",context=None):
    if not context:
        context = sys._getframe(1).f_code.co_name
    root.output(f"TODO [{context}]: {msg}")

class TkErrorCatcher:
    def __init__(self,func,subst,widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except SystemExit as msg:
            raise
        except Exception as err:
            root.exception()
tk.CallWrapper = TkErrorCatcher

#
# Global variables
#
title = gridlabd.__title__
version = gridlabd.__version__.split('-')[0]
build = gridlabd.version()["build"]
branch = gridlabd.version()["branch"] 
python = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ({sys.version_info.releaselevel})"
system = f"{os.uname().sysname} {os.uname().release} ({os.uname().machine})"
library = gridlabd.__file__

# 
# Load/initialize preferences
#
try:
    with open("gridlabd-preferences.conf","r") as f:
        preferences = json.load(f)
except:
    preferences = {
        "Welcome dialog enabled" : {
            "value" : False, # TODO: this should be True 
            "description" : "Show welcome dialog",
            },
        "Save output filename" : {
            "value" : "output.txt",
            "description" : "File name to save output on exit",
            },
        "Save output" : {
            "value" : True,
            "description" : "Enable saving output on exit",
            },
        "Reopen last file" : {
            "value" : True,
            "description" : "Enable reopening last file on initial open",
            },
        "Unused classes display enabled" : {
            "value" : False,
            "description" : "Enable display of unused classes in elements list",
            },
        "Class display enabled" : {
            "value" : True,
            "description" : "Enable display of classes in elements list",
            },
        "Traceback enabled" : {
            "value" : True,
            "description" : "Enable output of exception traceback data",
            },
        }


#
# Last run info
#
try:
    with open("gridlabd-appdata.conf","r") as f:
        application_data = json.load(f)
except:
    application_data = {
        "recent_files" : [],
}

#
# Platform specifics
#
if sys.platform == "darwin":
    try:
        from Foundation import NSBundle
    except:
        import pip
        pip.main(["install","pyobjc"])
        from Foundation import NSBundle
    bundle = NSBundle.mainBundle()
    if bundle:
        info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
        if info and info['CFBundleName'] == 'Python':
            info['CFBundleName'] = "GridLAB-D"
            info['CFBundleShortVersionString'] = f"{version}"
            info['CFBundleVersion'] = f"{build} {branch}"
            info['NSHumanReadableCopyright'] = gridlabd.copyright().split("\n\n")[1]

#
# Clipboard
#

class Clipboard:

    source_value = None
    source_type = None

    def __init__(self,main):
        self.main = main

    def copy(self,type,value,append=False):
        source_type = type
        source_value = value
        if not append:
            self.main.clipboard_clear()
        self.main.clipboard_append(json.dumps(value))

    def paste(self,type='*'):
        if type == '*' or type == source_type:
            return source_value
        else:
            return None

    def get_type(self):
        return source_type

    def get_value(self):
        return source_value

    def is_type(self,type):
        return type == source_type

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
        for file in application_data["recent_files"]:
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
        
        self.model_menu.add_command(label="Settings...", command=main.model_build)

        self.add_cascade(label="Model", menu=self.model_menu)

        # View menu
        self.view_menu = Menu(self,tearoff=False)
        self.add_cascade(label="View", menu=self.view_menu)
        self.view_menu_elements = Menu(self,tearoff=False)
        # main.view_module = BooleanVar()
        # self.view_menu_elements.add_checkbutton(label = "Module", onvalue = True, offvalue = False, variable = main.view_module, command = main.on_view_elements)
        main.view_class = BooleanVar()
        main.view_class.set(preferences["Class display enabled"]["value"])
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

#
# Main editor
#
class Editor(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.configure(background='lightgray')

        self.style = ttk.Style(self)
        self.style.configure('gridlabd.Treeview',
            padding = 3,
            selectmode = 'browse',
            )
        self.style.configure('gridlabd.Text',
            padding = 3,
            )

        self.clock = None
        self.configuration = None
        self.weather = None
        self.library = None
        self.filename = None
        self.model = None
        self.modify = None
        self.template = None
        # self.viewtype = 'objects' # 'objects','classes','modules','globals','schedules','filters'
        # self.viewstyle = 'name' # 'name'

        self.output_height = 300
        self.sidebar_width = 200
        self.modelview_layout = dict(x=0, y=0, width=self.sidebar_width, height=self.winfo_screenheight()-50-self.output_height)
        self.dataview_layout = dict(x=self.sidebar_width, y=0, width=int(self.winfo_screenwidth()/2-self.sidebar_width), height=self.winfo_screenheight()-self.output_height)
        self.outputview_layout = dict(x=0, y=int(self.winfo_screenheight()-50-self.output_height), width=int(self.winfo_screenwidth()/2), height=self.output_height)

        self.set_title()
        self.geometry(f'{int(self.winfo_screenwidth()/2)}x{self.winfo_screenheight()}')

        self.menubar = MenuBar(self)
        self.config(menu=self.menubar)

        self.treeview = ModelTree(self)
        self.treeview.place(x=self.modelview_layout['x'],y=self.modelview_layout['y'])

        self.dataview = DataView(self)
        self.dataview.place(x=self.dataview_layout['x'],y=self.dataview_layout['y'])

        self.outputview = OutputView(self)
        self.outputview.place(x=self.outputview_layout['x'],y=self.outputview_layout['y'])

        if len(sys.argv) > 1:
            self.filename = sys.argv[1]
            self.load_model()
            self.update()

        if sys.platform == "darwin":
            self.createcommand('::tk::mac::ShowPreferences',self.preferences)
            self.createcommand('::tk::mac::standardAboutPanel',self.help_about)
            self.createcommand('::tk::mac::Quit',self.file_exit)
            self.bind("<Meta_L><,>",self.preferences)

        if application_data['recent_files']:
            self.filename = application_data['recent_files'][0]
            self.load_model()


    def output(self,msg,end='\n'):
        self.outputview.append_text(msg,end=end)

    def warning(self,msg,end='\n'):
        self.outputview.append_text("WARNING: +"+msg,end=end)

    def error(self,msg,end='\n'):
        self.outputview.append_text("ERROR: "+msg,end=end)

    def exception(self,err=None,end='\n'):
        if not err:
            import traceback
            e_type,e_value,e_trace = sys.exc_info()
            text = f"EXCEPTION [{e_type.__name__}]: {e_value}"
            tag = '\n'.join(traceback.format_exception(e_type,e_value,e_trace))
            self.outputview.append_text(text,tag=tag)
        else:
            self.outputview.append_text(f"EXCEPTION: {err}",end=end)

    def preferences(self):
        PreferencesDialog(self,preferences)

    def load_model(self,filename=None):
        if not filename:
            filename = self.filename
        if not filename:
            return
        try:
            with open(filename,"r") as f: 
                try:
                    filedata = json.load(f)
                except Exception as errmsg:
                    messagebox.showerror(filename,f"unable to load file ({errmsg})")
                    return
            if self.set_model(filedata):
                self.set_title(filename)
        except Exception as msg:
            messagebox.showerror(filename,msg)

    def set_model(self,filedata):
        if not filedata \
                or not "application" in filedata.keys() \
                or filedata["application"] != "gridlabd-editor":
            messagebox.showerror(filename,f"file does not contain a valid {gridlabd.__title__} data file")
            return False
        self.model = filedata["data"]
        self.treeview.update_model()
        return True

    def save_model(self):
        with open(self.filename,"w") as f: json.dump(self.model,f,indent=4)

    def set_title(self,text=None):
        title = gridlabd.__title__
        if text:
            title = gridlabd.__title__ + " -- " + os.path.basename(text)
        self.title(title)

    def on_view_elements(self,event=None):
        self.treeview.update_model()

    #
    # File menu
    #
    def file_new(self,event=None):
        self.filename = None
        self.model = None
        self.load_model()

    def file_open(self,event=None):
        if self.filename:
            initialfile = os.path.basename(self.filename)
            defaultextension = os.path.splitext(self.filename)[1]
            initialdir = os.path.dirname(self.filename)
        else:
            initialfile = None
            defaultextension = ".gld"
            initialdir = os.getcwd()
        filename = filedialog.askopenfilename(
            initialfile = initialfile,
            defaultextension = defaultextension,
            initialdir = initialdir,
            )
        self.load_model(filename)

    def file_import(self,event=None):
        inputname = filedialog.askopenfilename()
        if not inputname:
            return
        import_dialog = ImportDialog(self,inputname=inputname)
        if import_dialog.result == True:
            self.filename = import_dialog.outputname
            inputext = os.path.splitext(inputname)[1][1:]
            outputext = os.path.splitext(import_dialog.outputname)[1][1:]
            if import_dialog.inputtype: 
                inputtype = f"{inputext}-{import_dialog.inputtype}"
            else: 
                inputtype = inputext
            if import_dialog.outputtype:
                outputtype = f"{outputext}-{import_dialog.outputtype}"
            else:
                outputtype = outputext
            command =  f"gridlabd convert -i {inputname} -o {import_dialog.outputname} -f {inputtype} -t {outputtype}"
            self.output(f"Running {command}...\n")
            result = subprocess.run(command.split(),capture_output=True)
            if result:
                self.output(result.stdout)
                self.output(result.stderr)
            else:
                self.error("command failed")
            if result and result.returncode == 0:
                self.load_model()
            else:
                messagebox.showerror("File import",result.stderr)

    def file_close(self,event=None):
        TODO()

    def file_save(self,event=None):
        self.save_model()

    def file_saveas(self,event=None):
        if self.filename:
            initialfile = os.path.basename(self.filename)
            defaultextension = os.path.splitext(self.filename)[1]
            initialdir = os.path.dirname(self.filename)
        else:
            initialfile = "untitled.json"
            defaultextension = ".json"
            initialdir = os.getcwd()
        self.filename = filedialog.asksaveasfilename(
            initialfile = initialfile,
            defaultextension = defaultextension,
            initialdir = initialdir,
            )
        self.save_model()
        self.update()

    def file_export(self,event=None):
        TODO()

    def file_exit(self,event=None):

        # save outputview to output save file
        if preferences["Save output"]["value"]:
            with open(preferences["Save output filename"]["value"],"w") as f:
                f.write(self.outputview.get(1.0,"end-1c"))
        with open("gridlabd-appdata.conf","w") as f:
            json.dump(application_data,f)
        self.destroy()

    #
    # Edit menu
    #

    def undo(self,event=None):
        TODO()

    def redo(self,event=None):
        TODO()

    def cut(self,event=None):
        TODO()

    def copy(self,event=None):
        focus = self.focus_get()
        item = focus.get_selected()
        # item[0] is self.filename
        text = self.model
        for ref in item["context"]:
            text = text[ref]
        self.clipboard_clear()
        self.clipboard_append(json.dumps(text,indent=4))

    def paste(self,event=None):
        TODO()

    def insert(self,event=None):
        TODO()

    def delete(self,event=None):
        TODO()

    def paste_special(self,event=None):
        TODO()

    #
    # Model menu
    #
    def model_build(self,event=None):
        self.output(f"\nStarting {os.path.split(self.filename)[1]}...\n")
        tic = timeit.default_timer()
        command = ["gridlabd",self.filename]
        if self.template:
            command.append(self.template)
        command.extend(["-D","show_progress=FALSE"])
        result = subprocess.run(command,capture_output=True)
        toc = timeit.default_timer()
        self.output(result.stderr)
        self.output(result.stdout)
        if result.returncode:
            self.error(f"\nreturn code {result.returncode}!\n")
        else:
            self.output(f"\nSimulation done\n")
        self.output(f"Elapsed time: {toc-tic:.2g} seconds\n")

    def model_clock(self,event=None):
        msg = Tk()
        msg.title("Clock")
        table = ttk.Treeview(msg,columns=['value'],show='tree')
        table.insert('',END,text='Time zone',values=[self.model['globals']['timezone_locale']['value']])
        table.insert('',END,text='Start time',values=[self.model['globals']['starttime']['value']])
        table.insert('',END,text='Stop time',values=[self.model['globals']['stoptime']['value']])
        table.column('#0',width=100)
        table.column('value',width=500,stretch=YES)
        table.grid(row=0, column=0)

    def model_configure(self,event=None):
        messagebox.showerror(f"Configure",f"Configuration is not available")

    def model_modify(self,event=None):
        messagebox.showerror(f"Configure",f"Modify is not available")

    def model_template_manager(self,event=None):
        os.system("/usr/local/bin/python3 /usr/local/share/gridlabd/template.py &")

    def model_template_choose(self,event=None):
        initialdir = "/usr/local/share/gridlabd/template"
        if not os.path.exists(initialdir):
            self.model_template_manager
        template = filedialog.askopenfilename(
            initialfile = self.template,
            defaultextension = ".glm",
            initialdir = initialdir,
            )
        if template:
            self.template = template
            self.output(f"Template {self.template} added")

    def model_library_manager(self,event=None):
        os.system("/usr/local/bin/python3 /usr/local/share/gridlabd/library.py &")

    def model_library_choose(self,event=None):
        initialdir = "/usr/local/share/gridlabd/library"
        if not os.path.exists(initialdir):
            self.model_library_manager
        library = filedialog.askopenfilename(
            initialfile = self.library,
            defaultextension = ".glm",
            initialdir = initialdir,
            )
        if library:
            self.library = library
            self.output(f"Library {self.library} added")

    def model_weather_manager(self,event=None):
        os.system("/usr/local/bin/python3 /usr/local/share/gridlabd/weather.py &")

    def model_weather_choose(self,event=None):
        initialdir = "/usr/local/share/gridlabd/weather"
        if not os.path.exists(initialdir):
            self.model_weather_manager
        weather = filedialog.askopenfilename(
            initialfile = self.weather,
            defaultextension = ".tmy3",
            initialdir = initialdir,
            )
        if weather:
            self.weather = weather
            self.output(f"Weather {self.weather} added")

    #
    # Help
    #
    def help_about(self):
        messagebox.showinfo(title, f"Version: {version}-{build}\nSource: {branch}\nLibrary: {library}\n\nSystem: {system}\nPython: {python}")

    def help_license(self):
        title = gridlabd.__title__
        license = gridlabd.license()
        msg = Tk()
        msg.title(f"{title} License")
        txt = Label(msg,text=license, anchor=W, justify=LEFT)
        txt.grid(row=0, column=0)
        msg.mainloop()

    def help_documentation(self):
        webbrowser.open(f"https://docs.gridlabd.us/",new=2)

    def help_reportissue(self):
        webbrowser.open(f"https://issues.gridlabd.us/new/choose",new=2)
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
                iid = idlist[0]
                item = self.item_index[iid]
                itype = item["type"]
                if itype == "object":
                    name = self.item.get(iid,'text')
                    self.main.dataview.show_object(name)

    def get_selected(self):
        result = []
        for iid in self.selection():
            result.append(self.item_index[iid])
        return result

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

#
# Editor output view
#
class OutputView(Frame):

    def __init__(self,main,*args,**kwargs):
        
        super().__init__(height = main.outputview_layout['height'],
            width = main.outputview_layout['width'],
            *args,**kwargs)
        
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.text = Text(self,font = Font(family="Courier",size=12),wrap=NONE)
        self.text.grid(row=0,column=0,sticky="nsew",padx=2,pady=2)
        
        yscroll = ttk.Scrollbar(self,orient="vertical",command=self.text.yview)
        yscroll.grid(row=0,column=1, sticky="nsew")
        self.text["yscrollcommand"] = yscroll.set
        
        xscroll = ttk.Scrollbar(self,orient="horizontal",command=self.text.xview)
        yscroll.grid(row=1,column=0, sticky="nsew")
        self.text["xscrollcommand"] = xscroll.set
        
        self.tags = {}
        self.text.tag_config("blue",foreground="blue")
        self.text.tag_bind("blue","<Button-1>",self.on_click)
        self.text.tag_config("red",foreground="red")
        self.text.tag_bind("red","<Button-1>",self.on_click)

        self.append_text(f"{title} {version}-{build} ({branch}) {system}\n{__doc__}")

    def on_click(self,event):
        pos = event.widget.index("@%s,%s"%(event.x,event.y))
        line = int(float(str(pos)))
        if self.tags[line]["end"]:
            self.tags[line]["end"]
            self.text.delete(f"{line+1}.0",self.tags[line]["end"])
        else:
            self.text.insert(f"{line+1}.0",self.tags[line]["text"])
            self.tags[line]["end"] = f"{line+1}.0+{len(self.tags[line]['text'])}c"

    def append_text(self,text,end='\n',tag=None,color="red"):
        if not tag:
            self.text.insert(END,text+end)
        else:
            line = int(float(str(self.text.index(END)))-1)
            self.text.insert(END,text+end,color)
            self.tags[line] = {"text":tag,"end":None}
        self.text.see(END)
        self.text.update()

#
# Preferences dialog
#
class PreferencesDialog(simpledialog.Dialog):

    def __init__(self,parent,preferences):
        Toplevel.__init__(self, parent)
        self.parent = parent
        self.transient(parent)
        self.title("Preferences")

        tree = ttk.Treeview(self,columns=["value","description"])
        tree.heading("#0",text="Setting")
        tree.column("#0",width=150)
        tree.heading("value",text="Value")
        tree.column("value",width=200)
        tree.heading("description",text="Description")
        tree.column("description",width=450)
        tree.grid(row=0,column=1)
        for name in sorted(preferences.keys()):
            value = preferences[name]
            item = tree.insert('',END,text=name,values=[str(value["value"]),value["description"]])

        self.tree = tree

        Button(self, text="Save", width=10, command=self.on_save, default=DISABLED).grid(row=3,column=1,padx=10,pady=10)

        self.bind("<Double-1>",self.on_doubleclick)

        self.grab_set()
        self.wait_window(self)

    def on_doubleclick(self,event=None):
        item = self.tree.selection()[0]
        name = self.tree.item(item)['text']
        pref = preferences[name]
        value = pref['value']
        description = pref['description']
        ptype = type(value)
        if ptype is bool:
            ask = messagebox.askquestion
            if value:
                kwds = dict(default="yes")
            else:
                kwds = dict(default="no")
            def answer(value): return bool(value=="yes")
        elif ptype is float:
            ask = simpliedialog.askfloat
            kwds = dict(initialvalue=value)
            def answer(value): return float(value)
        elif ptype is int:
            ask = simpledialog.askinteger
            kwds = dict(initialvalue=value)
            def answer(value): return int(value)
        else:
            ask = simpledialog.askstring
            kwds = dict(initialvalue=value)
            def answer(value): return str(value)
        value = answer(ask(name,description,**kwds))
        preferences[name]['value'] = value
        self.tree.item(item,values=[preferences[name]['value'],preferences[name]['description']])
        self.update()

    def on_save(self):
        with open("gridlabd-preferences.conf","w") as f:
            json.dump(preferences,f,indent=4)
        self.destroy()

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

        config = subprocess.run(f"/usr/local/bin/python3 {install_path}/share/gridlabd/{inputext[1:]}2{outputext[1:]}.py --config".split(),capture_output=True)
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

#
# Main app startup
#
if __name__ == "__main__":
    root = Editor()
    if preferences["Welcome dialog enabled"]["value"]:
        messagebox.showinfo("Welcome",
            f"""{title}\n{version}-{build} ({branch}) {system}\n{__doc__}
            """)
    root.mainloop()
