"""
Editor.py

Editor.py contains class creating interface for marking the exact area of the selected forest.
It allows three different levels of input Red, Yellow and Green.
The result is stored inside of a png file
"""

from tkinter import *
import PIL
from PIL import Image, ImageDraw, ImageTk
import ResizingCanvas

cell_size=15

class Editor:
    def save(self):
        filename = self.file_name+"bitmask"+".png"
        self.image1.save(filename)
        self.root.destroy()

    def activate_paint(self,e):
        global lastx, lasty
        self.cv.bind('<B1-Motion>', self.paint)
        lastx, lasty = e.x, e.y

    def set_red(self):
        self.fill='red'

    def set_yellow(self):
        self.fill='yellow'

    def set_green(self):
        self.fill='green'

    def paint(self,e):
        global lastx, lasty
        x, y = self.cv.canvasx(e.x), self.cv.canvasy(e.y)
        xx=x//cell_size
        yy=y//cell_size
        xx=xx*cell_size
        yy=yy*cell_size
        self.stack.append(self.cv.create_rectangle((xx,yy,xx+cell_size,yy+cell_size),fill=self.fill, width=1))
        self.draw.rectangle((xx*4,yy*4,xx*4+cell_size*4,yy*4+cell_size*4), fill=self.fill, width=1)
        lastx, lasty = x, y

    def do_zoom(self,event):
        if len(self.stack) > 0:
            id = self.stack.pop()
            self.cv.delete(id)
        #factor = 1.001 ** event.delta
        #cv.scale(ALL, 0,0,factor, factor)

    def __init__(self,file_name):
        self.fill='red'
        self.file_name=file_name
        self.root = Tk()
        lastx, lasty = None, None
        image_number = 0
        im = Image.open(file_name+".png") #'img7.997-11.535.png'
        self.image1 = PIL.Image.new('RGB', (im.width, im.height), 'white')
        im = im.resize((im.width // 4, im.height // 4), Image.ANTIALIAS)
        self.cv = Canvas(self.root, width=im.width, height=im.height, bg='white')
        self.stack = []


        self.draw = ImageDraw.Draw(self.image1)

        self.cv.bind('<1>', self.activate_paint)
        self.cv.pack(expand=YES, fill=BOTH)

        self.cv.image = ImageTk.PhotoImage(im)

        self.cv.create_image(0, 0, image=self.cv.image, anchor='nw')

        self.cv.bind("<MouseWheel>", self.do_zoom)
        self.cv.bind('<ButtonPress-3>', lambda event: self.cv.scan_mark(event.x, event.y))
        self.cv.bind("<B3-Motion>", lambda event: self.cv.scan_dragto(event.x, event.y, gain=1))

        bottomframe = Frame(self.root)
        bottomframe.pack(side=BOTTOM)



        btn_red = Button(bottomframe,text="■",fg='red', command=self.set_red)
        btn_red.pack(side=LEFT)

        btn_orange = Button(bottomframe, text='■',fg='orange', command=self.set_yellow)
        btn_orange.pack(side=LEFT)

        btn_green = Button(bottomframe, text="■",fg='green', command=self.set_green)
        btn_green.pack(side=LEFT)

        btn_save = Button(bottomframe, text="Save", command=self.save)
        btn_save.pack(side=RIGHT)
        zoomcycle = 0
        zimg_id = None
        self.root.mainloop()

#e=Editor("img7.997-11.535")