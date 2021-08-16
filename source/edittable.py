import os
import tkinter as tk
from tkinter import Frame, filedialog, ttk
from tmy3 import *

class PandasDataFrame(ttk.Treeview):
        """Basic test frame for the table"""
        def __init__(self, parent=None, data=DataFrame(),title="New dataframe",show='headings',columns=[]):
            super().__init__(self)
            self.parent = parent
            self.title(title)
            for column in data.columns:
                self.heading(column,text=column)
            for row,values in data.iterrows():
                self.insert('',END,text=row,values=values)


if __name__ == '__main__':
    filename = "https://raw.githubusercontent.com/slacgismo/gridlabd-weather/master/US/AK-Adak_Nas.tmy3"
    tmy3 = TMY3(filename,coerce_year=2020)
    # app = PandasDataFrame(parent=tk,data=tmy3.dataframe,title=os.path.split(filename)[1])
    # app.mainloop()

    root = tk.Tk()
    root.title('Treeview demo')
    root.geometry('620x200')

    data = tmy3.dataframe
    tree = ttk.Treeview(root, columns=list(map(lambda x: f"#x",range(len(data.columns)))), show='headings')

    # Update with new columns
    for key in range(len(data.columns)):
        tree.heading(f"#{key}", text=tmy3.dataframe.columns[key])
        tree.column(f"#{key}",width=50)

    for row,values in tmy3.dataframe.iterrows():
        # print(row,values.to_list())
        tree.insert('',tk.END,text=row,values=values.to_list())


    # bind the select event
    def item_selected(event):
        for selected_item in tree.selection():
            # dictionary
            item = tree.item(selected_item)
            # list
            record = item['values']
            #
            showinfo(title='Information',
                    message=','.join(record))


    tree.bind('<<TreeviewSelect>>', item_selected)

    tree.grid(row=0, column=0, sticky='nsew')

    # add a scrollbar
    scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')

    # run the app
    root.mainloop()    