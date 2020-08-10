"""
ResizingCanvas.py

ResizingCanvas.py implements a tkinter-based canvas used by the Editor for showing a map background
and allowing user to move and resize it
"""

from tkinter import *
import PIL
from PIL import Image, ImageDraw, ImageTk

class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        self.config(width=self.width, height=self.height)
        self.scale("all",0,0,wscale,hscale)