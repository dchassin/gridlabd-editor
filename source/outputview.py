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
        self.text.tag_config("error_text",foreground="red")
        self.text.tag_bind("error_text","<Button-1>",self.on_click)
        self.text.tag_config("error_msg",foreground="red")
        self.text.tag_bind("error_msg","<Button-1>",self.on_click)

    def on_click(self,event):
        pos = event.widget.index("@%s,%s"%(event.x,event.y))
        line = int(float(str(pos)))
        if self.tags[line]["end"]:
            self.text.delete(f"{line+1}.0",self.tags[line]["end"])
            self.tags[line]["end"] = None
        else:
            self.text.insert(f"{line+1}.0",self.tags[line]["text"],"error_text")
            self.tags[line]["end"] = f"{line+1}.0+{len(self.tags[line]['text'])}c"

    def append_text(self,text,end='\n',tag=None,color="error_msg"):
        if not tag:
            self.text.insert(END,text+end)
        else:
            line = int(float(str(self.text.index(END)))-1)
            self.text.insert(END,text+end,color)
            self.tags[line] = {"text":"| "+tag.strip().replace("\n","\n| ")+"\n","end":None}
        self.text.see(END)
        self.text.update()

