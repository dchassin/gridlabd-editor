"""
Copyright (C) 2021 Regents of the Leland Stanford Junior University

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
import datetime
import re

#
# Console output
#
def stdout(*msg,file=sys.stdout):
    print(*msg,file=file)

def stderr(*msg,file=sys.stderr):
    print(*msg,file=file)

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

try:
    from PIL import Image, ImageTk
except Exception as err:
    if system == 'Darwin':
        stderr(f"ERROR: {err}. Did you remember to run 'brew install pillow'?",file=sys.stderr)
    else:
        stderr(f"ERROR: {err}. Did you remember to install pillow support?",file=sys.stderr)
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
            root.exception(backup=1)
tk.CallWrapper = TkErrorCatcher

#
# GridLAB-D Editor modules
#
editor_path = os.path.split(__file__)[0]
sys.path.append(editor_path)

import runner
import preferences
import clipboard
import menubar
import modeltree
import dataview
import globalview
import outputview
import importdialog
import exportdialog

#
# GridLAB-D link
#
result = subprocess.run(f"{preferences.Preferences().get('GridLAB-D executable')} --version=install".split(),capture_output=True)
if not result:
    stderr("ERROR: GridLAB-D is not installed on this system")
    quit(-1)
install_path = result.stdout.decode("utf-8").strip()
bin_path = install_path + "/bin"
lib_path = install_path + "/lib/gridlabd"
include_path = install_path + "/include/gridlabd"
share_path = install_path + "/share/gridlabd"
try:
    import gridlabd
except:
    stderr("ERROR: GridLAB-D is not installed for this python environment")
    quit(-1)
copyright = subprocess.run(f"{preferences.Preferences().get('GridLAB-D executable')} --copyright".split(),capture_output=True).stdout.decode('utf-8')

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
# Application data
#
try:
    with open("gridlabd-appdata.conf","r") as f:
        application_data = json.load(f)
except:
    application_data = {
        "recent_files" : [],
        "traceback" : "/dev/stderr",
}
try:
    TRACEBACK = open(application_data["traceback"],"w")
except:
    error(f"unable to open traceback file '{traceback}'")
    TRACEBACK = None

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
            info['CFBundleExecutable'] = "GridLAB-D"
            info['CFBundleShortVersionString'] = f"{version}"
            info['CFBundleVersion'] = f"{build} {branch}"
            info['NSHumanReadableCopyright'] = gridlabd.copyright().split("\n\n")[1]

#
# Main editor
#
class Editor(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.configure(background='lightgray')
        self.preferences = preferences.Preferences()

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
        self.elements = {
            "classes":{},
            "modules":{},
            "objects":{},
            "globals":{}
            }
        # self.viewtype = 'objects' # 'objects','classes','modules','globals','schedules','filters'
        # self.viewstyle = 'name' # 'name'

        self.output_height = 300
        self.sidebar_width = 200
        self.modelview_layout = dict(x=0, y=0, width=self.sidebar_width, height=self.winfo_screenheight()-50-self.output_height)
        self.dataview_layout = dict(x=self.sidebar_width, y=0, width=int(self.winfo_screenwidth()/2-self.sidebar_width), height=self.winfo_screenheight()-self.output_height)
        self.outputview_layout = dict(x=0, y=int(self.winfo_screenheight()-50-self.output_height), width=int(self.winfo_screenwidth()/2), height=self.output_height)

        self.set_title()
        self.geometry(f'{int(self.winfo_screenwidth()/2)}x{self.winfo_screenheight()}')

        self.application_data = application_data
        self.menubar = menubar.MenuBar(self)
        self.config(menu=self.menubar)

        self.treeview = modeltree.ModelTree(self)
        self.treeview.place(x=self.modelview_layout['x'],y=self.modelview_layout['y'])

        self.dataview = dataview.DataView(self)
        self.dataview.place(x=self.dataview_layout['x'],y=self.dataview_layout['y'])

        self.outputview = outputview.OutputView(self)
        self.outputview.append_text(f"{copyright}\n{__doc__}\n\n{title} {version}-{build} ({branch}) {system}\n\n".replace('\n\n','\n'))
        self.outputview.place(x=self.outputview_layout['x'],y=self.outputview_layout['y'])

        if len(sys.argv) > 1:
            self.filename = sys.argv[1]
            self.load_model()
            self.update()

        if sys.platform == "darwin":
            self.createcommand('::tk::mac::ShowPreferences',self.preferences.dialog)
            self.createcommand('::tk::mac::standardAboutPanel',self.help_about)
            self.createcommand('::tk::mac::Quit',self.file_exit)
            self.bind("<Meta_L><,>", self.preferences.dialog)

        if application_data['recent_files']:
            self.filename = application_data['recent_files'][0]
            self.load_model()

    def output(self,msg,end='\n',noblank=False):
        # print(f"output = [{msg}] -->","["+(re.sub('[\r\n]+','\n',msg.strip('\n')) if noblank else msg)+"]",file=sys.stderr,flush=True)
        self.outputview.append_text((re.sub('[\r\n]+','\n',msg.strip('\n')) if noblank else msg),end=end)

    def warning(self,msg,end='\n',noblank=False):
        if msg:
            self.outputview.append_text("WARNING: +"+(re.sub('[\r\n]+','\n',msg.strip('\n')) if noblank else msg),end=end)

    def error(self,msg,end='\n',noblank=False):
        # print(f"error = [{msg}]",file=sys.stderr,flush=True)
        if msg:
            self.outputview.append_text("ERROR: "+(re.sub('[\r\n]+','\n',msg.strip('\n')) if noblank else msg),end=end)

    def exception(self,backup=0,err=None,end='\n'):
        if not err:
            import traceback
            e_type,e_value,e_trace = sys.exc_info()
            e_origin = e_trace
            while e_origin.tb_next:
                e_origin = e_origin.tb_next
            e_file = os.path.basename(e_origin.tb_frame.f_code.co_filename)
            e_line = e_origin.tb_lineno
            text = f"EXCEPTION [{e_type.__name__}@{e_file}/{e_line}]: {e_value}"
            tag = '\n'.join(traceback.format_exception(e_type,e_value,e_trace))
            self.outputview.append_text(text,tag=tag)
            if TRACEBACK:
                print(f"EXCEPTION [{e_type.__name__}@{e_file}/{e_line}]: {e_value}",file=TRACEBACK)
                traceback.print_tb(e_trace,file=TRACEBACK)
                TRACEBACK.flush()
        else:
            if TRACEBACK:
                traceback.print_exception(err,file=TRACEBACK,flush=True)
            self.outputview.append_text(f"EXCEPTION: {err}",end=end)

    def show_modelitem(self,iid):
        item = self.treeview.item_index[iid]
        # print("item",item,flush=True)
        if "type" in item and "data" in item:
            callname = "show_"+item["type"]
            if hasattr(self.dataview,callname):
                display = getattr(self.dataview,callname)
                name = self.treeview.item(iid,'text')
                display(name,item["data"])

    def load_model(self,filename=None):
        if not filename:
            filename = self.filename
        if not filename:
            return
        try:
            with open(filename,"r") as f: 
                filedata = json.load(f)
            if self.set_model(filedata):
                self.set_title(filename)
        except Exception as msg:
            self.exception()
            # messagebox.showerror(filename,msg)

    def set_model(self,filedata):
        if not filedata \
                or not "application" in filedata \
                or filedata["application"] != "gridlabd-editor":
            messagebox.showerror(self.filename,f"file does not contain a valid {gridlabd.__title__} data file")
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
        with open(inputname,"r") as fh:
            data = json.load(fh);
            print(data,file=sys.stderr,flush=True)
            self.treeview.set_model()
        return
        # import_dialog = importdialog.ImportDialog(self,inputname=inputname)
        # if import_dialog.result == True:
        #     self.filename = import_dialog.outputname
        #     inputext = os.path.splitext(inputname)[1][1:]
        #     outputext = os.path.splitext(import_dialog.outputname)[1][1:]
        #     if import_dialog.inputtype: 
        #         inputtype = f"{inputext}-{import_dialog.inputtype}"
        #     else: 
        #         inputtype = inputext
        #     if import_dialog.outputtype:
        #         outputtype = f"{outputext}-{import_dialog.outputtype}"
        #     else:
        #         outputtype = outputext
        #     command =  f"gridlabd convert -i {inputname} -o {import_dialog.outputname} -f {inputtype} -t {outputtype}"
        #     # result = runner.Runner(command,output_call=self.output,error_call=self.error)
        #     # if result.returncode:
        #     #     messagebox.showerror("File import failed",f"Return code {result.returncode}\n\n"+result.get_errors('\n'))
        #     self.output(f"Running {command}...\n")
        #     result = subprocess.run(command.split(),capture_output=True)
        #     if result:
        #         self.output(result.stdout)
        #         self.output(result.stderr)
        #     else:
        #         self.error("command failed")
        #     if result and result.returncode == 0:
        #         self.load_model()
        #     else:
        #         messagebox.showerror("File import",result.stderr)

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
        if self.preferences.get("Save output"):
            with open(self.preferences.get("Save output filename"),"w") as f:
                f.write(self.outputview.text.get(1.0,"end-1c"))
        with open("gridlabd-appdata.conf","w") as f:
            json.dump(application_data,f,indent=4)
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
    def model_compile(self,gldname):
        glmname = os.path.splitext(gldname)[0]+".glm"
        with open(glmname,"w") as fh:
            print(f"// created by gridlabd-editor from {gldname} as {datetime.datetime.now()}",file=fh)
            for item in self.model:
                key = item['type']
                values = item['values']
                if key == 'comments':
                    print("\n".join([f"// {x}" for x in values]),file=fh)
                elif key == 'clock':
                    block = ''.join([f"\n    {x[0]} \"{x[1]}\";" for x in values.items()]) + '\n'
                    print(f"clock {{{block}}}",file=fh)
                elif key == 'modules':
                    for module, properties in values.items():
                        if properties:
                            block = ''.join([f"\n    {x[0]} \"{x[1]}\";" for x in properties.items()]) + '\n'
                            print(f"module {module} {{{block}}}",file=fh)
                        else:
                            print(f"module {module};",file=fh)
                elif key == "inputs":
                    for name, args in values.items():
                        macro = f"#input \"{name}\""
                        for tag, value in args.items():
                            macro += f" --{tag} {value}"
                        macro += ";"
                        print(macro,file=fh)
                elif key == "globals":
                    for name,value in values.items():
                        print(f"#define {name}={value}",file=fh)
                elif key == "includes":
                    for file, args in values.items():
                        if args:
                            arglist = [f"{x[0]}={x[1]}" for x in args.items()]
                            print(f"#include using({','.join(arglist)}) \"{file}\";",file=fh)
                        else:
                            print(f"#include \"{file}\";",file=fh)
                # elif key == "objects":
                #     for name, 
                elif values:
                    print(f"#warning {key} not processed",file=fh)
                    print("//",json.dumps(values,indent=4).replace("\n","\n// "),file=fh)
            print("// END",file=fh)
        return glmname

    def model_build(self,event=None):
        self.output(f"\nCompiling {os.path.split(self.filename)[1]}...\n")
        tic = timeit.default_timer()
        command = ["gridlabd","-W",os.path.dirname(self.filename),"-C",self.model_compile(self.filename)]
        if self.template:
            command.append(self.template)
        command.extend(["-D","show_progress=FALSE"])
        result = subprocess.run(command,capture_output=True)
        toc = timeit.default_timer()
        self.output(result.stdout.decode('utf-8').strip(),noblank=True)
        tag = result.stderr.decode('utf-8').strip()
        if result.returncode:
            self.outputview.append_text(f"Compile failed: exit code {result.returncode}",tag=tag)
        else:
            self.outputview.append_text(f"Build completed ok",tag=tag)
        self.output(f"Elapsed time: {toc-tic:.2g} seconds\n")

    def model_run(self,event=None):
        self.output(f"\nStarting {os.path.split(self.filename)[1]}...\n")
        tic = timeit.default_timer()
        command = ["gridlabd","-W",os.path.dirname(self.filename),self.model_compile(self.filename)]
        if self.template:
            command.append(self.template)
        command.extend(["-D","show_progress=FALSE"])
        result = subprocess.run(command,capture_output=True)
        toc = timeit.default_timer()
        self.output(result.stdout.decode('utf-8').strip(),noblank=True)
        tag = result.stderr.decode('utf-8').strip()
        if result.returncode:
            self.outputview.append_text(f"Run failed: exit code {result.returncode}",tag=tag)
        else:
            self.outputview.append_text(f"Run completed ok",tag=tag)
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
        os.system(f"/usr/local/bin/python3 {editor_path}/template.py &")

    def model_template_choose(self,event=None):
        initialdir = f"{share_path}/template"
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
        os.system(f"/usr/local/bin/python3 {editor_path}/library.py &")

    def model_library_choose(self,event=None):
        initialdir = f"{share_path}/library"
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
        os.system(f"/usr/local/bin/python3 {editor_path}/weather.py &")

    def model_weather_choose(self,event=None):
        initialdir = f"{share_path}/weather"
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

    def model_settings(self,event=None):
        initialdir = "/usr/local/opt/gridlabd"
        folder = None
        while not folder:
            folder = filedialog.askdirectory(title="Choose GridLAB-D version",initialdir=initialdir)
            if not folder:
                return
            if os.path.exists(folder+"/bin/gridlabd"):
                folder = None
        self.preferences.set("GridLAB-D install",folder)

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
# Main app startup
#
if __name__ == "__main__":
    root = Editor()
    try:
        ico = Image.open(__file__.replace(".py",".png"))
        photo = ImageTk.PhotoImage(ico)
        root.wm_iconphoto(True, photo)
    except Exception as err:
        print("EXCEPTION:",err)
    if preferences.Preferences().get("Welcome dialog enabled"):
        messagebox.showinfo("Welcome",
            f"""{title}\n{version}-{build} ({branch}) {system}\n\n{copyright}\n{__doc__}
            """)
    root.mainloop()
