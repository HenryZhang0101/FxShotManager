import tkinter as tk
from tkinter import filedialog
import os
from FxUtil import *


# Get the Resolve instance
fu = resolve.Fusion()
ui = fu.UIManager
disp = bmd.UIDispatcher(ui)

project = resolve.GetProjectManager().GetCurrentProject()
media_pool = project.GetMediaPool()
# currentFolder = media_pool.GetCurrentFolder()


# Define the UI layout
layout = ui.VGroup({
    "Spacing": 10
}, [
    ui.Label({"Text":"Directory","Weight": 0}),
    ui.HGroup([
        ui.LineEdit({ 'ID':'directory', "Weight": 0.5}),
        ui.Button({ 'ID':'browse', 'Text':'Browse' ,"Weight": 0.2}),  
    ],{ "Spacing": 5 , "Weight": 0}), 
    ui.Label({"Text":"VFX Shots","Weight": 0}),
    ui.Tree({ 'ID':'shots', 'ColumnCount': 5 ,"AlternatingRowColors" : True, 'SortingEnabled': True, "Weight": 1, "HeaderHidden": False}),
    ui.Button({ 'ID':'update', 'Text':'Update All' ,"Weight": 0})
    
])

# Create the window
win = disp.AddWindow({"WindowTitle": "Update FX Shots", "ID": "MainWindow", "Geometry": [100, 150, 600, 600]}, layout)

# Access UI elements
itm = win.GetItems()



# add tree items
tree = win.Find('shots')
tree.SetHeaderLabels(["ID","Name", "Version", "Current","Status"])
tree.ColumnWidth[0]= 50
tree.ColumnWidth[1]= 200
tree.ColumnWidth[2]= 80
tree.ColumnWidth[3]= 80
tree.ColumnWidth[4]= 80




fx_folder = FxFolder()

# Initialize tk root once to avoid lifecycle overhead
tk_root = tk.Tk()
tk_root.withdraw()
tk_root.attributes('-topmost', True)

# functions
def browse(ev):
    directory = filedialog.askdirectory(parent=tk_root)
    
    if directory:
        win.Find('directory').SetText(directory)
        refresh_tree()
        fx_folder.set_clip_colors()

def refresh_tree():
    tree.Clear()
    fx_folder.update(win.Find('directory').GetText(),media_pool)
    fx_table = fx_folder.get_fx_shots()
    for i, fx_shot in enumerate(fx_table):
        item = tree.NewItem()
        item.SetText(0, str(i))
        item.SetText(1, fx_shot[0])
        item.SetText(2, fx_shot[1])
        item.SetText(3, fx_shot[2])
        item.SetText(4, fx_shot[3])
        tree.AddTopLevelItem(item)

def update(ev):
    fx_folder.update_all()
    refresh_tree()

def window_closed(ev):
    tk_root.destroy()
    disp.ExitLoop()
    
win.On.MainWindow.Close = window_closed
win.On["browse"].Clicked = browse
win.On["update"].Clicked = update

# Show the window
win.Show()

# Keep the window running
disp.RunLoop()

# Clean up after closing
win.Hide()