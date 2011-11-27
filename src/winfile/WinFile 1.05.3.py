#!/usr/bin/ python
# -*- coding: latin-1 -*-

# GNU GENERAL PUBLIC LICENSE
# WinFile main source code ( http://code.google.com/p/winfiles60/ ) - A powerful filemanager for the Symbian OS
# Copyright   2008-2011 memoryN70 ( memoryS60@gmail.com )
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#WinFile Main Programm source code
#Python console execute: execfile("E:\\system\\apps\\python\\my\\winfile 1.05.py")
#                        execfile("E:\\data\\python\\winfile 1.05.3.py")
#Symbian UID (2nd edition): 0x06dfae12
#Symbian UID (3rd-5th-^3): 0x

# python libs
from __future__ import generators #Serve per una scansione speciale dei files per la ricerca
import struct
import time
import sys
import os
import types
import random
import codecs
import traceback
#traceback.print_exc()
#import imp

__shell__ = 1 #if script is run into python shell
__version__ = 1.053
__version_info__ = (1, 05, 03, '--/--/2011')
__author__ = "MemoryN70 <memoryS60@gmail.com>"
__long_name__ = "WinFile: the filemanager for Symbian OS"
__revision__ = "(r20)"

class DEBUGGER:
    def __init__(s):
        s.cbs = []
        s.log = ''
        s.to_file = 1
        s.olderr = sys.stderr
        s.oldout = sys.stdout
        s.filename = "D:\\WinFile_debug.log"#directory.appdir+"\\debug.log"
        #class itself calling write()
        sys.stdout = sys.stderr = s
    def quit(s):
        sys.stdout = s.oldout
        sys.stderr = s.olderr
    def write(s,t):
        s.log += t
        s.olderr.write(t)
        if s.to_file:
            try:
                #try to redirect output to file in append mode
                open(s.filename,'a').write(t)
            except:
                pass
        for i in s.cbs:
            i(t)

class _directories:
    def __init__(s):
        #s.local_directory=sys.path
        s.disk = sys.path[0][0:1]
        s.appdir = "%s:\\System\\Apps\\WinFile"%s.disk
        if s.appdir not in sys.path:
            #Be sure to include the local directory...WinFile libs, resources have the priority
            sys.path.insert(0, s.appdir)
        try:
            s.skin_dir = os.path.normpath(open(s.appdir+"\\theme_dir.ini").read())
        except:
            s.skin_dir = "D:\\winfile_theme"
        #Paths
        s.lang_dir = "%s\\Lang"%s.appdir
        s.data_dir = "%s\\Data"%s.appdir
        s.allskin_dir = "%s\\Skin"%s.appdir
        s.plugins_dir = "%s\\Plugins"%s.appdir
        s.file_plugins = "%s\\FileOpen"%s.plugins_dir
        s.info_plugins = "%s\\Info"%s.plugins_dir
        #Files
        s.settings_file = "%s\\settings.dat"%s.data_dir
        s.theme_file = "%s\\theme.dat"%s.data_dir
        s.session_file = "%s\\session.bin"%s.data_dir
        s.first_boot_file = "%s\\first_boot"%s.data_dir

    def create(s,path):
        try:
            os.makedirs(path)
            return 1
        except:
            return 0

debug = DEBUGGER()
#konsole = Konsole()
#debug.cbs.append(konsole)

print __long_name__
print "Version: ", __version__, __revision__
print __version_info__
print time.ctime()

# !!! Remeber: calling this means also update sys.path with appdir!!!
directory = _directories()

print "Local directory", directory.appdir#, directory.local_directory

# symbian libs
import appuifw
import e32
import sysinfo
from graphics import *
from key_codes import *


# 3rd party symbian libs
libs = ["msys", "DriveInfo", "fileutils", "appswitch", "zipfile"]

for lib in libs:
    try:
        exec("%s=__import__('%s')"%(lib, lib))
    except:
        # Set the missing library name to None
        exec("%s = None"%lib)
        print "** Failed to load", lib, "Reinstall the module or WinFile **\n"
        traceback.print_exc()
        print "\n"

# try:
    # import msys
    # import DriveInfo
    # import fileutils
# except:
    # traceback.print_exc()
# try:
    # from akntextutils import wrap_text_to_array
    
# except:
    # print "Please install akntextutils to boost some programm features!"
    # def wrap_text_to_array(a,b,c): return [a]
# try:
    # import appswitch
# except:
    # traceback.print_exc()
#sys.path.append('e:\data\python')
#import ziptools
#import zipfile

#WinFile UI Framework

TEST_IMG = Image.new((1,1))

# def wrap_text_to_array2(text, font, width):

    # lines = []
    # text = text.splitlines()
    
    # for line in text:

        # line_out = u""
        # fits = TEST_IMG.measure_text(line, font, width)[2]
            
        # if fits <= 0:
            # lines.append(line)
            # break
        
        

def wrap_text_to_array(text, font, width):
        if not text:
            return [u""]
        lines = []
        # Paragraph yet to be chopped
        text_lines = text.splitlines()
        for text_left in text_lines:
            while len(text_left) > 0:
                bounding, to_right, fits = TEST_IMG.measure_text(text_left, font, width)
                if fits <= 0:
                    lines.append(text_left)
                    break
                slice = text_left[0:fits]
                # How many chars we can skip at the end of the row
                # (whitespaces at the end of the row)
                adjust = 0
                if len(slice) < len(text_left):
                    # Use the last space as a break point
                    rindex = slice.rfind(u" ")
                    if rindex > 0:
                        adjust = 1
                        slice = slice[0:rindex]
                lines.append(slice)
                text_left = text_left[len(slice)+adjust:]
        # print "input",len(text),"out",len(lines), len(''.join(lines))
        # print ''.join(lines) == text
        return lines

ORIENTATION_HORIZONTAL = 1
ORIENTATION_VERTICAL = 2

class StatusBar:
#A class to manage screen bars, with touch event support
#by Memory
#Version: 0.3
    def __init__(s, cb=None):

        #s.img = img #Where to draw everything
        #s.id = 0 #default 0
        #s.description = None #a short press of the area to show up this message
        s.orientation = ORIENTATION_HORIZONTAL # !!AUTODETECTED!! vertical / horizontal
        s.position = (0, 0, 100, 10) # x,y,xf,yf: position of the first edge of the bar , length and height
        s.bg_fill_color = None #None if no background (transparent), otherwise a color
        s.bg_outline_color = 0
        s.bar_fill_color = 0 #or None for transparent
        s.bar_outline_color = 0 #or None
        s.max_value = 100
        s.min_value = 0
        s.actual_value = 0
        #s.step = 1 #default step
        s.sensitivity = .02 # touch area is 2 % bigger than the bar to increase sensitivity
        #Calculation of some values
        s.init_values()
        s.formatter = int #This is important. It is used to round a value to have better ui style
        s.callback = cb #If set, use this in some functions instead of ScrollBar.draw()

    def set_touch(s):

        if ui.touch_screen:
            ui.bind_touch(EDrag, s.touch_event, s.coords_touch)

    def unset_touch(s):

        if ui.touch_screen:
            ui.unbind_touch(EDrag, None, s.coords_touch)

    def touch_event(s, pos):
    
        # !!! values are float !!! Remember it for calculation precision
        s.range = float(abs(s.max_value - s.min_value))
        if s.orientation == ORIENTATION_VERTICAL:
            unit = abs(s.yf - pos[1])
            scale = s.range / s.y
        elif s.orientation == ORIENTATION_HORIZONTAL:
            unit = abs(pos[0] - s.x0)
            scale = s.range / s.x

        #print "Moved to:",pos , unit
        val = unit * scale
        # val = min(val, s.max_value)
        # val = max(val, s.min_value)
        if val>s.max_value: #TODO: use max() / min()
            val = s.max_value
        if val<s.min_value:
            val = s.min_value
        #this is not always int or float. Depends on s.formatter
        s.actual_value = s.formatter(val)

        if s.callback:
            s.callback(s.actual_value)

    def set_default(s):
        # not to be implemented there. Only in main app!
        init_values()

    def init_values(s):
        #Initialize coords and other values
        s.x1, s.y1, s.x2, s.y2 = s.position
        s.x = max(s.x1, s.x2)-min(s.x1, s.x2) #x width
        s.y = max(s.y1, s.y2)-min(s.y1, s.y2) #y height
        s.xf, s.yf = max(s.x1, s.x2), max(s.y1, s.y2)
        #First coord of the rect (upper left corner)
        s.x0, s.y0 = min(s.x1, s.x2), min(s.y1, s.y2)
        if s.x < s.y:
            s.orientation = ORIENTATION_VERTICAL
        else:
            s.orientation = ORIENTATION_HORIZONTAL
        #s.height = s.position[3]
        #s.lenght = s.position[2]
        # if s.orientation == ORIENTATION_HORIZONTAL:
            # s.rect = [(0,0),(s.lenght, s.height)]
        # elif s.orientation == ORIENTATION_VERTICAL:
            # s.rect = [(0,0),(s.height, s.lenght)]
        # s.coords = [ s.position[0:2],
                    # (s.rect[1][0]+s.position[0], s.rect[1][1]+s.position[1])
                   # ]
        s.coords = [(s.x0, s.y0), (s.xf, s.yf)]
        #Here the coords for touch event. They are approx 5% "bigger" than the rectangle of the bar to increase sensitivity
        s.coords_touch = [ (int(s.x0 * (1.00-s.sensitivity)), int(s.y0 * (1.00-s.sensitivity))),
                           (int(s.xf * (1.00+s.sensitivity)), int(s.yf * (1.00+s.sensitivity)))
                         ]
        #print s.coords, s.orientation

    def percentage(s):

        return float(s.actual_value) / s.max_value * 100.0

    def get(s):

        return s.actual_value

    def set(s, v):
        #Set and draw a new value
        s.actual_value = v
        s.draw()

    def draw(s, img):

        #Background
        img.rectangle(s.coords, None, s.bg_fill_color)
        #Dinamyc bar
        perc = float(s.actual_value) / s.max_value
        if s.orientation == ORIENTATION_VERTICAL:
            img.rectangle( ((s.x0, s.yf - int(s.y * perc)), (s.xf, s.yf) ), s.bar_outline_color, s.bar_fill_color)
        elif s.orientation == ORIENTATION_HORIZONTAL:
            img.rectangle( ((s.x0, s.y0), (s.x0 + int(s.x * perc), s.yf) ), s.bar_outline_color, s.bar_fill_color)
        #Draw border
        img.rectangle(s.coords, s.bg_outline_color, None)

class Button:
#A class to mangage a button element, with touch event support
#version 0.1 alpha
    def __init__(s, cb=None):
    
        #s.img = img #where to draw it
        #s.description = None #A short description of the button
        s.callback = cb #Callback assigned with it
        s.caption = u"" #Label of the button
        s.font = None
        s.text_color = 0
        s.max_width = -1
        s.position = (0,0,None,None) #x,y, size (x,y) if size == None, the rect is created from text measurement
        s.alignment = ALIGNMENT_LEFT
        s.bg_fill_color = None #None if no background (transparent), otherwise a color
        s.bg_outline_color = 0#None
        #s.bg_img = None #If you want to use an image...It will be stretched if too small / large!
        s.init_values()
    
    def __del__(s):
    
        #When the object is deleted
        s.unset_touch(0)
        
    def init_values(s):
        #Initialize coords and other values
        bbox = TEST_IMG.measure_text(s.caption, s.font, s.max_width)[0]
        s.coords = [(s.position[0]+bbox[0], s.position[1]+bbox[1]),(s.position[0]+bbox[2], s.position[1]+bbox[3])]
        
    def set_touch(s):
    
        if ui.touch_screen:
            ui.bind_touch(EButton1Up, s.pressed, s.coords)
            ui.bind_touch(EButton1Down, s.pressing, s.coords)
            print s.coords
        ####
        #To remove the state of pressed
        #canvas.bind(EButton1Up, s.draw) #Warning: this isn't safe!!!
        ###
        
    def unset_touch(s):
        pass
        
    def pressed(s, pos):
    
        if s.callback:
            s.callback()

    def pressing(s, pos):
        #s.draw(pressing = 1)
        ui.canvas.rectangle(s.coords, None, s.bg_outline_color)
        ui.canvas.rectangle(s.coords, s.bg_fill_color, None)

    def draw(s, img, pressing = 0):
    
        if pressing:
            img.rectangle(s.coords, None, s.bg_outline_color)
            img.rectangle(s.coords, s.bg_fill_color, None)
        # else:
        #img.rectangle(s.coords, None, s.bg_fill_color)
        #img.rectangle(s.coords, s.bg_outline_color, None)
        img.rectangle(s.coords, s.bg_outline_color, s.bg_fill_color)
        img.text(s.position[0:2], s.caption, s.text_color, s.font)

class ScrollBar:
#A class to manage screen bars, with touch event support
#by Memory
#Version: 0.2 beta
    def __init__(s, cb = None):

        s.orientation = ORIENTATION_HORIZONTAL # or vertical
        s.position = (0,0,100,10) #x,y coord and height, lenght
        s.bg_fill_color = None #None if no background (transparent), otherwise a color
        s.bg_outline_color = 0
        s.bar_fill_color = 0 #or None for transparent
        s.bar_outline_color = 0 #or None
        s.max_value = 100
        s.min_value = 0
        s.max_page = 10
        s.current = 0
        s.sensitivity = .02 # touch area is 2 % bigger than the bar to increase sensitivity
        #TODO: best way to avoid 1 pixel bars??!!
        s.min_bar_size = 10
        s.min_bar_size_perc = .05 #Percentage of size
        #Calculation of some values
        #s.init_values()
        s.callback = cb #the function that is called at every user input
        # if s.feedback:
            #set touch screen feedback
            # s.set_touch()
    def set_touch(s):

        if ui.touch_screen:
            ui.bind_touch(EDrag, s.touch_event, s.coords_touch)
            ui.bind_touch(EButton1Down, s.touch_event, s.coords_touch)

    def touch_event(s, pos):
    
        # !!! values are float !!! Remember it for calculation precision
        range = float(abs(s.max_value - s.min_value))
        # if s.orientation == ORIENTATION_VERTICAL:
            # unit = abs(pos[1]-s.coords[0][1])
            # scale = range / s.rect[1][1]
        # elif s.orientation == ORIENTATION_HORIZONTAL:
            # unit = abs(pos[0]-s.coords[0][0])
            # scale = range / s.rect[1][0]
        if s.orientation == ORIENTATION_VERTICAL:
            unit = abs(pos[1] - s.y0)
            scale = range / s.y
        elif s.orientation == ORIENTATION_HORIZONTAL:
            unit = abs(pos[0] - s.x0)
            scale = range / s.x

        val = int(unit * scale)
        if val>s.max_value:
            val = s.max_value
        if val<s.min_value:
            val = s.min_value
        s.current = val

        if s.callback:
            s.callback(s.current)

    def init_values(s):
        #Initialize coords and other values
        #Initialize coords and other values
        s.x1, s.y1, s.x2, s.y2 = s.position
        s.x = max(s.x1, s.x2)-min(s.x1, s.x2) #x width
        s.y = max(s.y1, s.y2)-min(s.y1, s.y2) #y height
        s.xf, s.yf = max(s.x1, s.x2), max(s.y1, s.y2)
        #First coord of the rect (upper left corner)
        s.x0, s.y0 = min(s.x1, s.x2), min(s.y1, s.y2)
        if s.x < s.y:
            s.orientation = ORIENTATION_VERTICAL
            s.min_bar_size = s.y * s.min_bar_size_perc
        else:
            s.orientation = ORIENTATION_HORIZONTAL
            s.min_bar_size = s.x * s.min_bar_size_perc
        s.coords = [(s.x0, s.y0), (s.xf, s.yf)]
        #Here the coords for touch event. They are approx 5% "bigger" than the rectangle of the bar to increase sensitivity
        s.coords_touch = [ (int(s.x0 * (1.00-s.sensitivity)), int(s.y0 * (1.00-s.sensitivity))),
                           (int(s.xf * (1.00+s.sensitivity)), int(s.yf * (1.00+s.sensitivity)))
                         ]
        # s.height = s.position[3]
        # s.lenght = s.position[2]
        # if s.orientation == ORIENTATION_HORIZONTAL:
            # s.rect = [(0,0),(s.lenght, s.height)]
        # elif s.orientation == ORIENTATION_VERTICAL:
            # s.rect = [(0,0),(s.height, s.lenght)]
        # s.coords = [ s.position[0:2],
                    # (s.rect[1][0]+s.position[0], s.rect[1][1]+s.position[1])
                   # ]
        #Here the coords for touch event. They are approx 5% "bigger" than the rectangle of the bar to increase sensitivity
        # s.coords_touch = [ (int(s.position[0] * (1.00-s.sensitivity)), int(s.position[1] * (1.00-s.sensitivity))),
                           # (int((s.rect[1][0]+s.position[0]) * (1.00+s.sensitivity)), int((s.rect[1][1]+s.position[1]) * (1.00+s.sensitivity)))
                         # ]

    def percentage(s):

        return float(s.current) / s.max_value * 100.0

    def draw(s, img):
        #Background
        img.rectangle(s.coords, None, s.bg_fill_color)
        range = float(abs(s.max_value - s.min_value))
        #x,y,l,h=s.position
        if s.orientation == ORIENTATION_VERTICAL:
                # x = const
#            dy = s.rect[1][1]
            div_y = s.y / range
            yi = s.y0 + int(div_y * s.current)
            yf = yi + int(div_y * s.max_page)
            img.rectangle( (s.x0, yi, s.xf, yf), s.bar_outline_color, s.bar_fill_color)
        else:
                # y = const
            #dx = s.rect[1][0]
            div_x = s.x / range
            xi = s.x0 + int(div_x * s.current)
            xf = xi + int(div_x * s.max_page)
            img.rectangle( (xi, s.y0, xf, s.yf), s.bar_outline_color, s.bar_fill_color)
        #Draw border
        img.rectangle(s.coords, s.bg_outline_color)

ALIGNMENT_LEFT = 1
ALIGNMENT_CENTER = 2
ALIGNMENT_RIGHT = 4
ALIGNMENT_DOWN = 8
ALIGNMENT_MIDDLE = 16
ALIGNMENT_UP = 32
ALIGMENT_NONE = 64

def text_render(img, coords, text, fill = 0, font = None, alignment = ALIGNMENT_LEFT|ALIGNMENT_DOWN, cut = 0, width = None, border_x = 0, border_y = 0):
        """ Draw text defining its properties and alignment
        By default the text is drawn in the coordinates given (lower left corner) or in the lower left corner of the rectangle coords
        If you want only to draw some text at (x,y) without alignment or other calculations, use Image.text.
        
        @param img: canvas or Image object
        @param coords: [X,Y] or [X1,Y1,X2,Y2] rectangle. In the [x,y] mode, x or y can be None to set tha maximum x or y of the image
                            (usefull for ALIGNMENT_RIGHT, ALIGNMENT_DOWN...when it's not necessary to specify a coord but it's calculated by the function)
        @param text: unicode text string
        @param font: appuifw font (name, size, [options]) or None (default font) or 'normal'
        @param fill: color (r,g,b) or int
        @param aligment: combinations of (ALIGNMENT_LEFT = 1 ALIGNMENT_CENTER = 2 ALIGNMENT_RIGHT = 4) | (ALIGNMENT_DOWN = 8 ALIGNMENT_MIDDLE = 16 ALIGNMENT_UP = 32)
        @param cut: 1 to cut text at img.size[0]-x0 or width
        @param width: defines maximum text width instead of img.size[0]-x0
        x,y image size
        x0, y0 first coord of the rect (upper left corner)
        xf, yf initial pos (of the text)
        """
        if len(coords)==2:
            #X,Y
            x0, y0 = 0,0
            xf, yf = coords[0:2]
            x, y = img.size
            if (xf==None):
                xf = x
            if (yf==None):
                yf = y
        else:
            #Rect
            x1, y1, x2, y2 = coords
            maxx = max(x1,x2) - border_x
            maxy = max(y1,y2) - border_y
            minx = min(x1,x2) + border_x
            miny = min(y1,y2) + border_y
            x = maxx - minx #x width
            y = maxy - miny #y height
            #in this case initial pos (of the text) is the lower left corner
            xf, yf = minx, maxy
            #First coord of the rect (upper left corner)
            x0, y0 = minx, miny#min(y1,y2)

        if (not width):
            width = x - xf

        #measure_text(text[font=None, maxwidth=-1, maxadvance=-1 ])
        bbox, rpixel, n_chars = img.measure_text(text, font, width)

        if cut:
            if (len(text)>n_chars):
                text = u"%s..."%(text[:n_chars-3])

        if (alignment & ALIGNMENT_CENTER):
            #img.text(, text, fill, font)
            xf = ((width - rpixel) / 2) + x0 - xf#,pos[1])
            #print "Center"
        elif (alignment & ALIGNMENT_RIGHT):
            xf = x - rpixel + x0#,pos[1])
            #print "Right"
        if (alignment & ALIGNMENT_MIDDLE):
            yf = int(y0 + (y + (abs(bbox[1])+abs(bbox[3])) ) / 2.0)
            #print bbox
            #print "Middle"
        elif (alignment & ALIGNMENT_UP):
            yf = y0 + (abs(bbox[1])+abs(bbox[3]))
            #print "Up"
        img.text((xf, yf), text, fill, font)
        return (xf, yf), bbox, rpixel, n_chars

def lines_render(img, coords, lines, spacing = 1, fill = 0, font = None, alignment = ALIGNMENT_LEFT|ALIGNMENT_UP, cut = 0, width = None):
    if not lines:
        return
    if len(coords)==2:
        #X,Y
            x0, y0 = 0,0
            xf, yf = coords[0:2]
            x, y = img.size
            if (xf == None):
                xf = x
            if (yf == None):
                yf = y
    else:
            #Rect
            x1, y1, x2, y2 = coords
            maxx = max(x1,x2)
            maxy = max(y1,y2)
            minx = min(x1,x2)
            miny = min(y1,y2)
            x = maxx - minx #x width
            y = maxy - miny #y height
            #in this case initial pos (of the text) is the lower left corner
            xf, yf = minx, maxy
            #First coord of the rect (upper left corner)
            x0, y0 = minx, miny

    if (not width):
        width = x - xf

    to_draw = []
    ty = 0
    
    for text in lines:
        bbox, rpixel, n_chars = img.measure_text(text, font, width)
        h = abs(bbox[1]) + abs(bbox[3])
        ty += (h + spacing)
        if cut:
            if (len(text)>n_chars):
                text = u"%s..."%(text[:n_chars-3])
        to_draw.append((text, h, bbox, rpixel, n_chars))

    y1 = yf
    x1 = xf
 
    if (alignment & ALIGNMENT_MIDDLE):
        y1 = y0 + int(y/2.0 - ty/2.0)
    elif (alignment & ALIGNMENT_DOWN):
        y1 = yf
    elif (alignment & ALIGNMENT_UP):
        y1 = y0 + to_draw[0][1]

    for text, h, bbox, rpixel, n_chars in to_draw:
        # = line
        if (alignment & ALIGNMENT_CENTER):
            x1 = ((width - rpixel) / 2) + x0 - xf
        elif (alignment & ALIGNMENT_RIGHT):
            x1 = x - rpixel + x0
        if (alignment & ALIGNMENT_DOWN):
            img.text((x1, y1), text, fill, font)
            y1 -= h + spacing
        else:
            y1 += h + spacing
            img.text((x1, y1), text, fill, font)


    return x1, y1, ty#, lines

# def blit(img, pos, mask = None):
    # pass
def roundRect(g, x, y, w, h, r):
    # limit r
    if r>w/2:
        r=w/2
    if r>h/2:
        r=h/2
    x1=x+r; y1=y+r; x2=x+w-r; y2=y+h-r; r2=2*r;
    g.ellipse(x, y, r2, r2, 90, 180)
    g.ellipse(x+w-r2, y, r2, r2, 0, 90)
    g.ellipse(x, y+h-r2, r2, r2, 180, 270)
    g.ellipse(x+w-r2, y+h-r2, r2, r2, 270, 0)
    g.rect(x1, y, w-r2, r)
    g.rect(x, y1, w, h-r2+1)
    g.rect(x1, y2, w-r2+1, r)
    # draw the four edges
    g.line(x1, y, x2, y)
    g.line(x, y1, x, y2)
    g.line(x1, y+h-1, x2, y+h-1)
    g.line(x+w-1, y1, x+w-1, y2)
    # draw the four corners
    g.ellipse(x, y, r2, r2, 90, 180)
    g.ellipse(x+w-r2, y, r2, r2, 0, 90)
    g.ellipse(x, y+h-r2, r2, r2, 180, 270)
    g.ellipse(x+w-r2, y+h-r2, r2, r2, 270, 0)


class Text_Object:
    # It is a simple start....
    # It will be used in text_viewer and various widgets like info sceen and popup window
    def __init__(s, text, rect, style, cb):
        s.text = text
        s.rect = rect
        s.style = style
        s.cb = cb
        s.font = None
        s.text_lines = []
        # How many pixel to add to text height
        s.spacing = 1
        s.line_query = 1
        s.VScrollbar = ScrollBar(lambda x: s.goto_line(x))
        #s.VScrollbar.orientation = ORIENTATION_VERTICAL
        s.text_init()
        s.screen_change(1)
        

    def text_init(s):
        s.x1, s.y1, s.x2, s.y2 = s.rect
        s.x = max(s.x1,s.x2) - min(s.x1,s.x2) #x width
        s.y = max(s.y1,s.y2) - min(s.y1,s.y2) #y height
        #in this case initial pos (of the text) is the lower left corner
        s.xf, s.yf = max(s.x1,s.x2), max(s.y1,s.y2)
        #First coord of the rect (upper left corner)
        s.x0, s.y0 = min(s.x1,s.x2), min(s.y1,s.y2)

        s.width = s.x# - s.xf
        s.text_lines = []
        s.text = s.text.replace(u"\t",u"    ") #Sostituiamo i tabulatori con 4 spazi (cosi non si vede il quadratino)
        lines = s.text.splitlines()

        for line in lines:
            t = wrap_text_to_array(line, s.font, s.width)
            if t:
                s.text_lines+=t
            else:
                s.text_lines.append(u"")
        # Maximum width of the text in the normal (non-wrap) mode
        s.max_x = 0
        # The maximum text height
        s.text_height = 0
        # Scan every line for these results
        for line in s.text_lines:
        
            bbox, p, n_char = TEST_IMG.measure_text(line, s.font)
            h = abs(bbox[1]) + abs(bbox[3])
            if h>s.text_height:
                s.text_height = h
            if p>s.max_x:
                s.max_x = p

        s.line_no = len(s.text_lines)

    def screen_change(s,at_init = 0):
        #old = ui.landscape

        s.text_dy = (s.text_height + s.spacing)
        s.max_lines = int( s.y / float((s.text_height + s.spacing)))
        if s.line_no>s.max_lines:
            s.max_rectY_size = s.max_lines*s.text_dy
        else:
            s.max_rectY_size = s.line_no*s.text_dy
        s.first_line = 0
        s.end_line = s.max_lines
        if (s.style & ALIGNMENT_MIDDLE):
            s.y1 = s.y0 + int(s.y/2.0 - s.max_rectY_size/2.0)
        elif (s.style & ALIGNMENT_DOWN):
            s.y1 = s.yf
        elif (s.style & ALIGNMENT_UP):
            s.y1 = s.y0 + s.text_dy

        s.VScrollbar.max_page = s.max_lines
        s.VScrollbar.min_value = 0
        s.VScrollbar.position = (s.xf - 10, s.y0, s.xf, s.yf)#(s.xf-10,s.y0,s.y,10)
        s.VScrollbar.init_values()
        # if not at_init:
            # s.text_init(s.line_sep)

    def bind(s):
        s.VScrollbar.set_touch()
        if ui.landscape==1:
            ui.bind(EScancodeUpArrow,s.pag_su)
            ui.bind(EScancodeLeftArrow,s.pag_giu)
            ui.bind(EScancode9, lambda: s.goto_line(s.line_no-1))
            ui.bind(EScancode8, lambda: s.goto_line(0))
            ui.bind(EScancode0, lambda: s.pag_su(s.max_lines))
            ui.bind(EScancodeHash, lambda: s.pag_giu(s.max_lines))
        elif ui.landscape==2:
            ui.bind(EScancodeLeftArrow,s.pag_su)
            ui.bind(EScancodeRightArrow,s.pag_giu)
            ui.bind(EScancode7, lambda: s.goto_line(s.line_no-1))
            ui.bind(EScancode8, lambda: s.goto_line(0))
            ui.bind(EScancode0, lambda: s.pag_su(s.max_lines))
            ui.bind(EScancodeStar, lambda: s.pag_giu(s.max_lines))
        else:
            ui.bind(EScancodeUpArrow,s.pag_su)
            ui.bind(EScancodeDownArrow,s.pag_giu)
            ui.bind(EScancodeStar, lambda: s.goto_line(s.line_no-1))
            ui.bind(EScancode7, lambda: s.goto_line(0))
            ui.bind(EScancode9, lambda: s.pag_su(s.max_lines))
            ui.bind(EScancodeHash, lambda: s.pag_giu(s.max_lines))

    def pag_giu(s,plus=1):
        if s.line_no>s.max_lines:
            if plus+s.end_line>s.line_no:
                s.end_line = s.line_no
                s.first_line = s.end_line-s.max_lines
            else:
                s.first_line += plus
                s.end_line += plus
            if s.cb:
                s.cb()

    def pag_su(s,lines=1):
        if s.line_no>s.max_lines:
            s.first_line -= lines
            s.end_line -= lines
            if s.first_line<0:
                s.end_line = s.max_lines
                s.first_line = 0
            if s.cb:
                s.cb()

    def goto_line(s, linea):
        if s.line_no<=s.max_lines:
            return
        if not (linea+1)>s.line_no:
            if not linea>s.line_no-s.max_lines:
                s.end_line = linea+s.max_lines
                s.first_line = linea
            else:
                s.end_line = s.line_no
                s.first_line = s.line_no-s.max_lines
            s.line_query = linea+1
        if s.cb:
            s.cb()

    def text_redraw(s, timg):
        i = 0
        for line in s.text_lines[s.first_line:s.end_line]:
            #TODO: some hacks to define only X alignment
            text_render(timg, (s.x0, s.y1 + (s.text_dy*i)), line, 0, s.font, ALIGNMENT_LEFT)
            #timg.text((s.x, s.y + (s.text_dy*i)), line, settings.text_color, skinUI.text_viewer_font)
            i += 1
        if s.line_no>s.max_lines:
            s.VScrollbar.current = s.first_line# - s.max_lines
            s.VScrollbar.max_value = s.line_no - 1# - s.max_lines
            s.VScrollbar.draw(timg)

# class Rect:

    # def __init__(s, coords):

        # s.coords = coords
        # x1, y1, x2, y2 = coords
        # dx = max(x1,x2) - min(x1,x2) #x width
        # dy = max(y1,y2) - min(y1,y2) #y height
        # xf, yf = max(x1,x2), max(y1,y2)
        # x0, y0 = min(x1,x2), min(y1,y2)

# class Arrow:

    # def __init__(s, img, pos, fillC, lineC, height, orientation = 0):

        # img.line([pos, (pos[0], pos[1])])


class _SkinUI:

    def __init__(s):

        s.dx, s.dy = ui.display_size
        s.px = s.dx / 100.0
        s.py = s.dy / 100.0
        
        # General UI #
        
        #Title rect
        s.title_rect = [0, 0, s.dx, int(s.py*8)]
        #Rect where softkeys are
        s.softkeys_rect = [0, int(s.py*94), s.dx, s.dy]
        #The main drawable area used
        s.main_drawable_rect = [0, s.title_rect[3], s.dx, s.softkeys_rect[1]]
        #The rect of the main scrollbar of the programm
        s.scrollbar_rect = (s.dx - int(s.px*3), s.title_rect[3], s.dx, s.softkeys_rect[1])
        #The popup widget max size
        #s.popup_coords = [int(px*5)]
        #The maximum area of a popup widget (inside the widget itself)
        s.popup_size = [int(s.px*94), int(s.py*70)]
        s.popup_text_rect = [int(round(s.px*3)), s.title_rect[3], int(s.px*94)-int(round(s.px*3)), int(s.py*70)]
        # The rect of the draw area without bar
        #s.area_wobar = 
        # Arrows used in lists or menus
        #s.arrow_pos = [(s.softkeys_rect[3] - s.softkeys_rect[1]) * 0.60
        
        #   # General Fonts #  #
        
        s.default_font = None
        s.softkey_font = (None, int((s.softkeys_rect[3] - s.softkeys_rect[1])*.75))
        s.popup_font = u'Nokia Sans SemiBold S60'
        s.about_font = ('normal', s.py*10, FONT_ANTIALIAS)
        s.title_font = (None, int(s.title_rect[3]*.70))
        
        #   # Colors #  #
        
        #Image viewer background color
        s.IV_bg_color = 0
        
        # TEXT VIEWER #
        
        s.text_viewer_font = (None, s.py*5)
        # Start X pos
        s.TV_x = int(round(s.px*3))
        s.TV_text_width = s.scrollbar_rect[0] - s.TV_x - s.TV_x
        s.text_area_rect = [0, s.title_rect[3], s.scrollbar_rect[0], s.softkeys_rect[1]]
        #s.v_scrollbar_rect = (s.TV_x, s.softkeys_rect[1]-int(s.px*3), s.TV_text_width, int(s.px*3))
        
        # AUDIO PLAYER #
        
        s.tags_position = (s.TV_x, s.title_rect[3] + int(s.py*10))
        s.lyrics_font = 'dense'
        s.lyrics_pos = (None, s.dy/2)
        s.icons_pos = (s.dx * .63, s.dy * .82)
        s.icons_size = 10
        s.volume_bar_rect = (s.dx * .914, s.dy * .653, s.dx * .954, s.dy * .856)
        s.seek_bar_rect = (s.TV_x, s.dy * .822, s.dx * .602, s.dy * .856)
        s.audio_info_rect = (int(s.seek_bar_rect[0]), int(s.seek_bar_rect[1] - (s.py * .058)), int(s.seek_bar_rect[2]), int(s.seek_bar_rect[1] - 2))
            # s.main.rectangle((5,171,106,178), settings.text_color)
            # s.main.rectangle((6,172,x_per,177), settings.playerbar_color1, settings.playerbar_color2)
            # s.main.rectangle((162,177-(settings.volume*4),167,177), settings.playerbar_color1, settings.playerbar_color2)
            # s.main.rectangle((161,136,168,178), settings.text_color)
            # text_right(s.main,168,u'%s' % (s.ms_to_hh_mm(duration)), settings.text_color, "legend", 106)
            # s.main.text((6,168),u'%s' % (s.ms_to_hh_mm(current_position)), settings.text_color, "legend")
            # s.main.text((6,156),_(u"%s di %s")%(s.audio_index+1,len(s.audio_list)), settings.text_color, "legend")
    def after_graphics_boot(s):
        # MENU #

        s.mnbg_bright = -35
        s.submnbg_bright = -35
        s.mn_sel_Yspacing = 5
        s.mn_sel_Xspacing = 5
        s.mn_x = 0
#        s.mn_y =
        s.mn_x_size = grafica.mn_sel.size[0] + (s.mn_sel_Xspacing * 2)
        s.mn_element_size = (grafica.mn_sel.size[1] + s.mn_sel_Yspacing)
        s.mn_element_size2 = grafica.mn_sel.size[1]
        s.mn_text_height = grafica.mn_sel.size[1] * .60
        s.mn_text_x = s.mn_x + s.mn_sel_Xspacing + 5
        s.mn_text_x_size = grafica.mn_sel.size[0] - 10
        s.mn_elem_page =  int(ui.display_size[1] * .60 / s.mn_element_size)

        # SubMenu #

        #s.submn_element_size = (grafica.submn_sel.size[1] + 5)
        #s.submn_element_size2 = grafica.submn_sel.size[1]
        #s.submn_text_height = grafica.submn_sel.size[1] * .60
        #s.submn_lenght = (grafica.submn_sel.size[0] + 4)
        
        s.submn_sel_Yspacing = 5
        s.submn_sel_Xspacing = 5
#        s.mn_y =
        s.submn_x_size = (grafica.submn_sel.size[0] + (s.submn_sel_Xspacing * 2))#grafica.submn_sel.size[0] + (s.submn_sel_Xspacing * 2)
        s.submn_x = s.dx - s.submn_x_size
        s.submn_sel_x = s.submn_x + s.submn_sel_Xspacing
        s.submn_element_size = (grafica.submn_sel.size[1] + s.submn_sel_Yspacing)
        s.submn_element_size2 = grafica.submn_sel.size[1]
        s.submn_text_height = grafica.submn_sel.size[1] * .60
        s.submn_text_x = s.submn_x + s.submn_sel_Xspacing + 5
        s.submn_text_x_size = grafica.submn_sel.size[0] - 10
        s.submn_elem_page =  int(ui.display_size[1] * .60 / s.submn_element_size)
        s.submn_y_max_size = s.submn_elem_page * s.submn_element_size
        s.submn_y = s.softkeys_rect[1] - s.submn_y_max_size
    
    def set_default_bar_colors(s, bar):
        bar.bg_fill_color = settings.scroll_bar_bg_color1
        bar.bg_outline_color = settings.scroll_bar_bg_color2
        bar.bar_fill_color = settings.s.scroll_bar_main_color1
        bar.bar_outline_color = settings.s.scroll_bar_main_color2
        
    def reload(s):
        s.__init__()
        s.after_graphics_boot()
        
    def graphics(s):
        sz = ui.display_size
        # Backgrounds
        s.bg_img = Image.new(sz)
        
        s.spuntoimg = Image.open(directory.skin_dir+"\\spunto.png")
        
        s.csel_img_normal = Image.open(directory.skin_dir+"\\selezione.jpg")

        s.csel_img_landscape = Image.open(directory.skin_dir+"\\selezione_LS.jpg")

        s.csel_img_mask_normal = Image.open(directory.skin_dir+"\\selezione_mask.bmp")
        s.csel_img_mask_landscape = Image.open(directory.skin_dir+"\\selezione_LS_mask.bmp")
        # Icons
        s.appimg = Image.open(directory.skin_dir+"\\Application.png")
        s.file_img = Image.open(directory.skin_dir+"\\File.png")
        s.cartella_img = Image.open(directory.skin_dir+"\\Cartella.png")
        s.dll_img = Image.open(directory.skin_dir+"\\dll.png")
        s.ingranaggio_img = Image.open(directory.skin_dir+"\\ingranaggio.png")
        s.internet_img = Image.open(directory.skin_dir+"\\internet.png")
        s.mmc_img = Image.open(directory.skin_dir+"\\mmcmemory.png")
        s.tel_img = Image.open(directory.skin_dir+"\\telmemory.png")
        s.musica_img = Image.open(directory.skin_dir+"\\musica.png")
        s.mail_img = Image.open(directory.skin_dir+"\\Mail.png")
        s.ram_img = Image.open(directory.skin_dir+"\\rammemory.png")
        s.rom_img = Image.open(directory.skin_dir+"\\rommemory.png")
        s.video_img = Image.open(directory.skin_dir+"\\video.png")
        s.immagine_img = Image.open(directory.skin_dir+"\\immagine.png")
        s.settings_img = Image.open(directory.skin_dir+"\\settings.png")
        s.archive_img = Image.open(directory.skin_dir+"\\Archivio.png")
        s.vcf_img = Image.open(directory.skin_dir+"\\Vcf.png")
        s.sis_img=Image.open(directory.skin_dir+"\\Sis_installer.png")
        s.text_img = Image.open(directory.skin_dir+"\\testo.png")
        s.pycon_img = Image.open(directory.skin_dir+"\\Python.png")

        #Maschere init
        
        s.appimg_mask = Image.new((32,32), 'L')
        s.file_img_mask = Image.new((32,32), 'L')
        s.cartella_mask = Image.new((32,32), 'L')
        s.dll_img_mask = Image.new((32,32), 'L')
        s.ingranaggio_img_mask = Image.new((32,32), 'L')
        s.internet_img_mask = Image.new((32,32), 'L')
        s.mmc_img_mask = Image.new((32,32), 'L')
        s.tel_img_mask = Image.new((32,32), 'L')
        s.musica_img_mask = Image.new((32,32), 'L')
        s.mail_mask = Image.new((32,32), 'L')
        s.ram_img_mask = Image.new((32,32), 'L')
        s.rom_img_mask = Image.new((32,32), 'L')
        s.video_img_mask = Image.new((32,32), 'L')
        s.immagine_img_mask = Image.new((32,32), 'L')
        s.settings_img_mask = Image.new((32,32), 'L')
        s.archive_mask = Image.new((32,32), 'L')
        s.vcf_mask = Image.new((32,32), 'L')
        s.sis_mask = Image.new((32,32), 'L')
        s.text_mask = Image.new((32,32), 'L')
        s.spunto_mask = Image.new((14,14), 'L')
        s.pycon_mask = Image.new((32,32), 'L')
        #Caricamento maschera;d.forward()
        s.appimg_mask.load(directory.skin_dir+"\\Application_mask.bmp")
        s.file_img_mask.load(directory.skin_dir+"\\File_mask.bmp")
        s.cartella_mask.load(directory.skin_dir+"\\Cartella_mask.bmp")
        s.dll_img_mask.load(directory.skin_dir+"\\dll_mask.bmp")
        s.ingranaggio_img_mask.load(directory.skin_dir+"\\ingranaggio_mask.bmp")
        s.internet_img_mask.load(directory.skin_dir+"\\internet_mask.bmp")
        s.mmc_img_mask.load(directory.skin_dir+"\\mmcmemory_mask.bmp")
        s.tel_img_mask.load(directory.skin_dir+"\\telmemory_mask.bmp")
        s.musica_img_mask.load(directory.skin_dir+"\\musica_mask.bmp")
        s.mail_mask.load(directory.skin_dir+"\\mail_mask.bmp")
        s.ram_img_mask.load(directory.skin_dir+"\\rammemory_mask.bmp")
        s.rom_img_mask.load(directory.skin_dir+"\\rommemory_mask.bmp")
        s.video_img_mask.load(directory.skin_dir+"\\video_mask.bmp")
        s.immagine_img_mask.load(directory.skin_dir+"\\immagine_mask.bmp")
        s.settings_img_mask.load(directory.skin_dir+"\\settings_mask.bmp")
        s.archive_mask.load(directory.skin_dir+"\\archivio_mask.bmp")
        s.vcf_mask.load(directory.skin_dir+"\\vcf_mask.bmp")
        s.sis_mask.load(directory.skin_dir+"\\Sis_installer_mask.bmp")
        s.text_mask.load(directory.skin_dir+"\\testo_mask.bmp")
        s.spunto_mask.load(directory.skin_dir+"\\spunto_mask.bmp")
        s.pycon_mask.load(directory.skin_dir+"\\Python_mask.bmp")
        #menu

        s.bg_img = s.bg_img_normal
        s.csel_img = s.csel_img_normal#.resize((176,16))
        s.csel_img_mask = Image.new(s.csel_img.size,'L')
        s.csel_img_mask.blit(s.csel_img_mask_normal)
        
        s.mn_sel = s.csel_img.resize((168,16))
        s.mn_sel_mask = s.csel_img_mask.resize((168,16))
        s.submn_sel = s.csel_img.resize((100,16))
        s.submn_sel_mask = s.csel_img_mask.resize((100,16))
    def screen_change(s):

        if ui.landscape:
            s.bg_img=s.bg_img_landscape
            s.csel_img=s.csel_img_landscape
            s.csel_img_mask=Image.new(s.csel_img_mask_landscape.size,'L')
            s.csel_img_mask.blit(s.csel_img_mask_landscape)
            s.mn_i=s.csel_img.resize((200,16))
            s.mn_i_mask=s.csel_img_mask.resize((200,16))

        else:
            s.bg_img=s.bg_img_normal
            s.csel_img=s.csel_img_normal
            s.csel_img_mask=Image.new(s.csel_img_mask_normal.size,'L')
            s.csel_img_mask.blit(s.csel_img_mask_normal)
            s.mn_i=s.csel_img.resize((168,16))
            s.mn_i_mask=s.csel_img_mask.resize((168,16))

# TODO: HERE TO BE PUT IN A MODULE!!!
THM_CONFIG_FILE = "%s_config.dat"
THM_ENGINE_VER = 2.00 # if the version saved in theme is lower (warn) or upper (try to load but warn, ask update)
THM_MANIFEST_EXT = ".wth" # Winfile THeme

class SknOBJ:

    def __init__(s, path):

        s._skin_path, s._skin_filename = os.path.split(path)
        s._current_profile = 0
        s.name = None
        s.author = None
        s.version = 0.0
        s.description = None
        s.docpath = None
        s.engine_version = THM_ENGINE_VER
        s.profiles = {"default":None} # SkinUI instances??
    
    def parse_version(s):

        if s.engine_version > THM_ENGINE_VER:
        
            print "The current skin needs an updated version of WinFile Theme Manager!"
            print "Current:", THM_ENGINE_VER, " Needs:", s.engine_version
            return -1
        
        elif s.engine_version < THM_ENGINE_VER:
        
            print "Warn: the current skin may be updated to the latest engine version..."
            return -2
        
        return 0
    
    def save_cfg(s):
    
        f = os.path.join(s._skin_path, THM_CONFIG_FILE%(s._skin_filename))
    
    def load_cfg(s):
    
        f = os.path.join(s._skin_path, THM_CONFIG_FILE%(s._skin_filename))

class _SkinMGMT:
    
    def __init__(s):
    
        s._skin_number = 0
        s._skin_list = []
        
    def GetSkins(s):
    
        d = directory.allskin_dir
        # Perform a depth scan
        # A folder is allowed to store more than 1 theme file
        gestione_file.scan_dir(d, 1, 1)
    
    def config_save(s, thm):
    
        thm.save_cfg()

MOVE_LEFT = 1
MOVE_RIGHT = 2
MOVE_UP = 4
MOVE_DOWN = 8
MOVE_NONE = 16
MOVE_UPLEFT = MOVE_LEFT|MOVE_UP
MOVE_UPRIGHT = MOVE_RIGHT|MOVE_UP
MOVE_DOWNLEFT = MOVE_LEFT|MOVE_DOWN
MOVE_DOWNRIGHT = MOVE_RIGHT|MOVE_DOWN

#TODO: kinetic scroll
'''
si deve avere un timer che normalmente è inattivo. Appena si tocca e si sposta lo stilo deve entrare in funzione.
Frequenza almeno 0.1 secondi. A ogni chiamata diminuisci sempre di pù la velocità con un fattore costante.
Funz callback sempre deve contenere metodo avvio timer e salvare la velocità di partenza.
'''

class TouchDriver:
    def __init__(s, rect, callback = (None, None, None,), x_speed = 0.90, y_speed = 0.90, kinetic = 0):

        # Here are set the last coordinates received, None at init
        s.last_coords = None
        s.kinetic = kinetic
        # The speed of both X & Y movement (% of the axis size)
        # 1-> full speed (one pixel resolution, immediate movement recognizing)
        # 0-> axis deactivated
        # default value 90 %
        s.x_speed = x_speed
        s.y_speed = y_speed
        # The touchable area
        s.rect = rect
        s.lx = abs(s.rect[0] - s.rect[2])
        s.ly = abs(s.rect[1] - s.rect[3])
        # Precision based on speed
        s.dx = s.lx * (1.0-s.x_speed)
        s.dy = s.ly * (1.0-s.y_speed)
        s.cb = callback[0]
        s.down_call = callback[1]
        s.up_call = callback[2]
        # Kinetic part
        s.speed = 0
        s.last_x = 0
        s.last_y = 0

    def start(s):
    
        ui.bind_touch(EDrag, s.drag_cb, s.rect)
        ui.bind_touch(EButton1Up, s.up_cb, s.rect)
        ui.bind_touch(EButton1Down, s.down_cb, s.rect)

    def stop(s):

        ui.unbind_touch(EDrag, s.drag_cb, s.rect)
        ui.unbind_touch(EButton1Up, s.up_cb, s.rect)
        ui.unbind_touch(EButton1Down, s.down_cb, s.rect)

    def drag_cb(s, coords):

        direction, x, y = s.get_direction(coords)
        if s.cb:
            s.cb(direction, x, y)

    def up_cb(s, coords):
        
        print "TouchDriver: up"
        s.last_x, s.last_y = coords
        if s.up_call:
            s.up_call(coords)

    def down_cb(s, coords):
    
        print "TouchDriver: down"
        s.last_x, s.last_y = coords
        if s.down_call:
            s.down_call(coords)

    def get_direction(s, coords):
        
        s.last_x, s.last_y = coords
        mov = MOVE_NONE
        if coords == None:
            return mov, 0, 0
        if s.last_coords == None:
            s.last_coords = coords
            return mov, 0, 0
        x, y = coords
        ox, oy = s.last_coords

        #Movement along the X axis
        xdiff = abs(x-ox)
        if xdiff > s.dx:
            if (x > ox):

                mov |= MOVE_RIGHT

            elif (x < ox):

                mov |= MOVE_LEFT
        #Movement along the Y axis
        ydiff = abs(y-oy)
        if ydiff > s.dy:
        
            if (y > oy):
                
                mov |= MOVE_DOWN

            elif (y < oy):

                mov |= MOVE_UP

        s.last_coords = coords
        return mov, xdiff, ydiff
    
    def kinetic_engine(s):
        
        while s.speed:
            pass
    
    def kinetic_cb(s, event):

        s.list_speed -= (s.last_y - event[1])/2.0

        s.last_x, s.last_y = event
        # if abs(s.list_speed)>5:
            # s.list_is_down=False

# A number of mouse moves are ignored after a press to differentiate
# it from a press & drag.
gMaxIgnoredMouseMoves = 4
# The timer measures the drag speed & handles kinetic scrolling. Adjusting
# the timer interval will change the scrolling speed and smoothness.
gTimerInterval = 0.20
# The speed measurement is imprecise, limit it so that the scrolling is not
# too fast.
gMaxDecelerationSpeed = 30
# influences how fast the scroller decelerates
gFriction = .5

class KineticDriver:
    def __init__(s, rect, callback = (None, None, None,), x_speed = 0.90, y_speed = 0.90):

        # Here are set the last coordinates received, None at init
        s.last_coords = None
        # The speed of both X & Y movement (% of the axis size)
        # 1-> full speed (one pixel resolution, immediate movement recognizing)
        # 0-> axis deactivated
        # default value 90 %
        s.x_speed = x_speed
        s.y_speed = y_speed
        # The touchable area
        s.rect = rect
        s.lx = abs(s.rect[0] - s.rect[2])
        s.ly = abs(s.rect[1] - s.rect[3])
        # Precision based on speed
        s.dx = s.lx * (1.0-s.x_speed)
        s.dy = s.ly * (1.0-s.y_speed)
        s.cb = callback[0]
        s.down_call = callback[1]
        s.up_call = callback[2]
        # Kinetic part
        s.speed = 0
        s.last_x = 0
        s.last_y = 0

        s.scrollArea = None
        s.isPressed = False
        s.isMoving = False
        s.actual_pos = 0
        s.lastMouseYPos = 0
        s.lastScrollBarPosition = 0
        s.velocity = 0
        s.ignoredMouseMoves = 0
        s.ignoredMouseActions = 0
        s.lastPressPoint = None
        s.kineticTimer = e32.Ao_timer() # cb->onKineticTimerElapsed
    
    # def isTimerActive(s):
        # try:
            # s.kineticTimer.after(0.1, lambda: None)
        # except:
            # return 1
        # return 0
        
    def timer_cb(s):

        s.onKineticTimerElapsed()
        s.kineticTimer.after(gTimerInterval, s.timer_cb)

    def stopMotion(s):

        s.isMoving = False
        s.velocity = 0
        s.kineticTimer.cancel()

    #! intercepts mouse events to make the scrolling work
    def eventFilter(s, event, pos):

        #s.actual_pos = pos
        if (event == EButton1Down):
          
            s.isPressed = True
            s.lastPressPoint = pos
            #s.lastScrollBarPosition = s.scrollArea->verticalScrollBar()->value()
            if s.isMoving: # press while kinetic scrolling, so stop
                s.stopMotion()

        elif (event == EDrag):
          
            if not s.isMoving:

                # A few move events are ignored as "click jitter", but after that we
                # assume that the user is doing a click & drag
                if s.ignoredMouseMoves < gMaxIgnoredMouseMoves:
                    s.ignoredMouseMoves += 1
                else:
                    s.ignoredMouseMoves = 0
                    s.isMoving = True
                    s.lastMouseYPos = pos[1]
                   #if not s.isTimerActive():
                    try:
                        s.kineticTimer.after(gTimerInterval, s.timer_cb)
                    except:
                        pass
            else:
             
                # manual scroll
                s.drag_cb(pos)
                #dragDistance = pos[1] - s.lastPressPoint[1]
                # s.scrollArea->verticalScrollBar()->setValue(
                   # s.lastScrollBarPosition - dragDistance)

        elif (event == EButton1Up):
          
             s.isPressed = False
             s.ignoredMouseMoves = 0
             # Looks like the user wanted a single click. Simulate the click,
             # as the events were already consumed
             if not s.isMoving:
             
                # QMouseEvent* mousePress = new QMouseEvent(QEvent::MouseButtonPress,
                   # s.lastPressPoint, Qt::LeftButton, Qt::LeftButton, Qt::NoModifier)
                # QMouseEvent* mouseRelease = new QMouseEvent(QEvent::MouseButtonRelease,
                   # s.lastPressPoint, Qt::LeftButton, Qt::LeftButton, Qt::NoModifier)

                s.ignoredMouseActions = 2
                # QApplication::postEvent(object, mousePress)
                # QApplication::postEvent(object, mouseRelease)

        #return True # filter event
    

    def onKineticTimerElapsed(s):
    
        if s.isPressed and s.isMoving:

            # the speed is measured between two timer ticks
            cursorYPos = s.last_y#s.scrollArea->mapFromGlobal(QCursor::pos()).y()
            s.velocity = cursorYPos - s.lastMouseYPos
            s.lastMouseYPos = cursorYPos
       
        elif (not s.isPressed) and s.isMoving:

            # use the previously recorded speed and gradually decelerate
            s.velocity = max(-gMaxDecelerationSpeed, min(s.velocity, gMaxDecelerationSpeed))
            if( s.velocity > 0 ):
                s.velocity -= gFriction
            elif( s.velocity < 0 ):
                s.velocity += gFriction
            if( abs(s.velocity) < abs(gFriction) ):
                s.stopMotion()
            s.drag_cb((s.last_x, s.lastMouseYPos - s.velocity))
            #s.lastMouseYPos = s.lastMouseYPos - s.velocity
            #print "kinetic cb..."
          # scrollBarYPos = s.scrollArea->verticalScrollBar()->value()
          # s.scrollArea->verticalScrollBar()->setValue(scrollBarYPos - s.velocity)

        else:
            s.stopMotion()

    def start(s):
    
        ui.bind_touch(EDrag, lambda c: s.eventFilter(EDrag, c), s.rect)
        ui.bind_touch(EButton1Up, lambda c: s.eventFilter(EButton1Up, c), s.rect)
        ui.bind_touch(EButton1Down, lambda c: s.eventFilter(EButton1Down, c), s.rect)

    def stop(s):

        ui.unbind_touch(EDrag, lambda c: s.eventFilter(EDrag, c), s.rect)
        ui.unbind_touch(EButton1Up, lambda c: s.eventFilter(EButton1Up, c), s.rect)
        ui.unbind_touch(EButton1Down, lambda c: s.eventFilter(EButton1Down, c), s.rect)

    def drag_cb(s, coords):

        direction, x, y = s.get_direction(coords)
        if s.cb:
            s.cb(direction, x, y)

    def get_direction(s, coords):
        
        s.last_x, s.last_y = coords
        mov = MOVE_NONE
        if coords == None:
            return mov, 0, 0
        if s.last_coords == None:
            s.last_coords = coords
            return mov, 0, 0
        x, y = coords
        ox, oy = s.last_coords

        #Movement along the X axis
        xdiff = abs(x-ox)
        if xdiff > s.dx:
            if (x > ox):

                mov |= MOVE_RIGHT

            elif (x < ox):

                mov |= MOVE_LEFT
        #Movement along the Y axis
        ydiff = abs(y-oy)
        if ydiff > s.dy:
        
            if (y > oy):
                
                mov |= MOVE_DOWN

            elif (y < oy):

                mov |= MOVE_UP

        s.last_coords = coords
        return mov, xdiff, ydiff

# class TouchScroller:

    # def __init__(s, elements):
        
        # s.elem = elements #[bbox1, bbox2]
    
    # def pressing(s):
        # pass
    # def released(s):
        # pass

class unzip:
    def extract(self, file, dir):
        if not dir.endswith(':') and not os.path.exists(dir):
            os.mkdir(dir)

        zf = zipfile.ZipFile(file)

        self._createstructure(file, dir, zf)

        for name in zf.namelist():
            if not name.endswith('/'):
                outfile = open(os.path.join(dir, name), 'wb',10000)
                outfile.write(zf.read(name))
                outfile.flush()
                outfile.close()
        zf.close()


    def _createstructure(self, file, dir, zf):
        self._makedirs(self._listdirs(file, zf), dir)


    def _makedirs(self, directories, basedir):
        #""" Create any directories that don't currently exist """
        for dir in directories:
            curdir = os.path.join(basedir, dir)
            if not os.path.exists(curdir):
                os.mkdir(curdir)

    def _listdirs(self, file, zf):
        # """ Grabs all the directories in the zip structure
        # This is necessary to create the structure before trying
        # to extract the file to it. """
        #zf = zipfile.ZipFile(file)
        dirs = []

        for name in zf.namelist():
            if name.endswith('/'):
                dirs.append(name)

        dirs.sort()
        return dirs


#t=time.time()
__supported_encodings__ = ['ascii', 'utf8', 'latin1', 'iso-8859-1', 'utf16']

def ru(x):
#Only utf8 decoding. Deprecateded: use to_unicode
    return x.decode('utf-8')

def ur(x):
#Only utf8 decoding. Deprecateded: use to_unicode
    return x.encode('utf-8')

def to_unicode(x):
# This an important coding feature...!
    if type(x) == types.UnicodeType:
        return x
    else:
        try:
            return ru(x) #utf8: the most common to try
        except:
            for enc in ['ascii', 'latin1', 'iso-8859-1']:
                try:
                    return x.decode(enc)
                    #break
                except UnicodeError:
                    continue
            return x

def decode_text(text):
# Used to decode a text stream (maybe a file)
    if text.startswith('\xff\xfe') or text.startswith('\xfe\xff'): #Se è unicode (utf16)
        text = text.decode('utf16')
    elif text.startswith('\xef\xbb\xbf'): #Se è utf8
        text = text.decode('utf8')
    else:
        for enc in __supported_encodings__:
            try:
                text = text.decode(enc)#.replace(u"\x00","")
                break
            except UnicodeError:
                pass
        else:
            raise UnicodeError
    return text

def load_text_file(file):
        #TODO: improve utf-16 detection
        f = open(file, 'r')
        text = f.read()
        f.close()
        if text.startswith('\xff\xfe') or text.startswith('\xfe\xff'):# or text.find("\x20\x29")!=-1 or text.find("\x0d\x00\x0a\x00")!=-1: #Se è unicode (utf16)
            enc = 'utf16' #Codifica x l'unicode
            text = text.decode(enc)
        elif text.startswith('\xef\xbb\xbf'): #Se è utf8
            enc = 'utf8'
            text = text.decode(enc)
        else:
            for enc in __supported_encodings__:
                try:
                    text = text.decode(enc).replace(u"\x00","")
                    break
                except UnicodeError:
                    pass
            else:
                raise UnicodeError
        return text.replace(u'\r\n', u'\u2029').replace(u'\n', u'\u2029') , enc , len(text) , u'\u2029'

def inverti_bn(img):
    maschera=Image.new(img.size,"1")
    maschera.blit(img)
    img=Image.new(img.size,"1")
    img.clear(0)
    img1=Image.new(img.size,"1")
    img1.clear((255,255,255))
    img1.blit(img,mask=maschera)
    return img1

def crea_icone(file_aif):
    #Reads an aif file and returns icon and its mask
    images = []
    txt = open(file_aif).read()
    count=0
    while 1:
        if count==2: break
        count+=1
        i = txt.find('(\x00\x00\x00')
        if (i < 4):
            break
        (l,) = struct.unpack('i', txt[(i - 4):i])
        if (l > 40):
            mbm = txt[(i - 4):((i - 4) + l)]
        else:
            txt = txt[(i + 4):]
            continue
        open('d:\\WFtemp.mbm', 'w').write('7\x00\x00\x10B\x00\x00\x10\x00\x00\x00\x009d9G' + struct.pack('i', (l+20)) + mbm + '\x01\x00\x00\x00\x14\x00\x00\x00')
        try:
            img = Image.open('d:\\WFtemp.mbm')
            images.append(img.resize((32,32),keepaspect=1))
            del img
        except:
            txt = txt[(i + 4):]
            continue
        txt = txt[((i - 4) + l):]
    try: os.remove('d:\\WFtemp.mbm')
    except: pass
    try:
        i=Image.new(images[1].size,"1")
        i.blit(inverti_bn(images[1]))
    except:
        i=images[1]
    return images[0],i

def get_UID(app):
    f = open(app)
    uid1,uid2,uid3 = map(lambda x: hex(x).strip('L'),struct.unpack('LLL',f.read(12)))
    f.close()
    return uid1,uid2,uid3

def luminosita(img,perc):
    if not perc:
        return img
    maschera=Image.new(img.size,"L")
    immagine=Image.new(img.size)
    perc=int(perc*2.55)
    if perc>0:
        immagine.clear((255,255,255))
    else:
        perc=-perc
        immagine.clear((0,0,0))
    perc=255-perc
    maschera.clear((perc,perc,perc))
    immagine.blit(img,mask=maschera)
    del maschera
    return immagine

def blur(img, val):
    if not val:
        return
    im = Image.new(img.size)
    im.blit(img)
    mask = Image.new(img.size, 'L')
    mask.clear((val, val, val))
    img.blit(im, target=(1,0), mask= mask)
    img.blit(im, target=(0,1), mask= mask)
    img.blit(im, target=(-1,0), mask= mask)
    img.blit(im, target=(0,-1), mask= mask)

def color_mixer(start, end, perc):
    r,g,b = start
    r2,g2,b2 = end
    rr,gr,br = abs(r2-r)*perc, abs(g2-g)*perc, abs(b2-b)*perc
    return (int(min(r,r2) + rr), int(min(g,g2) + gr) , int(min(b,b2) + br))

def text_center(img,y1,testo, fil=(0,0,0), font=None): #Centra testo
    x = img.size[0]
    l = img.measure_text(testo, font)[1]
    img.text((((x - l) / 2),y1), testo, fil, font)

def text_cut(img, pos , testo, fill=(0,0,0), font=None,end=u"..."): #Taglia testo se superiore allo schermo
    x = img.size[0]
    lenn = img.measure_text(testo,font,x-pos[0])[2]
    if len(testo)<=lenn:
        img.text(pos, testo, fill, font)
    else:
        img.text(pos,testo[:lenn-len(end)]+end, fill, font)

def text_right(img,y,text,color=(0,0,0),font=None,x=None):
    l=img.measure_text(text, font)[1]
    if x:
        img.text((x-l,y), text, color, font)
    else:
        img.text((img.size[0]-l,y), text, color, font)

# def CreateMask(img):
    # width, height = img.size
    # mask = Image.new(img.size, '1')
    # transparent_color = img.getpixel((0,0))[0]
    # for y in range(height):
        # line = img.getpixel([(x, y) for x in range(width)])
        # for x in range(width):
            # if line[x] == transparent_color:
                # mask.point((x,y), 0)
    # return mask

class user_messages:
    def __init__(s):
        s.state = 0 #Used in query()
        s.panel = None
        s.tobj = None
        s.coord = None
        s.title = None
        s.in_use = 0

    def check_queue(s, f):
        if s.queue:
            print "popup: waiting for user!"
            s.queue.append(f)
            return 1
        else:
            print "popup: ok, no wait"
            return 0

    def draw_panel(s, __direct__ = 0):
        if s.panel and s.tobj and s.coord:
            px,py = s.panel.size
            s.panel.clear(0xffffff)
            if s.title:
                text_render(s.panel, [0,0,px,skinUI.title_rect[3]], s.title, settings.path_color, skinUI.title_font, ALIGNMENT_CENTER, 1)
            s.panel.rectangle([(0,0),(px,py)], outline = settings.window_border, width = 1)
            s.tobj.text_redraw(s.panel)
            if __direct__:
                ui.direct_draw(s.panel, s.coord)
            else:
                ui.draw(s.panel, s.coord)

    def create_panel(s, text, title):
        cx,cy = ui.display_size
        s.tobj = Text_Object(text, skinUI.popup_text_rect, ALIGNMENT_LEFT|ALIGNMENT_UP, s.draw_panel)
        height = s.tobj.max_rectY_size + (skinUI.title_rect[3]*2)
        s.panel = Image.new((skinUI.popup_size[0], height))
        s.coord = (6,(cy/2) - height/2)
        s.title = title

    def note(s, text, title = None, timeout = 3, _direct_ = 0): #timeout <=0 equivale al tasto OK: l'utente chiude la finestra

        # if s.check_queue(lambda: s.note(text, title, timeout, _direct_)):
            # return
        #if s.in_use:
        # while s.in_use:
            # e32.Ao_yield()
        s.in_use = 1
        s.create_panel(text, title)
        
       # alpha_panel=Image.new((ui.canvas_image.size[0]-12,30+(len(to_draw)*12)),"L")
        # try:
            ##TODO: here shouldn't be anymore a try statement (new skin code, always present img object, empty at start)
            # panel.blit(grafica.bg_img, target=(-((cx-(cx-12))/2),0))
        # except:
            # pass
        
    
        if _direct_:
            s.draw_panel(1)
            return

        prev = ui.get_state()
        ui.reset_ui()
        ui.switch_allowed = 0
        s.tobj.bind()
        prev_img = Image.new(ui.canvas_image.size)
        prev_img.blit(ui.canvas_image)
        lc = e32.Ao_lock()
        if timeout<=0:
            #ui.mode_callback= lambda: ui.draw(panel,target=(6,(ui.canvas_image.size[1]/2)-panel.size[1]/2))
            #ui.mode_callback=s.draw
            ui.left_key = [lc.signal, _(u"Ok")]
            ui.bind(EScancodeSelect, lc.signal)
        else:
            e32.ao_sleep(timeout, lc.signal)
            e32.ao_sleep(0.2)
            ui.key_callback = lambda k: lc.signal()

        #ui.draw(panel,target=(6,(ui.canvas_image.size[1]/2)-panel.size[1]/2))
      #  tg=(6,(ui.canvas_image.size[1]/2)-panel.size[1]/2)
       # for a in xrange(0,256,4):
          #  alpha_panel.clear((a,a,a))
        #    ui.canvas.blit(panel,mask=alpha_panel,target=tg)
           # e32.ao_sleep(0.01)
           # e32.Ao_yield()
        s.draw_panel()
        lc.wait()
        ui.draw(prev_img)
        ui.set_state(prev)
        ui.canvas_refresh()
        #Cleanup
        s.panel = None
        s.tobj = None
        s.coord = None
        s.title = None
        s.in_use = 0

    def direct_note(s, text, title = None):
        s.note(text, title, _direct_=1)

    def query(s, text, title = None, left = None, right = None):
        cx,cy = ui.display_size
        s.state = 0
        if not left:
            left=_(u"Ok")
        if not right:
            right=_(u"Annulla")
        def acc():
            lc.signal()
            s.state = 1

        s.create_panel(text, title)

        prev = ui.get_state()
        ui.reset_ui()
        ui.switch_allowed = 0
        prev_img = Image.new(ui.canvas_image.size)
        prev_img.blit(ui.canvas_image)
        lc = e32.Ao_lock()
        ui.left_key = [acc,left]
        ui.right_key = [lc.signal,right]
        ui.bind(EScancodeSelect, acc)
        
        s.draw_panel()

        lc.wait()
        ui.draw(prev_img)
        ui.set_state(prev)
        ui.canvas_refresh()
        #Cleanup
        s.panel = None
        s.tobj = None
        s.coord = None
        s.title = None
        return s.state

class progress_dialog:
    def __init__(s, text, title=None, break_cb=None, actual=0, max=100, step=1):
        s.actual = actual
        s.max = max
        s.step = step
        s.text = text
        s.title = title
        s.panel = None
        s.tobj = None
        s.coord = None
        s.perc = float(s.actual) / float(s.max) * 100.0
        #s.init_text()
        #s.init_graph()
        s.create_panel()
        s.prev = ui.get_state()
        ui.reset_ui()
        ui.switch_allowed=0
        s.prev_img = Image.new(ui.canvas_image.size)
        s.prev_img.blit(ui.canvas_image)
        if break_cb:
            ui.right_key = [break_cb, _(u"Annulla")]
        #ui.canvas_refresh()
        s.draw()

    def close(s):
        ui.draw(s.prev_img)
        ui.set_state(s.prev)
        ui.canvas_refresh()
        del s.prev,s.prev_img,s.panel

    # def init_text(s):
        # linee=s.text.splitlines()
        # s.to_draw=[]
        # try:
            # for linea in linee:
                # t=wrap_text_to_array(linea,u'Nokia Sans SemiBold S60',ui.canvas_image.size[0]-16)
                # if t!=(): s.to_draw+=t
                # else: s.to_draw.append("")
        # except:
            # s.to_draw=linee
        # del linee

    def update_text(s, text):
        s.tobj.text = text
        s.tobj.text_init()
        s.tobj.screen_change()

    def update_state(s, n):
        if n<0:
            return
        if n>s.max:
            return
        s.actual = n
        s.perc = float(s.actual) / float(s.max) * 100.0

    def forward(s):
        s.update_state(s.actual+s.step)

    def rew(s):
        s.update_state(s.actual-s.step)

    def draw(s):#, __direct__ = 0):
        if s.panel and s.tobj and s.coord:
            px,py = s.panel.size
            s.panel.clear(0xffffff)
            if s.title:
                text_render(s.panel, [0,0,px,skinUI.title_rect[3]], s.title, settings.path_color, skinUI.title_font, ALIGNMENT_CENTER, 1)
            s.panel.rectangle([(0,0),(px,py)], outline = settings.window_border, width = 1)
            s.tobj.text_redraw(s.panel)
            # if __direct__:
                # ui.direct_draw(s.panel, s.coord)
            # else:
            ui.draw(s.panel, s.coord)

    def create_panel(s):
        cx,cy = ui.display_size
        s.tobj = Text_Object(s.text, skinUI.popup_text_rect, ALIGNMENT_LEFT|ALIGNMENT_UP, s.draw)
        height = s.tobj.max_rectY_size + (skinUI.title_rect[3]*2)
        s.panel = Image.new((skinUI.popup_size[0], height))
        s.coord = (6,(cy/2) - height/2)

    #def init_graph(s):
        #s.panel = Image.new((ui.canvas_image.size[0]-12,50+(len(s.to_draw)*12)))#(164,50+(len(s.to_draw)*12)))
        #s.border_coord = [(0,0),(ui.canvas_image.size[0]-13,0),(ui.canvas_image.size[0]-13,s.panel.size[1]-1),(0,s.panel.size[1]-1),(0,0)]
        #s.target = (-((ui.canvas_image.size[0]-(ui.canvas_image.size[0]-12))/2),0)
        #max_chr = s.panel.measure_text(s.title,settings.mainfont,ui.canvas_image.size[0]-14)[2]
        #if len(s.title)>=max_chr:
        #    s.title=s.title[:max_chr-3] + u"..."

    def set_title(s,t):
        # To keep some backwards compatibility
        s.title = t
        # max_chr = s.panel.measure_text(t,settings.mainfont,ui.canvas_image.size[0]-14)[2]
        # if len(t)<=max_chr:
            # s.title=t
        # else:
            # s.title=t[:max_chr-3]+u"..."
    #def draw(s):
        # try:
            # s.panel.blit(grafica.bg_img,target=s.target)
        # except:
            # pass
        #text_center(s.panel,11,s.title,settings.path_color)
        #s.panel.line(s.border_coord,outline=settings.window_border,width=1)
        #i=1
        #for linea in s.to_draw:
        #    s.panel.text((10,20+(12*i)),linea,fill=settings.text_color,font=u'Nokia Sans SemiBold S60')
        #    i+=1
        #s.panel.rectangle((10,30+(12*(i-1)),s.panel.size[0]-10,40+(12*(i-1))),settings.progress_bar_bg_color1,settings.progress_bar_bg_color2)
        #s.panel.rectangle((10,30+(12*(i-1)),int((float(s.panel.size[0])-10.0)/100.0*s.perc),40+(12*(i-1))),settings.progress_bar_color1,settings.progress_bar_color2)
        #ui.draw(s.panel,target=(6,(ui.canvas_image.size[1]/2)-s.panel.size[1]/2))

class FKey:
    def __init__(self, key, cb, option = None):
        self.key = key
        self.cb = cb
        #Option is keyevent type for key; it's (rect, dx, dy) for touch event
        self.option = option

# Pointer Events
# copied from key_codes to support also old platforms
EButton1Down=0x101
EButton1Up=0x102
EButton2Down=0x103
EButton2Up=0x104
EButton3Down=0x105
EButton3Up=0x106
EDrag=0x107
EMove=0x108
EButtonRepeat=0x109
ESwitchOn=0x10A

# class Keyboard(object):
        # def __init__(self,onevent=None):
            # self._keyboard_state={}
            # self._downs={}
            # self._onevent=onevent
        # def handle_event(self,event):
            # e_type = event['type']
            # if e_type == appuifw.EEventKeyDown:
                # code=event['scancode']
                # if not self.is_down(code):
                    # self._downs[code]=self._downs.get(code,0)+1
                # self._keyboard_state[code]=1
            # elif e_type == appuifw.EEventKeyUp:
                # self._keyboard_state[event['scancode']]=0
            # if self._onevent:
                # self._onevent(event)
        # def is_down(self,scancode):
            # return self._keyboard_state.get(scancode,0)
        # def pressed(self,scancode):
            # if self._downs.get(scancode,0):
                # self._downs[scancode]-=1
                # return True
            # return False
class Keyboard(object):
#Alternative keyboard driver used in Image Viewer
        def __init__(s):#,onevent=lambda:None):
            s._keyboard_state={}
            s._downs={}
#            s._onevent=onevent
        def handle_event(s,event):
            evt = event['type']
            if evt == 3: #EEventKeyDown
                code=event['scancode']
                if not s.is_down(code):
                    s._downs[code]=s._downs.get(code,0)+1
                s._keyboard_state[code]=1
            elif evt == 2: #EEventKeyUp
                s._keyboard_state[event['scancode']]=0
#            s._onevent()
        def is_down(s,scancode):
            return s._keyboard_state.get(scancode,0)
        def pressed(s,scancode):
            if s._downs.get(scancode,0):
                s._downs[scancode]-=1
                return True
            return False
class _UI:

#This is the class to manage all the basic UI features of WinFile like softkeys, canvas, menus, keys and touch events.

    def __init__(s):
        s.canvas = None
        s.saved_state = []
        s.focus_state = 1
        s.landscape = 0
        #Input events
        s.k_type = (appuifw.EEventKey, appuifw.EEventKeyDown, appuifw.EEventKeyUp,)
        s.t_type = (EButton1Up, EButton1Down, EDrag, ESwitchOn,)
        s.bindarr = []
        s.prevbindarr = [] #For menu
        s.touchbindarr = []
        s.prevtouchbindarr = [] #For menu
        s.menuopened = 0
        s.menu_exit = None
        #Callbacks
        s.focus_cb = None
        s.key_callback = None
        s.mode_callback = None
        #SoftKeys
        s.left_key = [None,u""]
        s.sx_btn = [[],[]]
        s.right_key = [None,u""]
        s.dx_btn = [[],[]]
        #
        s.switch_allowed = 1
        s.switching_mode = 0
        #s.key_driver = Keyboard(s.key_cb)
        appuifw.app.screen = 'full'
        #init canvas
        # select drawing method based on symbian edition
        if main.S60v2:
            s.canvas_refresh = s.canvas_refresh_v2
            s.direct_draw = s.direct_draw_v2
        else:
            s.canvas_refresh = s.canvas_refresh_v3
            s.direct_draw = s.direct_draw_v3
        s.canvas = appuifw.Canvas(redraw_callback = s.canvas_refresh, event_callback = s.key_cb, resize_callback = s.resize_cb)#s.key_driver.handle_event)
        #The default screen size in portrait mode (deprecated)
        s.screen_size = s.get_screen_size()
        #The default screen size in landscape mode (deprecated)
        s.landscape_size = (s.screen_size[1],s.screen_size[0])
        #this is the actual size of the canvas
        #s.display_size = s.canvas.size
        print "Screen %ix%i"%s.screen_size#, s.canvas.size
        # init screen buffer
        s.canvas_image = Image.new(s.display_size)
        s.ui_image = Image.new(s.display_size)
        # s.key_dict = {0x30: '0', 0x31: '1', 0x32: '2', 0x33: '3', 0x34: '4', 0x35: '5', 0x36: '6', 0x37: '7', 0x38: '8', 0x39: '9', 0x2a: '*', 0x23: '#',
                    # 0xf80b: 'Matita', 8: 'C', 0xf862: 'Verde'}
        #New things to fully support 3rd / 5th edition device and new facilities
        s.touch_screen = 0
        #s.sensor_device = 0

    def get_canvas_size(s):
        if main.S60v2:
            if s.landscape:
                return s.landscape_size
            else:
                return s.screen_size
        else:
            if s.canvas:
                return s.canvas.size

    display_size = property(get_canvas_size)

    def get_screen_size(s):
        sz = sysinfo.display_pixels()
        return min(sz),max(sz)

    def save_state(s):
        #Save current UI settings
        s.saved_state = [s.bindarr,s.focus_cb,s.key_callback,s.mode_callback,s.left_key,s.right_key,s.menu.menuarr,s.menu.num,s.switch_allowed,s.touchbindarr,s.prevtouchbindarr]

    def reload_state(s):
        #Reload previous saved UI state
        s.bindarr,s.focus_cb,s.key_callback,s.mode_callback,s.left_key,s.right_key,s.menu.menuarr,s.menu.num,s.switch_allowed,s.touchbindarr,s.prevtouchbindarr = s.saved_state

    def reset_ui(s):
        #Reset UI settings to init
        s.bindarr,s.focus_cb,s.key_callback,s.mode_callback,s.left_key,s.right_key,s.menu.menuarr,s.menu.num,s.switch_allowed,s.touchbindarr,s.prevtouchbindarr=[],None,None,None,[None,u""],[None,u""],[],0,1,[],[]

    def get_state(s):
        #Return array with UI settings
        return [s.bindarr,s.focus_cb,s.key_callback,s.mode_callback,s.left_key,s.right_key,s.menu.menuarr,s.menu.num,s.switch_allowed,s.touchbindarr,s.prevtouchbindarr]

    def set_state(s,st):
        #Set UI settings from given array
        s.bindarr,s.focus_cb,s.key_callback,s.mode_callback,s.left_key,s.right_key,s.menu.menuarr,s.menu.num,s.switch_allowed,s.touchbindarr,s.prevtouchbindarr = st

    def body_init(s):
        #Prepare UI before using it
        appuifw.app.body = s.canvas
        appuifw.app.focus = s.fc_cb
        appuifw.app.menu = []
        appuifw.app.exit_key_handler = lambda: None
        s.menu = Menu(s.bindprevarr)
        try:
            s.touch_screen = appuifw.touch_enabled()
            print "Touch device found"
            appuifw.app.directional_pad = True
        except:
            #Sure no touch or pys60 too old
            s.touch_screen = 0
            print "No touch device found"
        # try:
            # import sensor
            # s.sensor = sensor
            # del sensor
            # s.sensor_device = 1
        # except:
            # s.sensor_device = 0
        s.set_softkey_touch()

    def toggle_pad(s):
        if appuifw.app.directional_pad:
            appuifw.app.directional_pad = False
        else:
            appuifw.app.directional_pad = True

    def is_landscape(s, rect):
        x,y = rect
        if (x == y):
            # Strange, but can happen. No landscape per default
            return 0
        if x>y:
            return 1
        return 0

    def resize_cb(s, rect):
        if main.S60v3:
            #print s.display_size
            mode = s.is_landscape(s.display_size)
            #if s.landscape != mode:
            s.change_screen_mode(mode)

    def left_softkey(s):
        s.openmenu()
        if s.left_key[0]:
            s.left_key[0]()

    def right_softkey(s):
        if s.menuopened:
            if s.menu_exit:
                s.menu_exit()
        else:
            if s.right_key[0]:
                s.right_key[0]()

    def set_softkey_touch(s):
        x,y = s.display_size
        s.sx_btn = [xrange(x/2+1), xrange(y-20, y+1)]
        s.dx_btn = [xrange(x/2, x+1),xrange(y-20, y+1)]

    def key_cb(s, key):
        # '''I tasti da catturare e utilizzare sono, in ordine di precedenza:
        # -Softkeys/Menu (se il tasto softkey sinistro ha anche un callback, non verrà comunque ignorato)
        # -Bind con metodo interno
        # '''
        #print s.keyboard.last['scancode']
        #print key
        #sc, kc, ty = key['scancode'], key['keycode'], key['type']
        
        #To speed up things here, avoid to use constant variables!
        ty = key['type']
        if ty in s.k_type:
            #keyboard input
            
            sc = key['scancode']
            if s.key_callback and not s.menuopened:
                s.key_callback(key)
            else:
                s.cb_capture(sc, ty)
            #Hardcoded keys (special WinFile,UI keys)
            if ty==3: #EEventKeyDown
                #SoftKeys
                if sc==164: #EStdKeyDevice0
                    s.left_softkey()
                if sc==165: #EStdKeyDevice1
                    s.right_softkey()
            elif ty==1: #EEventKey
                #Pencil key to change view mode, on the device where the key is present
                if sc == 18 and (not s.menuopened) and s.switch_allowed: #EStdKeyLeftShift
                    s.change_screen_mode()

        elif ty in s.t_type:
            #touch event input
            pos = key['pos']
            s.touch_cb(ty, pos)
            #Hardcoded keys (special WinFile,UI keys)
            if ty == EButton1Up:
                x,y = pos
                if (x in s.sx_btn[0]) and (y in s.sx_btn[1]):
                    s.left_softkey()
                if (x in s.dx_btn[0]) and (y in s.dx_btn[1]):
                    s.right_softkey()

    def get_shortcut(s, p, translate = 0):
        #p can be key code or callback assigned to key
        for fk in s.bindarr:
            if p in [fk.key, fk.cb]:
                if fk.key in s.key_dict:
                    if translate:
                        return _(s.key_dict[fk.key])
                    else:
                        return s.key_dict[fk.key]
                else:
                    return '?'

    def change_screen_mode(s, mode=None):
        #Switch screen mode by key/menu
        if s.switching_mode:
            return
        if s.menuopened:
            s.menu.close()
        if mode != None:
            if mode != s.landscape:
                s.landscape = mode
            else:
                #Already in requested mode
                return
        else:
            if s.landscape == 0:
                #instead of using two vars for each screen mode, use just one to simplify...just swap x and y!
                #s.display_size=s.display_size[1],s.display_size[0]
                s.landscape = 2
            elif s.landscape == 2:
                s.landscape = 1
            elif s.landscape == 1:
                #s.display_size=s.display_size[1],s.display_size[0]
                s.landscape = 0

        s.switching_mode = 1
        
        grafica.screen_change()
        skinUI.reload()
        s.set_softkey_touch()
        
        s.canvas_image = Image.new(s.display_size)
        s.ui_image = Image.new(s.display_size)
        
        try:
            # no chance to fail here...
            if s.mode_callback:
                s.mode_callback()
        except Exception,e:
           #print "Fatal error in s.mode_callback() in UI.change_screen_mode(): ",str(e)
           traceback.print_exc()

        s.switching_mode = 0

    def fc_cb(s,state):
        s.focus_state = state
        if not state and s.menuopened:
            s.menu.close()
        if s.focus_cb:
            s.focus_cb(state)

    def draw(s, im, target=(0,0)):
        #if s.menuopened:
            #TODO: call the background update of menu class
        s.canvas_image.blit(im, target = target)
        s.canvas_refresh()

    def direct_draw_v2(s, img, target):
            if s.landscape==1:
                s.ui_image.blit(img, target=target)
                s.canvas.blit(s.ui_image.transpose(ROTATE_90))
            elif s.landscape==2:
                s.ui_image.blit(img, target=target)
                s.canvas.blit(s.ui_image.transpose(ROTATE_270))
            else:
                s.canvas.blit(img,target=target)
    
    def direct_draw_v3(s, img, target):
        
        s.canvas.blit(img, target = target)

    def canvas_refresh_v2(s, rect=None):
        # if not (s.canvas_image.size[0] == s.canvas.size[0]):
            # try:
                # print "New canvas size",rect,s.canvas.size
                # s.resize_cb(s.canvas.size)
            # except:
                # traceback.print_exc()
        # s3 = main.S60v3
        # if s3:
            # s.canvas.begin_redraw()
        try:
            # if s.landscape==1: s.ui_image.blit(s.canvas_image.transpose(ROTATE_90))#,target=(0,0,176,208),scale=1) #LANDSCAPE :)
            # elif s.landscape==2: s.ui_image.blit(s.canvas_image.transpose(ROTATE_270))
            # else: s.ui_image.blit(s.canvas_image)
            # if s.landscape:
                # s.ui_image.text((5,174),s.left_key[1],font=u"Default",fill=settings.label_color)
                # text_right(s.ui_image,174,s.right_key[1],settings.label_color)
            # else:
                # s.ui_image.text((5,206),s.left_key[1],font=u"Default",fill=settings.label_color)
                # text_right(s.ui_image,206,s.right_key[1],settings.label_color)
            # s.canvas.blit(s.ui_image)
            if s.landscape==1:
                s.ui_image.blit(s.canvas_image)
                s.draw_softkeys(s.ui_image)
                #s.ui_image.text((3,173),s.left_key[1],fill=settings.label_color,font=settings.label_font)
                #text_right(s.ui_image,173,s.right_key[1],settings.label_color,settings.label_font,206)
                s.canvas.blit(s.ui_image.transpose(ROTATE_90))
            elif s.landscape==2:
                s.ui_image.blit(s.canvas_image)
                s.draw_softkeys(s.ui_image)
                #s.ui_image.text((3,173),s.left_key[1],fill=settings.label_color,font=settings.label_font)
                #text_right(s.ui_image,173,s.right_key[1],settings.label_color,settings.label_font,206)
                s.canvas.blit(s.ui_image.transpose(ROTATE_270))
            else:
                #s.canvas.begin_redraw((0,0,s.canvas.size[0],s.canvas.size[1]))
                s.canvas.blit(s.canvas_image)
                #s.canvas.end_redraw((0,0,s.canvas.size[0],s.canvas.size[1]))
                s.draw_softkeys(s.canvas)
                #s.canvas.text((3,205),s.left_key[1],fill=settings.label_color,font=settings.label_font)
                #text_right(s.canvas,205,s.right_key[1],settings.label_color,settings.label_font,174)
        except:
            #traceback.print_exc()
            pass
        # if s3:
            # s.canvas.end_redraw()

    def canvas_refresh_v3(s, rect = None):
        # In the newer phones canvas is automatically rotated
        try:
            if not rect:
                # Crash if called during auto redraw callback
                s.canvas.begin_redraw()
            s.canvas.blit(s.canvas_image)
            s.draw_softkeys(s.canvas)
            if not rect:
                s.canvas.end_redraw()
        except:
            #traceback.print_exc()
            pass

    def draw_softkeys(s, img):
        x,y = img.size
        text_render(img, skinUI.softkeys_rect, s.left_key[1], settings.label_color, skinUI.softkey_font, ALIGNMENT_MIDDLE|ALIGNMENT_DOWN, 1, x/2)
        text_render(img, skinUI.softkeys_rect, s.right_key[1], settings.label_color, skinUI.softkey_font, ALIGNMENT_MIDDLE|ALIGNMENT_RIGHT, 1, x/2)

    def shutdown_effect(s,step=-10,fr=0,to=100):
        try:
            ui_image = Image.new(s.display_size)
            if s.landscape==1:
                ui_image.blit(s.canvas_image.transpose(ROTATE_90))
            elif s.landscape==2:
                ui_image.blit(s.canvas_image.transpose(ROTATE_270))
            else:
                ui_image.blit(s.canvas_image)
            while abs(fr)<=to:
                s.canvas.blit(luminosita(ui_image,fr))
                fr+=step
            del ui_image
        except:
            return

    def openmenu(s):
        #print 'Tasto sinistro premuto'
        if not s.menu.num:
            return
        if s.menuopened == 0:
            s.prevbindarr = s.bindarr
            s.prevtouchbindarr = s.touchbindarr
            s.menuopened = 1
            s.menu.open()
        else:

            e32.ao_yield() #Ho messo questo per evitare l'effetto "doppio click" che si ottiene se si preme il softkey sinistro...

            s.menu.select()

    def bindprevarr(s):
        s.menuopened = 0
        s.bindarr = s.prevbindarr
        s.touchbindarr = s.prevtouchbindarr

    def unbindall(s):
        s.bindarr = []
        s.touchbindarr = []

    def bind(s, key, cb, ktype = appuifw.EEventKey):
        if not (type(key) in [types.TupleType, types.ListType]):
            key = [key]
        for k in key:
            fk = FKey(k, cb, ktype)
            s.bindarr.append(fk)

    def bind_touch(s, type, cb, rect = None):
        #Do some calculations to speed things up
        try:
            x1,y1,x2,y2 = rect[0][0], rect[0][1], rect[1][0], rect[1][1]
        except:
            x1,y1,x2,y2 = rect
        dx = xrange(min(x1,x2),max(x1,x2)+1)
        dy = xrange(min(y1,y2),max(y1,y2)+1)
        ft = FKey(type, cb, (rect,dx,dy))
        s.touchbindarr.append(ft)

    def unbind(s, key, type = appuifw.EEventKey):
        for fk in s.bindarr:
            if (fk.key == key) and (fk.option == type):
                s.bindarr.remove(fk)

    def unbind_touch(s, type, rect):
        for t in s.touchbindarr:
            if (t.key == type) and (rect == t.option[0]):
                s.touchbindarr.remove(t)

    def getfk(s, key, type):
        for fk in s.bindarr:
            if (fk.key == key) and (fk.option == type):
                return fk
        return None

    def cb_capture(s, key, type):
        fk = s.getfk(key, type)
        if fk != None:
            fk.cb()

    def touch_cb(s, type, pos):
      #  print type, rect
        for t in s.touchbindarr:
#            print t.key, t.option
            if (t.key == type) and ((pos[0] in t.option[1]) and (pos[1] in t.option[2])):
                #print type, pos, t.option
                t.cb(pos)

class FMenu:
    def __init__(self, title, cb = None, submenu = None, shortcut = None):
        self.title = title
        self.submenu = submenu
        self.cb = cb
        self.shortcut = shortcut

class Menu:

    def __init__(self, cb_close = None):
        self.old_label=[]
        self.img = None
        self.num = 0
        self.sm = None
        self.cb_close = cb_close
        self.index = 0
        self.page = 0
        #self.elem_page = 5
        self.menuarr = []

    def menu(self, menu):
        self.menuarr = []
        for mn in menu:
            title = mn[0]
            cb_menu = mn[1]
            if (len(cb_menu) >= 1) and types.TupleType==type(cb_menu[0]):
                #Submenu entry
                sarr = []
                for mn2 in cb_menu:
                    #Shortcut (key) filter, submenus
                    if len(mn2) == 3:
                        scs = mn2[2]
                    else:
                        scs = None
                    fmenu2 = FMenu(mn2[0], mn2[1], None, scs)
                    sarr.append(fmenu2)
                fmenu = FMenu(title, None, sarr)
            else:
                #Normal entry
                #Shortcut (key) filter, menus
                if len(mn) == 3:
                    sc = mn[2]
                else:
                    sc = None
                fmenu = FMenu(title, cb_menu[0], None, sc)
            self.menuarr.append(fmenu)
        self.num = len(self.menuarr)

    def reopen(self):
        self.sm = None
        self.cbind()
        self.show()

    def open(self):
        self.old_label = [ui.left_key, ui.right_key]
        ui.left_key = [None,_(u"Seleziona")]
        ui.right_key = [None,_(u"Indietro")]
        self.sm = None
        self.index = 0
        self.page = 0

        self.img = Image.new(ui.display_size)
        self.img.blit(ui.canvas_image)

        self.menu_img = Image.new(ui.display_size)
#        self.bg_img = Image.new(ui.display_size)
#        self.bg_img.blit(ui.canvas_image)
        self.bg_img = luminosita(ui.canvas_image, skinUI.mnbg_bright)
        #blur(self.bg_img,200)
        
        # self.element_size = (grafica.mn_i.size[1] + 5)
        # self.element_size2 = grafica.mn_i.size[1]
        # self.text_height = grafica.mn_i.size[1] * .60

        #self.elem_page =  #int(ui.display_size[1] * .60 / self.element_size)
        #mx,my = self.menu_img.size

        if self.num>=skinUI.mn_elem_page:
            self.y = skinUI.softkeys_rect[1] - (skinUI.mn_element_size * skinUI.mn_elem_page) - skinUI.mn_sel_Yspacing
        else:
            self.y = skinUI.softkeys_rect[1] - (skinUI.mn_element_size * self.num) - skinUI.mn_sel_Yspacing
            
        self.yf = skinUI.softkeys_rect[1]
        

        self.cbind()
        self.show()

    def update_background(self,img):
        #self.bg_img.blit(img)
        self.bg_img = luminosita(img, skinUI.mnbg_bright)
        self.show()

    def close(self):
        if (self.img != None):
            ui.left_key, ui.right_key = self.old_label
            self.cunbind()
            ui.draw(self.img)
            self.img = None
            if (self.cb_close != None):
                self.cb_close()

    def up(s):

        if s.index>0:
            s.index -= 1
        elif s.page>0:
            s.page -= 1
        elif s.num>skinUI.mn_elem_page-1:
            s.index = skinUI.mn_elem_page - 1
            s.page = s.num - skinUI.mn_elem_page
        elif s.num>0:
            s.index = s.num - 1
        s.redrawmenu()

    def down(s):

        if s.num>(skinUI.mn_elem_page-1):
            if s.index<(skinUI.mn_elem_page-1):
                s.index += 1
            elif s.index+s.page+1<s.num:
                s.page += 1
            else:
                s.index = 0
                s.page = 0
        elif s.num>0:
            if (s.index + 1)<s.num:
                s.index += 1
            else:
                s.index = 0
                s.page = 0
        s.redrawmenu()

    def right(self):
        mn = self.menuarr[self.index+self.page]
        if (mn.submenu != None):
            self.cunbind()
            self.sm = SubMenu(mn.submenu, self, self.menu_img)
            self.sm.open()

    def select(self, i = None):
        if i:
            try:
                mn = self.menuarr[i + self.page]
            except IndexError:
                return
        else:
            mn = self.menuarr[self.index + self.page]
        if (mn.submenu == None):
            self.close()
            mn.cb()
        else:
            if (self.sm != None):
                self.sm.select()
                return
            self.cunbind()
            self.sm = SubMenu(mn.submenu, self , self.menu_img)
            self.sm.open()

    def cbind(self):
        ui.unbindall()
        ui.menu_exit=self.close
        if ui.landscape == 1:
            ui.bind(EScancodeUpArrow, self.right)
            ui.bind(EScancodeLeftArrow, self.up)
            ui.bind(EScancodeSelect, self.select)
            ui.bind(EScancodeRightArrow, self.down)
        if ui.landscape == 2:
            ui.bind(EScancodeDownArrow, self.right)
            ui.bind(EScancodeLeftArrow, self.down)
            ui.bind(EScancodeSelect, self.select)
            ui.bind(EScancodeRightArrow, self.up)
        else:
            ui.bind(EScancodeUpArrow, self.up)
            ui.bind(EScancodeDownArrow, self.down)
            ui.bind(EScancodeSelect, self.select)
            ui.bind(EScancodeRightArrow, self.right)

        ui.bind(EStdKeyEnter, self.select)
        # Bind every number key for the fast selection!
        ui.bind(EScancode1, lambda: self.select(0))
        ui.bind(EScancode2, lambda: self.select(1))
        ui.bind(EScancode3, lambda: self.select(2))
        ui.bind(EScancode4, lambda: self.select(3))
        ui.bind(EScancode5, lambda: self.select(4))
        ui.bind(EScancode6, lambda: self.select(5))
        ui.bind(EScancode7, lambda: self.select(6))
        ui.bind(EScancode8, lambda: self.select(7))
        ui.bind(EScancode9, lambda: self.select(8))
        #for i in xrange(1, skinUI.mn_elem_page+1):
            #??? Doesn't work ???
            # try:
                # ui.bind(eval("EScancode%i"%i), eval("lambda: self.select(%i)"%i))
            # except:
                # break

    def cunbind(self):
        ui.unbindall()

    def redrawmenu(self):
        mx,my = self.menu_img.size
        sx,sy = grafica.mn_sel.size
        
        mn_rect = (0, self.y, skinUI.mn_x_size, self.yf)
        
        # Background
        self.menu_img.blit(self.bg_img)
        # Menu background, menu rect
        self.menu_img.blit(grafica.bg_img, target = (0,self.y), source = mn_rect)
        # Menu rectangle
        self.menu_img.rectangle(mn_rect, outline = settings.window_border, width = 1)
        # Menu selection rect
        self.menu_img.blit(grafica.mn_sel, target = (4,((self.y + 5) + (self.index * skinUI.mn_element_size))), mask = grafica.mn_sel_mask)

        i = 0
        for mn in self.menuarr[self.page:self.page + skinUI.mn_elem_page]:
            #i19 = (i * 19)
            #ty = (self.y + 17) + i19
            #self.menu_img.text((10,ty), mn.title, settings.text_color)#u'Nokia Sans SemiBold S60')u'LatinBold12'
            #self.menu_img.rectangle((4, self.y + 5 + (i * self.element_size), sx + 10, self.y + (i * self.element_size) + sy + 5, ), 0,0)
            
            t_rect = (skinUI.mn_text_x, self.y + skinUI.mn_sel_Yspacing + (i * skinUI.mn_element_size), skinUI.mn_text_x + skinUI.mn_text_x_size , self.y + (i * skinUI.mn_element_size) + sy + skinUI.mn_sel_Yspacing, )
            text_render(self.menu_img, t_rect, mn.title, settings.text_color, (None, skinUI.mn_text_height), ALIGNMENT_MIDDLE, 1)
            if mn.shortcut:
                #text_right(self.menu_img, ty, mn.shortcut, settings.text_color, u'Nokia Sans SemiBold S60', mx-8)
                text_render(self.menu_img, t_rect, mn.shortcut, settings.text_color, (None, skinUI.mn_text_height, FONT_BOLD), ALIGNMENT_MIDDLE|ALIGNMENT_RIGHT)
            if mn.submenu:
                #self.menu_img.polygon([mx-13,((self.y + 7) + i19),mx-13,((self.y + 19) + i19),mx-7,((self.y + 13) + i19)], fill=settings.text_color)
                text_render(self.menu_img, t_rect, u">", settings.text_color, (None, skinUI.mn_text_height*1.15, FONT_BOLD), ALIGNMENT_MIDDLE|ALIGNMENT_RIGHT)
            i += 1
        
        # if self.num > skinUI.mn_elem_page:
            # self.menu_img.rectangle((0,0,20,20), color_mixer((255,255,255), (0,0,0), float(self.index) / self.num))
            # arr1 = []
            # arr2 = []
            # x = mx/2
            # arr1 = ()
            # y1 = skinUI.softkeys_rect[1] + 2
            # y2 = skinUI.softkeys_rect[3] - 2
            # for x in xrange():
                

        if self.sm:
            self.sm.bimg.blit(self.menu_img)
            self.sm.redrawmenu()
        else:
            ui.draw(self.menu_img)

    def show(self):
        self.redrawmenu()

class SubMenu:
    def __init__(self, menu, mn , image):

        self.bimg = Image.new(ui.display_size)
        self.submenu_img = Image.new(ui.display_size)
        self.bimg.blit(luminosita(image, skinUI.submnbg_bright))

        self.mn = mn
        self.index = 0
        self.menuarr = menu
        self.num = len(self.menuarr)
        self.page=0
        self.elem_page=6

    def open(self):
        # self.element_size = (grafica.mn_il.size[1] + 5)
        # self.element_size2 = grafica.mn_il.size[1]
        # self.text_height = grafica.mn_il.size[1] * .60
        # self.lenght = (grafica.mn_il.size[0] + 4)

        #Calculation of the submenu x size
        # for e in self.menuarr:
            # x1 = self.submenu_img.measure_text(e.title, (None, self.text_height))[1]
            # if x1>self.lenght:
                # self.lenght = x1
        # self.lenght += 10
        
        self.elem_page =  int(ui.display_size[1] * .60 / skinUI.submn_element_size)
        mx,my = self.submenu_img.size
        
        #self.x1 = mx - skinUI.submn_x_size
        #self.text_rect = (self.x1 + 4, )

        if self.num>=self.elem_page:
            self.y = skinUI.softkeys_rect[1] - (skinUI.submn_element_size * self.elem_page)
        else:
            self.y = skinUI.softkeys_rect[1] - (skinUI.submn_element_size * self.num)
        self.y -= skinUI.submn_sel_Yspacing
        self.cbind()
        self.show()
    def close(self):
        self.cunbind()
        self.mn.reopen()
    def up(s):
        if s.index>0:
            s.index-=1
        elif s.page>0:
            s.page-=1
        elif s.num>s.elem_page-1:
            s.index,s.page=(s.elem_page-1),s.num-s.elem_page
        elif s.num>0:
            s.index=s.num-1
        s.redrawmenu()
    def down(s):
        if s.num>(s.elem_page-1):
            if s.index<(s.elem_page-1):
                s.index+=1
            elif s.index+s.page+1<s.num:
                s.page+=1
            else:
                s.index,s.page=0,0
        elif s.num>0:
            if s.index+1<s.num:
                s.index+=1
            else:
                s.index,s.page=0,0
        s.redrawmenu()
    def left(self):
        self.close()
    def select(self, i = None):
        if i:
            try:
                mn = self.menuarr[i + self.page]
            except IndexError:
                return
        else:
            mn = self.menuarr[self.index + self.page]
    # def select(self):
        # mn = self.menuarr[self.index+self.page]
        self.mn.close()
        mn.cb()
    def cbind(self):
        ui.menu_exit=self.close
        if ui.landscape==1:
            ui.bind(EScancodeLeftArrow, self.up)
            ui.bind(EScancodeRightArrow, self.down)
            ui.bind(EScancodeDownArrow, self.left)
            ui.bind(EScancodeLeftSoftkey, self.select)
        elif ui.landscape==2:
            ui.bind(EScancodeLeftArrow, self.down)
            ui.bind(EScancodeRightArrow, self.up)
            ui.bind(EScancodeUpArrow, self.left)
            ui.bind(EScancodeLeftSoftkey, self.select)
        else:
            ui.bind(EScancodeUpArrow, self.up)
            ui.bind(EScancodeDownArrow, self.down)
            ui.bind(EScancodeLeftArrow, self.left)
            ui.bind(EScancodeLeftSoftkey, self.select)

        ui.bind(EScancodeSelect, self.select)
        ui.bind(EStdKeyEnter, self.select)
        # Bind every number key for the fast selection!
        ui.bind(EScancode1, lambda: self.select(0))
        ui.bind(EScancode2, lambda: self.select(1))
        ui.bind(EScancode3, lambda: self.select(2))
        ui.bind(EScancode4, lambda: self.select(3))
        ui.bind(EScancode5, lambda: self.select(4))
        ui.bind(EScancode6, lambda: self.select(5))
        ui.bind(EScancode7, lambda: self.select(6))
        ui.bind(EScancode8, lambda: self.select(7))
        ui.bind(EScancode9, lambda: self.select(8))
    def cunbind(self):
        ui.unbindall()
    def redrawmenu(self):
        mx,my = self.submenu_img.size
        sx,sy = grafica.submn_sel.size
        # if self.num>=self.elem_page:
            # y = (my - 22) - (20 * self.elem_page)
        # else:
            # y = (my - 22) - (20 * self.num)
        y1 = skinUI.submn_y + skinUI.submn_y_max_size#my - 16
        end_x = skinUI.submn_x + skinUI.submn_x_size
        #x1 = mx - self.lenght
        self.submenu_img.blit(self.bimg)
        self.submenu_img.blit(grafica.bg_img, target = (skinUI.submn_x,self.y), source = (skinUI.submn_x, self.y, end_x, y1))

        self.submenu_img.rectangle([(skinUI.submn_x,self.y), (end_x,y1)], outline=settings.window_border, width=1)
        self.submenu_img.blit(grafica.submn_sel, target = (skinUI.submn_sel_x, skinUI.submn_sel_Yspacing + self.y + (self.index * skinUI.submn_element_size)), mask = grafica.submn_sel_mask)

        # if self.num>self.elem_page:
            # lbar=float(y1-self.y-7)/(self.num-self.elem_page+1)
            # ybar=(self.page+1)*lbar
            # self.submenu_img.line((mx-6,self.y+3,mx-6,y1-5),settings.scroll_bar_bg_color1)
            # self.submenu_img.rectangle((mx-7,self.y+3+ybar-lbar,mx-4,self.y+3+ybar),outline=settings.scroll_bar_main_color1,fill=settings.scroll_bar_main_color2)

        i = 0
        #t_rect = (self.x1, self.y + 5 + (i * skinUI.submn_element_size), my - 4, self.y + (i * skinUI.submn_element_size) + sy + 5, )
        
        for mn in self.menuarr[self.page:self.page+self.elem_page]:
            t_rect = (skinUI.submn_text_x, skinUI.submn_sel_Yspacing + self.y + (i * skinUI.submn_element_size), skinUI.submn_text_x + skinUI.submn_text_x_size , skinUI.submn_sel_Yspacing + self.y + (i * skinUI.submn_element_size) + sy )
            #self.submenu_img.text((mx-104,(y + 17) + (i * 19)), mn.title, settings.text_color)
            #self.submenu_img.rectangle(t_rect, 0, None)
            t = 0
            if (mn.shortcut != None):
                #text_right(self.submenu_img, (y + 17) + (i * 19) , mn.shortcut, settings.text_color, u'Nokia Sans SemiBold S60', mx-10)
                t = text_render(self.submenu_img, t_rect, mn.shortcut, settings.text_color, (None, skinUI.submn_text_height), ALIGNMENT_MIDDLE|ALIGNMENT_RIGHT, 0, skinUI.submn_text_x)[2]
            i += 1
            text_render(self.submenu_img, t_rect, mn.title, settings.text_color, (None, skinUI.submn_text_height), ALIGNMENT_MIDDLE, 1, skinUI.submn_text_x - t)
        ui.draw(self.submenu_img)

    def show(self):
        self.redrawmenu()

class LType:
    def __init__(s, name = u'', undername = None, title = u'', icon = None, hid = 0):#, cb = None)#, type = 3, hid = 0, icon = [], cb = None):
        s.name = name
        s.undername = undername
        s.title = title
        s.icon = icon # [(icon, mask), ...]
        s.hidden = hid
#        s.cb = cb
#        s.type = type


class GrafList:
#Listbox controller
#TODO: support selection callback and element callback during scroll (every element that hasn't been called)
    def __init__(s):#,sel_cb=None,left_cb=None,right_cb=None):
        s.no_data = _(u"Nessun elemento")
        s.position = 0
        s.page = 0
        s.sel_cb = None
        s.left_cb = None
        s.right_cb = None
        s.selecting_cb = None
        s.elements = []
        s.selected = []
        s.mode_cb = None
        s.scroll_bar = ScrollBar(s.select_item)
        s.init2()
        s.cbind()

    def init2(s):
        s.ys = skinUI.title_rect[3]
        s.elementX_size, s.elementY_size = grafica.csel_img.size #TODO: add this in skinUI
        s.elem_page = int( (skinUI.main_drawable_rect[3] - skinUI.main_drawable_rect[1]) / float(s.elementY_size))
        s.spacing = int( ( (skinUI.main_drawable_rect[3] - skinUI.main_drawable_rect[1]) % s.elementY_size) / s.elem_page )
#        s.elem_rect = (0, 0, )
        #s.elem_page = int(ui.display_size[1] / s.element_size)

        s.list_image = Image.new(ui.display_size)
        s.touch_cntrl = KineticDriver(skinUI.main_drawable_rect, (s.touch_select, None, None), 0, 0.98)
        s.scroll_bar.position = skinUI.scrollbar_rect
        #s.scroll_bar.orientation = ORIENTATION_VERTICAL
        s.scroll_bar.max_page = s.elem_page
        s.scroll_bar.init_values()

    def touch_select(s, dire, x, y):

        if dire & MOVE_UP:
            s.up()
        if dire & MOVE_DOWN:
            s.down()

    def screen_change(s):
       # s.elem_page=int(ui.display_size[1]/s.element_size)
        # s.list_image=Image.new(ui.display_size)
        # s.scroll_bar.position = (ui.display_size[0]-20,20,ui.display_size[1]-41,15)
        # s.scroll_bar.max_page = s.elem_page
        # s.scroll_bar.init_values()
        #s.x,s.y=s.list_image.size
        #if (ui.landscape!=s.old_mode): s.position,s.index,s.page=0,0,0
        #s.old_mode=ui.landscape
        s.init2()
        i=s.current()
        s.position = 0
        s.page = 0
        s.select_item(i)
        s.cbind()
        if s.mode_cb!=None:
            s.mode_cb()
        s.redrawlist()

    def bind(s,**args):
        ui.bind(args)

    def current(s):
        return s.position + s.page

    def select_item(s, i, r = 1):
        # Give the possibility to pass None as argument, useful in some situations
        if i==None:
            i = 0
        s.position = 0
        s.page = 0
        ln = len(s.elements)
        if not ln:
            if r:
                s.redrawlist()
            return
        if type(i) in [types.StringType,types.UnicodeType]: #Se è una stringa, bisogna andare a selezionare l'elemento con tale nome
            try:
                while ln>s.position:
                        if s.elements[s.position].name == i:
                            break
                        else:
                            s.position += 1
                            if s.position >= (ln-1):
                                break
            except:
                s.position=0
        else:
            if (not i>(ln-1)):
                s.position = i
            else:
                s.position = 0
        if s.position>(s.elem_page-1):
            s.page = s.position-(s.elem_page-1)
            s.position = s.elem_page-1
        if r:
            s.redrawlist()

    def select_element(s):
        punto = s.current()
        if punto in s.selected:
            s.selected.remove(punto)
        else:
            s.selected.append(punto)
        s.redrawlist()

    def select_all(s):
        s.selected = range(0,len(s.elements))
        s.redrawlist()

    def select_none(s):
        s.selected = []
        s.redrawlist()

    def select_invert(s):
        for i in xrange(len(s.elements)):
            if i in s.selected:
                s.selected.remove(i)
            else:
                s.selected.append(i)
        s.redrawlist()

    def set_list(s, lista, i = 0):
        s.elements = []
        s.selected = []
        for i in lista:
            try:
                s.elements.append(LType(i[0],i[1],i[2],i[3],i[4]))#,i[5]))
            except:
                break
        s.select_item(i)
        # if i:
            # s.select_item(i,0)
        # else:
            # s.position,s.page=0,0,0
        # s.redrawlist()

    def page_up(s):
        if s.page == 0:
            s.position = 0
        else:
            if len(s.elements)>s.elem_page:
                s.page -= s.elem_page
                s.position = 0
            if s.page<0:
                s.page = 0
        s.redrawlist()
        s.selection_cb()

    def page_down(s):
        l = len(s.elements)
        if l <= s.elem_page:
            return
        l4 = l-s.elem_page
        s.page += s.elem_page
        s.position = s.elem_page-1
        if s.page>l4:
            s.page = l4
            s.position = s.elem_page-1
        s.redrawlist()
        s.selection_cb()

    def up(s):
        l = len(s.elements)
        if s.position>0:
            s.position -= 1
        elif s.page>0:
            s.page -= 1
        elif l>s.elem_page-1:
            s.position = (s.elem_page-1)
            s.page = l-s.elem_page
        elif l>0:
            s.position = l-1
        s.redrawlist()
        s.selection_cb()

    def down(s):
        l=len(s.elements)
        if l>(s.elem_page-1):
            if s.position<(s.elem_page-1):
                s.position+=1
            elif s.position+s.page+1<l:
                s.page+=1
            else:
                s.position = 0
                s.page = 0
        elif l>0:
            if (s.position+1) < l:
                s.position += 1
            else:
                s.position = 0
                s.page = 0
        s.redrawlist()
        s.selection_cb()
    
    def selection_cb(s):
        if s.selecting_cb:
            s.selecting_cb(s.current())

    def right_cb_cb(s):
        if s.right_cb!=None:
            s.right_cb()
#            s.selected = []

    def left_cb_cb(s):
        if s.left_cb!=None:
            s.left_cb()
#            s.selected = []

    def select_cb_cb(s):
        if s.sel_cb!=None:
            s.sel_cb()

    def reset(s):
        s.no_data = _(u"Nessun elemento")
        s.position = 0
        s.page = 0
        s.elements = []
        s.selected = []
        s.mode_cb = None
        s.sel_cb = None
        s.right_cb = None
        s.left_cb = None
        s.selecting_cb = None
        s.cbind()

    def save(s):
        return s.no_data,s.position,s.page,s.sel_cb,s.left_cb,s.right_cb,s.elements,s.selected,s.mode_cb,s.selecting_cb

    def load(s,sett):
        s.no_data,s.position,s.page,s.sel_cb,s.left_cb,s.right_cb,s.elements,s.selected,s.mode_cb,s.selecting_cb=sett

    def cbind(s):
        ui.unbindall()
        s.touch_cntrl.start()
        #Touch screen for the scroll bar
        s.scroll_bar.set_touch()
        ui.mode_callback=s.screen_change
        if ui.landscape==1:
            ui.bind(EScancodeUpArrow, s.right_cb_cb)
            ui.bind(EScancodeDownArrow, s.left_cb_cb)
            ui.bind(EScancodeRightArrow, s.down)
            ui.bind(EScancodeLeftArrow, s.up)
            ui.bind(EScancode0, s.page_up)
            ui.bind(EScancodeHash, s.page_down)
            ui.bind(EScancode9, s.select_element)
        if ui.landscape==2:
            ui.bind(EScancodeDownArrow, s.right_cb_cb)
            ui.bind(EScancodeUpArrow, s.left_cb_cb)
            ui.bind(EScancodeLeftArrow, s.down)
            ui.bind(EScancodeRightArrow, s.up)
            ui.bind(EScancode0, s.page_up)
            ui.bind(EScancodeStar, s.page_down)
            ui.bind(EScancode7, s.select_element)
        else:
            ui.bind(EScancodeUpArrow, s.up)
            ui.bind(EScancodeDownArrow, s.down)
            ui.bind(EScancodeRightArrow, s.right_cb_cb)
            ui.bind(EScancodeLeftArrow, s.left_cb_cb)
            ui.bind(EScancode9, s.page_up)
            ui.bind(EScancodeHash, s.page_down)
            ui.bind(EScancode0, s.select_element)
        #Common keys
        ui.bind((EScancodeSelect, EStdKeyEnter,), s.select_cb_cb)
    #def img_from_res(s,res,img):
# if preview_switch==1:
     #   try:
     #       tmp=Image.open(res)
      #      ix,iy=tmp.size
      #      dx,dy=img.size
#            n=os.path.normpath(s.dir+"\\_PAlbTN\\40x30\\"+txt+".40x30")
            #ix = 40.0#dimensione x foto
            #iy = 30.0#dimensione y foto
            #dx=34
            #y=13+i12
            #dy=63+i12+i12#(13+i12)+i12+50
            ###
      #      if ix>dx or iy>dy:
      #          if (dx/(ix/iy))<=dy: img.blit(tmp,target=(0,(dy-(int(dx/(ix/iy))))/2,dx,dy-((dy-(int(dx/(ix/iy))))/2)),scale=1)
      #          else : img.blit(tmp,target=((dx-(int(dy/(iy/ix))))/2,0,dx-((dx-(int(dy/(iy/ix))))/2),dy),scale=1)
      #      else : img.blit(tmp,target=((dx-ix)/2,(dy-iy)/2))
      #  except Exception,e:
       #     print str(e)
       # return img
        ###
    # else:
        # img.blit(immagine_img,mask=immagine_img_mask,target=(2,15+i12))
# elif ext_uni in videoextensions:
    # if preview_switch==1:
        # try:
            # n=os.path.normpath(s.dir+"\\_PAlbTN\\40x30\\"+txt+".40x30")
            # ix = 40.0
            # iy = 30.0
            # dx=34
            # y=13+i12
            # dy=63+i12+i12
            # if ix>dx or iy>dy:
                # if (dx/(ix/iy))<=dy: img.blit(Image.open(n),target=(3,(dy-(int(dx/(ix/iy))))/2,dx,dy-((dy-(int(dx/(ix/iy))))/2)),scale=1)
                # else : img.blit(Image.open(n),target=((dx-(int(dy/(iy/ix))))/2,y,dx-((dx-(int(dy/(iy/ix))))/2),dy),scale=1)
            # else : img.blit(Image.open(n),target=((dx-ix)/2,(dy-iy)/2))
        # except:
            # img.blit(video_img,mask=video_img_mask,target=(2,15+i12))
    # else:
        # img.blit(video_img,mask=video_img_mask,target=(2,15+i12))
    def redrawlist(s):
        lx,ly = s.list_image.size
        elen = len(s.elements)
        s.list_image.blit(grafica.bg_img)
        if not s.elements:
            #No elements, display a message
            lines = wrap_text_to_array(s.no_data, 'dense', lx)
            lines_render(s.list_image, skinUI.main_drawable_rect, lines, 1, settings.text_color, None, ALIGNMENT_MIDDLE|ALIGNMENT_CENTER)
            #yi = int(ly/2-len(lines)*6)
            #i = 0
            #for line in lines:
            #    text_center(s.list_image, yi+(12*i), line, settings.text_color, 'dense')
            #    i += 1
        else:
            selected_element = s.elements[s.position+s.page]
            #text_cut(s.list_image, (3,11) , selected_element.title, settings.path_color)
            text_render(s.list_image, skinUI.title_rect, selected_element.title, settings.path_color, None, ALIGNMENT_MIDDLE, 1)
            s.list_image.blit(grafica.csel_img, target = (0,((s.elementY_size + s.spacing)*s.position) + s.ys), mask = grafica.csel_img_mask)
            i = 0
            for ele in s.elements[s.page:s.page+s.elem_page]:
                try:
                        i12 = ((s.elementY_size + s.spacing) * i)  + s.ys
                        if ele.icon:
                            ei = ele.icon
                            ix, iy = ei[0].size
                            elem_rect = (ix + 3, i12, s.elementX_size,s.elementY_size + i12,)
                            if ele.hidden:
                                if len(ei)>1:
                                    s.list_image.blit(luminosita(ei[0], -30), target = (2, i12), mask = ei[1])
                                else:
                                    s.list_image.blit(luminosita(ei[0], -70), target = (2, i12))
                            else:
                                if len(ei)>1:
                                    s.list_image.blit(ei[0], target = (2, i12), mask = ei[1])
                                else:
                                    s.list_image.blit(ei[0], target = (2, i12))
                            if ele.undername:
                                #s.list_image.text((ix + 3, 28+i12), ele.name, settings.text_color, settings.mainfont)
                                #s.list_image.text((ix + 3, 43+i12), ele.undername, settings.text_color)
                                
                                #text_render(s.list_image, elem_rect, ele.name, settings.text_color, settings.mainfont, ALIGNMENT_UP, 1)
                                #text_render(s.list_image, elem_rect, ele.undername, settings.text_color, settings.mainfont, ALIGNMENT_DOWN, 1)
                                lines_render(s.list_image, elem_rect, (ele.name, ele.undername,), 2, settings.text_color, settings.mainfont, ALIGNMENT_MIDDLE|ALIGNMENT_CENTER, 1)
                            else:
                                #s.list_image.text((ix + 3, i12 + (i12/2)), ele.name, settings.text_color, settings.mainfont)
                                text_render(s.list_image, elem_rect, ele.name, settings.text_color, settings.mainfont, ALIGNMENT_MIDDLE, 1)
                        else:
                            elem_rect = (6, i12, s.elementX_size, s.elementY_size + i12,)
                            if ele.undername:
                                #s.list_image.text((5, 28 + i12), ele.name, settings.text_color, settings.mainfont) #TODO: 5 = int(3%ScreenX)
                                #s.list_image.text((5, 43 + i12), ele.undername, settings.text_color)
                                
                                #text_render(s.list_image, elem_rect, ele.name, settings.text_color, settings.mainfont, ALIGNMENT_UP, 1)
                                #text_render(s.list_image, elem_rect, ele.undername, settings.text_color, settings.mainfont, ALIGNMENT_DOWN, 1)
                                lines_render(s.list_image, elem_rect, (ele.name, ele.undername,), 2, settings.text_color, settings.mainfont, ALIGNMENT_MIDDLE|ALIGNMENT_CENTER, 1)
                            else:
                                #s.list_image.text((5, 36 + i12), ele.name, settings.text_color, settings.mainfont)
                                text_render(s.list_image, elem_rect, ele.name, settings.text_color, settings.mainfont, ALIGNMENT_MIDDLE, 1)
                        if (i+s.page) in s.selected:
                            s.list_image.blit(grafica.spuntoimg, target = (0,i12), mask=grafica.spunto_mask)
                except:
                    traceback.print_exc()
                i += 1
            #s.list_image.polygon((170,14,175,14,175,193,170,193),settings.scroll_bar_bg_color1,settings.scroll_bar_bg_color2) #Sfondo barra di scorrimento
            #s.list_image.rectangle((lx,15,lx-6,ly-15),settings.scroll_bar_bg_color1,settings.scroll_bar_bg_color2)
            if elen>s.elem_page:
                #Scrollbar
                # xa,xb=lx-5,lx-1
                # ratio = (ly-28)/elen
                # q=15 + int(ratio*s.page)
                # qp=q + int(ratio*s.elem_page)
                # s.list_image.rectangle((xa,q,xb,qp),settings.scroll_bar_main_color1,settings.scroll_bar_main_color2)
                s.scroll_bar.max_value = elen# - s.elem_page
                s.scroll_bar.current = s.page# - s.elem_page

                s.scroll_bar.draw(s.list_image)

                #s.list_image.polygon((xa,q,xb,q,xb,qp,xa,qp),settings.scroll_bar_main_color1,settings.scroll_bar_main_color2)
        #Draw on screen
        ui.draw(s.list_image)

# class Preview:
    # import thread
    # class img_thread:
        # def __init__(s):
            # lockT = thread.allocate_lock()
            
    # def __init__(s, n, def_ico):
        # s.icons = [def_ico]*n
        # s.n = n
    # def __call__(s):
        # pass

class Explorer:
    # '''
    # Gestisce i percorsi, i file e le directory oltre che ad altri servizi base (Task, Processi, File Ricevuti, ricerca)
    # Le stringhe dei percorsi e dei nomi sono stringhe utf8 (non decodificate a unicode)
    # '''
    def __init__(s):
        s.content_of_dir = [] #Contiene i percorsi COMPLETI del contenuto di una cartella,nome,grandezza,tipo
        s.root_list = [("","",3,0)] #Impostiamo all'interno un valore predefinito
        s.dir = 'root://'
        s.root_tools = [(_(u"File Ricevuti"), None, 3, 0, 0),
                        (_(u"Processi"), None, 3, 0, 0),
                        (_(u"Tasks"), None, 3, 0, 0)]
        s.tools_list = [x[0] for x in s.root_tools]
        s.last_oslistdir = []
        s.is_playing = None
        #s.now_playing = ur(_(u"In riproduzione"))

    def first_boot(s):
        try:
            d = settings.load_session()
            if d[0]:
                s.dir = d[0]#os.path.split(d)[0]+'\\'
                s.scan()
                s.set_list(d[1])
                s.set_inputs_type()
            else:
                s.goto_root()
        except:
            s.goto_root()
        s.set_inputs_type()

    def img_prev(s, path, def_ico):
        #TODO: implement image preview
        try:
            im = Image.open(path)
            im.resize((60,60), keepaspect = 1)
            return im
        except:
            pass
        return def_ico

    def sel_cb(s, index):
        fn = s.content_of_dir[index]
        e = ext_util.split_ext(fn)
        # if e in ext_util.imgextensions:
            # i = Image.open(to_unicode(fn))
            # ix,iy=tmp.size
            # dx,dy=i.size
            # n=os.path.normpath(s.dir+"\\_PAlbTN\\40x30\\"+txt+".40x30")
            # ix = 40.0#dimensione x foto
            # iy = 30.0#dimensione y foto
            # dx=34

            # if ix>dx or iy>dy:
                # if (dx/(ix/iy))<=dy:
                    # ui.canvas_image.blit(tmp,target=(0,(dy-(int(dx/(ix/iy))))/2,dx,dy-((dy-(int(dx/(ix/iy))))/2)),scale=1)
                # else:
                    # ui.canvas_image.blit(tmp,target=((dx-(int(dy/(iy/ix))))/2,0,dx-((dx-(int(dy/(iy/ix))))/2),dy),scale=1)
            # else:
                # ui.canvas_image.blit(tmp,target=((dx-ix)/2,(dy-iy)/2))

    def set_list(s, position = 0):
            #(name=i[0],undername=i[1],title=i[2],type=i[3],hid=i[4],icon=i[5],selected[6]
            ListBox.elements = []
            ListBox.selected = []
            #ListBox.selecting_cb = s.sel_cb
            d = to_unicode(s.dir)
            ListBox.no_data=_(u"La cartella %s non contiene elementi")%d
            rsd = _(u"Risorse del telefono")
            #except: ListBox.no_data=u"La cartella non contiene elementi"
            #ti=time.clock()
            # Adding these methods gives more speed
            elements_i = ListBox.elements.append
            sz_sett = settings.get_size_on_canvas
            format_sz = dataformatter.sizetostr
            icon_finder = ext_util.search_path
            dir_ico = [grafica.cartella_img,grafica.cartella_mask]

            u = None
            
            for elem in s.content_of_dir:

                path, name, type, size, mtime = elem
                try:
                    if type == 0:
                        # Folder
                        elements_i(LType(ru(name), None, d, dir_ico))
                    elif type == 1:
                        # File
                        if sz_sett:
                            u = format_sz(size)
                        name = ru(name)
                        dsc, ic = icon_finder(name)
                        # if dsc == 'image':
                            # elements_i(LType(name,u,d,icon=ic,cb=s.img_prev))
                        # else:
                        elements_i(LType(name, u, d, ic))
                    #elif type==0:
                        #if fileutils.is_hidden(path)or fileutils.is_system(path):
                        #    ListBox.elements.append(LType(name=ru(name),undername=None,title=d,type=0,hid=1,icon=[grafica.cartella_img,grafica.cartella_mask]))
                        #else:
                        #elements_i(LType(ru(name), None, d, icon=dir_ico))
                        #ListBox.elements.append(LType(name=ru(name),undername=None,title=d,type=0,hid=0,icon=[grafica.cartella_img,grafica.cartella_mask]))
                    elif type == 3:
                        # Root
                        try:
                            if sz_sett:
                                u=u"%s / %s"%(format_sz(size[0]), format_sz(size[1]))
                        except:
                            u = None
                        if path == "<PLAYER>":
                            # Player widget
                            if s.is_playing.tags:
                                # If there are some tags, use them
                                elements_i(LType(s.is_playing.title, s.is_playing.artist, rsd, [grafica.musica_img,grafica.musica_img_mask]))
                            else:
                                # otherwise only the filename!
                                elements_i(LType(_(u"In riproduzione"), to_unicode(name), rsd, [grafica.musica_img,grafica.musica_img_mask]))
                        elif name == "<DRIVE>":
                            # Drive
                            try:
                                elements_i(LType(ru(path), u, rsd, ext_util.drive_icon[mtime]))
                            except:
                                #traceback.print_exc()
                                elements_i(LType(ru(path), u, rsd, [grafica.tel_img,grafica.tel_img_mask]))
                        # elif path == "C:":
                            # elements_i(LType(ru(path),u,rsd,icon=[grafica.tel_img,grafica.tel_img_mask]))
                        # elif path == "D:":
                            # elements_i(LType(ru(path),u,rsd,icon=[grafica.ram_img,grafica.ram_img_mask]))
                        # elif path == "E:":
                            # try:
                                # elements_i(LType(u"%s %s"%(ru(path),DriveInfo.drive_names()[u"E:"]),u,rsd,icon=[grafica.mmc_img,grafica.mmc_img_mask]))
                            # except:
                                # elements_i(LType(ru(path),u,rsd,icon=[grafica.mmc_img,grafica.mmc_img_mask]))
                        # elif path == "Z:":
                            # elements_i(LType(ru(path),u,rsd,icon=[grafica.rom_img,grafica.rom_img_mask]))
                            
                        # elif path in drives:
                            # elements_i(LType(ru(path),u,title=u"Risorse del telefono",icon=[grafica.tel_img,grafica.tel_img_mask]))
                        else:
                            # Root tools
                            elements_i(LType(path, name, rsd))
                    else:
                        # Generic element
                        elements_i(LType(to_unicode(path), to_unicode(name), d))
                except:
                    elements_i(LType(_(u"Errore visualizzazione"), title=_(u"Errore elemento")))
                    traceback.print_exc()
                    #.25 / .26 E:\ (.17 / .15
                    # 1.12-1.15 E:\images
            #print str(time.clock()-ti)
            ListBox.select_item(position)

    # def _scan(s):
        # path=(os.path.join(s.dir,file))
        # if os.path.isdir(path): d.append((path,file,0,0))
        # else: f.append((path,file,1,os.path.getsize(path)))
        # return 
    # def _scan2(s,file,d,f):
        # path=os.path.join(s.dir,file)
        # if os.path.isdir(path):
            # d.append((path,file,0,0))
        # else:
            # f.append((path,file,1,os.path.getsize(path)))
    def alfabetico(s, lista):
        _lista_lower=map(lambda x: x.lower(),lista)
        _lista_lower_orig=_lista_lower[:]
        _lista_lower.sort()
        return map(lambda i: lista[i],map(_lista_lower_orig.index,_lista_lower))
    # """

# Idee:
# - la funzione elabora il risultato di scan()-> > gestione array elementi in input -> > spreco di risorse e lentezza
# - ragruppare tutte le proprietà del file (grandezza e data in particolare) tramite os.stat, evitando la sua doppia chimata in getsize e get_mtime
   # creare quindi un nuovo scan() completo di ordine definito
    # si arriva cosi a una funzione che risulterà più veloce tramite l'ordine per nome o nome rispetto alle altre ??   
# - la migliore cosa è di impostare direttamente gli elementi elaborati in content_of_dir cosi anche in vari visualizzatori si mantiene lo stesso ordine
# - futuro: ordine basato anche su altri attributi
# - portare tutto in c++ sarebbe il massimo: ricavare direttamente la content of dir pronta con già tutto ordinato!!!!

# os.stat(file) 
# array -> [8] data, [6] grandezza
# def isdir(path):
    # try:
        # st = os.stat(path)
    # except os.error:
        # return 0
    # return stat.S_ISDIR(st[stat.ST_MODE])

# def isfile(path):
    # try:
        # st = os.stat(path)
    # except os.error:
        # return 0
    # return stat.S_ISREG(st[stat.ST_MODE])

    def sort(s, dirs, files, by = None):
        temp = []
        temp2 = []
        if by == settings.SORT_BY_NAME:
            return dirs, files
        elif by == settings.SORT_BY_SIZE:
            # And here some games to sort our file list! Highly optimized instructions
            # I've tested that this method is faster than the sort(callable with cmp) but a little slower than the sort with a normal list
            # for i in xrange(0, len(files)):
                # temp.append((files[i][3], i))
            # the same, but faster :)
            temp = map(lambda i: (files[i][3], i), xrange(0, len(files)))
            temp.sort()
            return dirs, map(lambda x: files[x[1]], temp)
        elif sett == settings.SORT_BY_DATE:
            temp = map(lambda i: (files[i][4], i), xrange(0, len(files)))
            temp.sort()
            temp2 = map(lambda i: (files[i][4], i), xrange(0, len(files)))
            temp2.sort()
            return map(lambda x: dirs[x[1]], temp), map(lambda x: files[x[1]], temp2)
        
# No valid setting? No problem! Return no sorted lists and warn
        print "warn: invalid sorting settings!"
        return dirs, files

    def content_changed(s, state = 0):
        
        if state:
            print "is something changed?"
        else:
            print "explore is going sleeping..."

    def scan(s, list = None):
        stat = os.path.stat
        f,d,stats = [],[],[]
        s.content_of_dir = []

        if list:
            s.last_oslistdir = list
            dr = ''
        else:
            s.last_oslistdir = os.listdir(s.dir)
            dr = s.dir

        for file in s.last_oslistdir:

            path = os.path.join(dr, file)#"%s\\%s"%(s.dir,file)
            try:
                stats = os.stat(path)
                if stat.S_ISDIR(stats[0]):
                    #stats[8] -> modification time
                    d.append((path, file, 0, 0, stats[8]))
                else:
                    f.append((path, file, 1, stats[6], stats[8]))
            except:
                f.append((path, file, 1, 0, 0))
        # Sort file, if necessary 
        #ti = time.clock()
        d, f = s.sort(d, f, settings.sort_files_by)
        #tf = time.clock()
        #print tf-ti
        #TODO: these in the sort function?
        if settings.sort_mode == settings.SORT_DESCENDING:
            # Reverse both files and dirs, if set
            f.reverse()
            d.reverse()
            
        # directories order
        if settings.sort_dirs_by == settings.SORT_DIRS_LAST:
            s.content_of_dir = f+d
        else:
            s.content_of_dir = d+f

    def get_file(s,list=0): #ritorna percorso completo
        if list:
            temp=[]
            if ListBox.selected:
                for i in ListBox.selected:
                    temp.append(s.content_of_dir[i][0])
            else:
                temp.append(s.content_of_dir[ListBox.current()][0])
            return temp
        else:
            return s.content_of_dir[ListBox.current()][0]

    def get_root(s, p = 0):
        s.root_list = []
        s.dir = 'root://'
        root = e32.drive_list()
        # try: mmc_name=DriveInfo.drive_names()[u"E:"].encode("utf8")
        # except: mmc_name="Memory Card"
        try:
            if DriveInfo:
                sizes = DriveInfo.free_drivespace()
                totals = DriveInfo.total_drivespace()
                type = DriveInfo.drive_type()
        except:
            pass

        for drive in root:
            try:
                s.root_list.append((ur(drive), "<DRIVE>", 3, (sizes[drive], totals[drive],) , type[drive] ))
            except:
                s.root_list.append((ur(drive), "<DRIVE>", 3, (0,0) , 0))

        s.content_of_dir = s.root_list + s.root_tools

        if s.is_playing:
            s.content_of_dir.append(("<PLAYER>", s.is_playing.filename, 3, 0, 0))

        s.set_list(p)

    def goto_root(s,refresh=1,position=0):
        s.get_root(position)
        s.set_inputs_type()
    def refresh(s, p = None):
        # try:
            # d=ru(s.dir)
        # except:
        d = to_unicode(s.dir)
        if d == s.root_tools[0][0]: #Messaggi
            pass
        elif d == s.root_tools[1][0]: #Processi
            pass
        elif d == s.root_tools[2][0]: #Tasks
            pass
        elif d == u'root://': #root
            s.goto_root(p)
            return
        # elif s.content_of_dir == s.root_list: #Root
            # pass
        else:
            s.scan()
        if p:
            s.set_list(p)
        else:
            s.set_list()
        s.set_inputs_type()
    def view_refresh(s):
        if s.content_of_dir != s.root_list:
            try: s.refresh(ListBox.elements[ListBox.current()].name)
            except: pass
        else:
            s.goto_root()
            s.set_inputs_type()
    def go(s):
        #ti=time.clock()
        fn = s.get_file()
        file = to_unicode(fn)
        if len(s.content_of_dir)>0:
            if s.dir == 'root://':#s.content_of_dir == s.root_list:
                if file == s.root_tools[0][0]: #Messaggi
                    #Mail()
                    s.mail_scanner()
                    s.dir = ur(s.root_tools[0][0])
                    s.set_list()
                    s.set_inputs_type()
                elif file == s.root_tools[1]: #Processi
                    #ProcETask(1)
                    s.refresh_task_proc_list(0)
                    s.dir=ur(s.root_tools[1][0])
                    s.set_list()
                    s.set_inputs_type()
                elif file == s.root_tools[2][0]: #Tasks
                    #ProcETask(0)
                    s.refresh_task_proc_list(1)
                    s.dir=ur(s.root_tools[2][0])
                    s.set_list()
                    s.set_inputs_type()
                elif os.path.isdir(fn):
                    # od = s.dir
                    # d = fn + '\\'
                    # s.dir += d
                    s.dir = fn + '\\'
                    try:
                        s.scan()
                    except:
                        #Path is unavailable or protected
                        pass
                    s.set_list()
                    s.set_inputs_type()
                elif file == "<PLAYER>":
                    s.is_playing.restore()
            elif os.path.isdir(fn):
                if s.dir:# != 'root://':
                    s.dir += os.path.split(fn)[1] + '\\'
                else:
                    s.dir = fn + '\\'
                try:
                    s.scan()
                except:
                    #Path is unavailable or protected
                    pass
                s.set_list()
                s.set_inputs_type()
        #else: pass
        #print "go() in", time.clock()-ti
    def back(s):
        # s.l_punti=[]
        # s.l_file_sel=[]
        # if s.dir==posta:
            # s.goto_root()
        # if s.dir=="Tasks/" or s.dir=="Procs/":
            # s.goto_root()
#        if s.dir == 'root://':

        if s.dir!='root://' and os.path.exists(s.dir) and len(s.dir)>3: #Aggiungiamo anche un controllo in più, oltre che a semplificare tutto
            z = os.path.dirname(s.dir)
            w = (os.path.split(z))[1]
            z = os.path.dirname(z)
            if len(z) > 3:
                s.dir = z + '\\'
            else:
                s.dir = z
            s.scan()
            s.set_list(to_unicode(w))

        else: #Root
            try:
                if s.dir == 'root://':
                    p = ListBox.current()
                else:
                    root = e32.drive_list() + s.tools_list
                    p = root.index(s.dir.strip('\\'))
            except:
                p = 0
            s.goto_root(0, p)

        s.set_inputs_type()

    def cerca(s):
        temp = appuifw.query(_(u"Cerca testo (* per parola incompleta):"), 'text', settings.search_string)
        if temp != None:
            settings.search_string = temp
        else:
            return
        if s.dir == 'root://':#s.content_of_dir == s.root_list:
            d = s.get_file() + '\\'
        else:
            d = s.dir
        s.findFiles(os.path.normpath(d), settings.search_string)

    def findFiles(s, dir, pattern):
        fs,ds = [],[]
        import fnmatch #Purtroppo questa libreria ci mette molto a caricarsi...
        for d, dirs, files in gestione_file.walk(dir):
            #ds.extend([(os.path.join(d,n), n, 0, 0) for n in fnmatch.filter(dirs, pattern)])
            #fs.extend([(os.path.join(d,n), n, 1, os.path.getsize(os.path.join(d,n))) for n in fnmatch.filter(files, pattern)])
            ds.extend([os.path.join(d, n) for n in fnmatch.filter(dirs, pattern)])
            fs.extend([os.path.join(d, n) for n in fnmatch.filter(files, pattern)])
        if fs or ds:
#            s.content_of_dir = ds+fs
            #s.dir=_(u"File trovati: %s"%pattern)
            s.dir = ''
            s.scan(ds + fs)
            s.set_list()
            s.set_inputs_type()
            user.note(_(u"Trovati:\n%i file(s)\n%i cartella(e)")%(len(fs),len(ds)), _(u"Ricerca completa"), -1)
            del ds, fs
        else:
            user.note(_(u"Nessun file trovato!"), _(u"Ricerca completa"), -1)

    def find_java(s):
        fs = []
        user.direct_note(_(u"Scansione applicazioni Java in corso..."), _(u"Java"))
        import fnmatch
        for d, dirs, files in gestione_file.walk("E:\\System\\Midlets\\"):
            fs.extend([(n, d) for n in fnmatch.filter(files, "*.jar")])
        for d, dirs, files in gestione_file.walk("C:\\System\\Midlets\\"):
            fs.extend([(n, d) for n in fnmatch.filter(files, "*.jar")])
        if fs:
            #s.content_of_dir=[]
            #d,f=[],[]
            #for file,dir in fs:
            #    path=os.path.join(dir,file)
                #if os.path.isdir(path): d.append((path,file,0,0))
            #    s.content_of_dir.append((path, file, 1, os.path.getsize(path), os.path.getmtime(path)))
            #s.content_of_dir+=
            s.dir = _("Applicazioni Java")
            s.scan(fs)
            s.set_list()
            s.set_inputs_type()
            user.note(_(u"Trovate %i applicazioni Java")%len(s.content_of_dir), _(u"Ricerca completa"), -1)
           # del d,f
        else:
            user.note(_(u"Nessuna applicazione Java installata!"), _(u"Ricerca completa"), -1)
            return

    def mail_scanner(s):
    # '''Scanner dei files ricevuti tramite bt, mms , email oppure ir'''
    # '''Si basa sulle estensioni: senza,solitamente, sono i file indici del sistema di mail Symbian'''
    # '''Se si ricevono quindi files senza estensione (piuttosto improbabile) , non vengono trovati'''
        s.content_of_dir = []
        for path in ["C:\\System\\Mail","E:\\System\\Mail"]:
            try:
                user.direct_note(_(u"Scansione file ricevuti in: %s")%path[0:3],_(u"Scansione file ricevuti"))
                s.walktree(path)
            except:
                pass

    def walktree(s, dir):
        for f in os.listdir(dir):
            try :
                pathname = '%s\\%s' % (dir, f)
                if os.path.isdir(pathname):
                    s.walktree(pathname)
                else:
                    #Se il file ha un'estensione, siamo sicuri al 99% che è un file ricevuto
                    if pathname.rfind('.')!=-1:
                        s.content_of_dir.append((pathname, os.path.split(pathname)[1], 1, os.path.getsize(pathname), os.path.getmtime(pathname)))
            except:
                pass
# class ProcETask:
    # def __init__(s,proc_or_task=0,ft=1):
        # if ft:
            # if proc_or_task: #PROCESSI
                # temp=s.return_procs()
            # else: #TASKS
                # temp=s.return_tasks()
            # explorer.content_of_dir=temp[:]
            # del temp
    def return_procs(s):
        #processes = msys.process()#appswitch.process_list()
        prc = []
        for i in msys.process():
            pr, u_p = i.split(u"[")
            ud, pri = u_p.split(u"]")
            prc.append((ur(pr),str(ud),4,0))
        #del processes
        return prc
    def return_tasks(s):
        t = []
        for task, uid in msys.listtask(settings.show_hidden_tasks):
            t.append((ur(task),ur(uid),4,0))
        return t
    def refresh_task_proc_list(s, task_or_proc = 0, old = None):
        old = s.get_file()
        if task_or_proc==0:
            temp = s.return_procs()
        else:
            temp = s.return_tasks()
        s.content_of_dir = temp
        s.set_list(old)
    def close_kill_task(s, mode=1):
        task = ru(s.get_file())
        #Qui pensavo che il kill fosse quello più potente invece è il kill_app che da il tempo all'applicazione di salvare i suoi dati
        if mode==0:
            if user.query(_(u"Terminare %s ?") %task,_(u"Operazione task")):
               # appswitch.end_app(task)
                msys.closeapp(task)
                e32.ao_sleep(0.5)
                s.refresh_task_proc_list(1,task)
        elif mode==1:
            if user.query(_(u"Chiudere %s ?") %task,_(u"Operazione task")):
                msys.killapp(task)
                #appswitch.kill_app(task)
                e32.ao_sleep(0.5)
                s.refresh_task_proc_list(1,task)
    def term_proc(s):
        proc = ru(s.get_file()+"*")
        if user.query(_(u"Terminare %s ?") %(proc[:-1]),_(u"Operazione processo")):
           appswitch.kill_process(proc)
           e32.ao_sleep(0.5)
           s.refresh_task_proc_list(0)
    def set_inputs_type(s):
        mn = []
        ui.unbindall()
        ListBox.cbind()
        ListBox.left_cb,ListBox.right_cb = s.back,s.go
        ListBox.mode_cb = s.set_inputs_type
        ui.focus_cb = s.content_changed
        ui.bind(EScancodeStar, s.goto_root)
        d = to_unicode(s.dir)
        if d == s.root_tools[0][0]: #Messaggi
            ListBox.sel_cb,ListBox.left_cb,ListBox.right_cb = lambda: start(file=s.get_file()),s.back,s.go
            ui.bind(EScancode5, lambda: info_box(explorer.get_file(),main.restore))
            ui.bind(EScancode1, lambda: gestione_file.copia_inbox(s.get_file(1)))
            ui.bind(EScancode4, lambda: gestione_file.taglia(s.get_file(1)))
            ui.bind(EScancodeYes, gestione_file.invia)
            mn+=main.fileinbox_menu+main.editinbox_menu+main.select_menu+main.send_menu+main.tools2_menu
        elif d == s.root_tools[1][0]: #Processi
            ui.bind(EScancodeBackspace, s.term_proc)
            ui.bind(EScancode5, s.refresh_task_proc_list)
            ui.unbind(EScancode0)
            mn += main.processes_menu+main.tools2_menu
        elif d == s.root_tools[2][0]: #Tasks
            ui.bind(EScancodeBackspace, s.close_kill_task)
            ui.bind(EScancode5, lambda:s.refresh_task_proc_list(1))
            ui.unbind(EScancode0)
            ListBox.sel_cb=lambda: appswitch.switch_to_fg(ru(s.get_file()))
            mn += main.tasks_menu+main.tools2_menu
        elif d == u'root://':#s.content_of_dir == s.root_list: #Root
            ListBox.sel_cb=s.go#,ListBox.left_cb,ListBox.right_cb=s.go,s.back,s.go
            ui.bind(EScancode5, lambda: info_box(s.get_file(),main.restore))
            ui.bind(EScancode2, s.cerca)
            ui.unbind(EScancode0)
            mn += main.tools2_menu
        elif not s.content_of_dir:
            ListBox.sel_cb,ListBox.left_cb,ListBox.right_cb = ui.openmenu,s.back,None
            mn += main.empty_dir
            ui.bind(EScancode7, gestione_file.incolla)
        else:
            ListBox.sel_cb,ListBox.left_cb,ListBox.right_cb=lambda: start(file=s.get_file()),s.back,s.go
            ui.bind(EScancode2, s.cerca)
            #ui.bind(EScancodeStar, s.goto_root)
            ui.bind(EScancode5, lambda: info_box(explorer.get_file(),main.restore))
            ui.bind(EScancodeYes, gestione_file.invia)
            ui.bind(EScancodeBackspace, gestione_file.cancella)
            ui.bind(EScancode8, gestione_file.rinomina)
            #ui.bind(EScancode7,gestione_file.nuovo)
            ui.bind(EScancode7, gestione_file.incolla)
            ui.bind(EScancode6, lambda: gestione_file.attributes(s.get_file(1)))
            ui.bind(EScancode1, lambda: gestione_file.copia(s.get_file(1)))
            ui.bind(EScancode4, lambda: gestione_file.taglia(s.get_file(1)))
            mn+=main.file_menu+main.edit_menu+main.select_menu+main.send_menu+main.tools_menu
            #ui.bind(EScancode7,gestione_file.nuovo)
            # kc.bind(50, s.cerca)
            # kc.bind(53, lambda: info_box(file=explorer.get_state(),background_img=bg_img,appuifw_istance=appuifw,end_callback=restore))
            # mn.menu(menu_drive)
            # appuifw.app.menu=menu_drive
        #mn+=main.tools_menu
        mn += main.settings_menu
        mn += main.base_menu
        ui.menu.menu(mn)

class start: #Esegue un file...
    def __init__(s, mode=0, file=None, cb=None, cwd=None):
        try:
            if not file:
                s.n = os.path.normpath(explorer.get_file())
            else:
                s.n = os.path.normpath(file)
            s.ext_dict=dict(settings.open_with_files)
            s.ext=to_unicode(os.path.splitext(s.n)[1].lower())
        except: pass
        # except Exception,error:
            # appuifw.note(unicode(error),"error")
            # return
        if cb: s.callback=cb
        else: s.callback=main.restore
        s.cwd=cwd
        if mode==0: s.start_file()
        elif mode==1: s.open_internal()
        else: s.open_by_sys()
    def start_file(s):
       # try:
            if os.path.isfile(s.n):
                if s.ext==u'.app':
                    e32.start_exe(u'z:\\system\\programs\\apprun.exe',to_unicode(s.n))
                elif s.ext==u'.exe':
                    cmd=appuifw.query(_(u"Parametri (annulla>niente):"),"text")
                    if not cmd:
                        cmd=""
                    e32.start_exe(to_unicode(s.n),cmd)
                elif s.ext in s.ext_dict:
                    application=s.ext_dict[s.ext]
                    e32.start_exe('z:\\system\\programs\\apprun.exe',application+u' O"%s"'%to_unicode(s.n))
                elif plugins.init_module(ur(s.ext)):
                    #user.note(u"Modulo per gestire il file con estensione %s è stato caricato correttamente!"%s.ext)
                    plugins.start_module(s.n)
                    #return #Al termine dell'utilizzo/caricamento del plugin, la classe start non serve più
                elif s.ext in ext_util.installerextensions:
#                    appuifw.Content_handler().open(ru(s.n))
                    e32.start_exe(u'z:\\system\\programs\\apprun.exe',u'Z:\\System\\Apps\\AppInst\\Appinst.app O"%s"'%to_unicode(s.n))
                elif s.ext in ext_util.imgextensions:
                    mini_viewer(s.n,end_callback=s.callback)
                    #except: appuifw.Content_handler().open_standalone(ru(s.n))
                elif s.ext in ext_util.playlistextensions:
                    mini_player(to_unicode(s.n),s.callback,s.ext)
                elif s.ext in ext_util.audioextensions:
                    mini_player(to_unicode(s.n),s.callback)
                    #except: appuifw.Content_handler().open_standalone(ru(s.n))
                elif s.ext in [u".txt",u".ini",u".m",u".mm",u".log",u".lrc"]:
                    text_viewer(s.n,end_callback=s.callback)
                    #except: appuifw.Content_handler().open_standalone(ru(s.n))
                else:
                    s.open_by_sys()#appuifw.Content_handler().open_standalone(ru(s.n))
            else:
                explorer.go()
        # except Exception,error:
            # appuifw.note(unicode(error),"error")
    def open_internal(s):
      #  try:
            if os.path.isfile(s.n):
                if plugins.init_module(ur(s.ext)):
                    plugins.start_module(s.n)
                elif s.ext in ext_util.imgextensions:
                    mini_viewer(to_unicode(s.n),end_callback=s.callback)
                    #except: appuifw.Content_handler().open_standalone(ru(s.n))
                elif s.ext in ext_util.playlistextensions:
                    mini_player(to_unicode(s.n),s.callback,s.ext)
                elif s.ext in ext_util.audioextensions:
                    mini_player(to_unicode(s.n),s.callback)
                    #except: appuifw.Content_handler().open_standalone(ru(s.n))
                elif s.ext in [u".txt",u".ini",u".m",u".mm",u".log",u".py",u".xml",u".htm",u".html",u".csv",u".lrc"]:
                    text_viewer(s.n,end_callback=s.callback)
                    #except: appuifw.Content_handler().open_standalone(ru(s.n))
                else:
                    user.note(_(u"File non visualizzabile internamente!\nUtilizzare un programma esterno."),_(u"Visualizzatori"),-1)
            else:
                explorer.go()
        # except Exception,error:
            # appuifw.note(unicode(error),"error")
    def open_by_sys(s):
        try:
            appuifw.Content_handler().open_standalone(to_unicode(s.n))
        except TypeError, error:
            user.note(_(u"Tipo file sconosciuto!\nProvare ad utilizzare 'Apri con...'"),_(u"Errore apertura"),-1)
        except Exception, error:
            user.note(unicode(error),_(u"Errore apertura"),-1)

class explorer_plugins:
    #'''Gestione dei plugin per l'apertura di un tipo di file (basato su estensione)'''
    def __init__(s):
        if directory.file_plugins not in sys.path:
            #sys.path.append(directory.file_plugins+"\\")
            #sys.path=[directory.file_plugins+"\\"]+sys.path
            #Massima priorità alla directory dei plugins
            sys.path.insert(0,directory.file_plugins+"\\")
            #print sys.path
        s.plugin,s.active_plugin_name,s.plugin_end_cb=None,None,None #Modulo, nome, funzione da chiamare al termine
        try:
            s.plugin_list=os.listdir(directory.file_plugins)
        except:
            s.plugin_list=[]
        s.global_filename=""
    def init_module(s,ext):
        #print "Ricerca plugin..."
        #print ext,s.plugin_list
        if not ext:
            #s.plugin,s.active_plugin_name=None,None
            return 0
        # if s.plugin:
            # print "Requested clean by init_module"
            # s.clean_module()
        ext=ext.strip(".").lower()
        for plugin_name in s.plugin_list:
            #Supporta plugins con nome: ext1,ext2,exti.py
            supported_exts=plugin_name.lower().split(".")[0].split(",")
            if ext in supported_exts:
                #print "Plugin trovato"
                # if s.plugin:        # Pulizia vecchio plugin ancora caricato...
                    # print "Requested clean by init_module"
                    # s.clean_module()
                s.active_plugin_name=plugin_name
                s.plugin=__import__(os.path.splitext(plugin_name)[0])
                if s.plugin._winfile_version_>__version__:
                    if user.query(_(u"Il plugin necessita di una versione di WinFile maggiore.\nAttuale: %s\nRichiesta: %s\nProvare a caricare comunque?")%(str(__version__),str(s.plugin._winfile_version_))):
                        return 1
                #if s.plugin.
                #print "Plugin caricato"
                else:
                    return 1
        #s.plugin,s.active_plugin_name,s.plugin_end_cb=None,None,None
        return 0
    def start_module(s,filename):
        if s.plugin:
            s.global_filename=filename
            s.plugin.init_plugin(globals(),filename) #Funzione/classe obbligata dei plugin a cui viene passato il namespace del programma (per usare le sue risorse) e il nome del file
            # return 1
        # return 0
    def clean_module(s):
        if s.plugin_end_cb:
            s.plugin_end_cb()
            #print "Plugin Default Exit Callback Called"
        s.plugin,s.active_plugin_name,s.plugin_end_cb=None,None,None
        #print "Plugin succefully cleaned!"
    def stop_module(s,reload_files=0,other_cb=None):#,old_listbox=None):
        # try: s.plugin.stop_callback()
        # except: pass
        #s.plugin
        
        #s.plugin,s.active_plugin_name=None,None #Puliamo i moduli caricati
        #if other_callback: other_callback()
        # if old_listbox:
            # ListBox.load(old_listbox)
        s.clean_module()
        if other_cb:
            other_cb()
            #print "Other_cb called"
        if reload_files:
            explorer.refresh(to_unicode(os.path.split(s.global_filename)[1]))
        else:
            explorer.set_list(to_unicode(os.path.split(s.global_filename)[1]))
            explorer.set_inputs_type()

class FileManager:
#The core of the file management capabilities
    def __init__(s):
        s.file_array = []
        s.bt_abort = 0
        s.move_or_copy = 0 #0 per copia, 1 per sposta
        s.denied_chars = [":","/","\x5C",'"',"*","?",">","<","|"] #A little array containing some characters, wich cannot be used during renaming or creating a new file

    def _dir_scanner(s,path,lista,lista2,sub_dir=1,append_dir=0):
            if os.path.exists(path):
                if append_dir:
                    lista2.append(path)
                names = os.listdir(path)
                for child in names:
                    tpath = os.path.normpath(os.path.join(path,child))
                    if(os.path.isdir(tpath)):
                        if sub_dir:
                            s._dir_scanner(tpath,lista,lista2,sub_dir,append_dir)
                    else:
                        lista.append(tpath)

    def scan_dir(s,path,sub_dir=1,append_dir=0):
        # Scanner dei files e delle directory con varie opzioni di ricerca
        files = []
        dirs = []
        s._dir_scanner(path,files,dirs,sub_dir,append_dir)
        if not append_dir:
            return files
        else:
            return files,dirs

    def walk(s, top, topdown = True, onerror = None):
        # We may not have read permission for top, in which case we can't
        # get a list of the files the directory contains.  os.path.walk
        # always suppressed the exception then, rather than blow up for a
        # minor reason when (say) a thousand readable directories are still
        # left to visit.  That logic is copied here.
        try:
            names = os.listdir(top)
        except os.error, err:
            if onerror is not None:
                onerror(err)
            return
        dirs, nondirs = [], []
        for name in names:
            if os.path.isdir(os.path.join(top, name)):
                dirs.append(name)
            else:
                nondirs.append(name)
        if topdown:
            yield top, dirs, nondirs
        for name in dirs:
            path = os.path.join(top, name)
            #if not os.path.islink(path):
            for x in s.walk(path, topdown, onerror):
                yield x
        if not topdown:
            yield top, dirs, nondirs
            
    def ask_readonly_or_system(s, path):
    
        rd = fileutils.is_readonly
        sy = fileutils.is_system
        if sy or rd:
            user.query(u"Attenzione!\nL'operazione sta per essere eseguita su un file di sola lettura o di sistema.\nProseguire o saltare il file?", u"Attenzione")
#        else:
            #return 0
    def ask_overwrite(s):
    
        user.query(u"Il percorso di destinazione esiste già!\nSovrascrivere?")
    def cancella(s,list = None):
        files_to_delete = []
        dirs_to_delete = []
        user.direct_note(_(u"Scansione elementi da eliminare..."),_(u"Preparazione"))
        #last_selected=ListBox.current()
        if list:
            for file in list:
                if os.path.isfile(file):
                    files_to_delete.append(file)
                else:
                    f,d = s.scan_dir(file,1,1)
                    dirs_to_delete += d
                    files_to_delete += f
        else:
            files = explorer.get_file(1)
            for file in files:
                if os.path.isfile(file):
                    files_to_delete.append(file)
                else:
                    f,d = s.scan_dir(file,1,1)
                    dirs_to_delete += d
                    files_to_delete += f
            # if os.path.isdir(file):
                    # f,d=s.scan_dir(file,1,1)
                    # dirs_to_delete+=d
                    # files_to_delete+=f
            # else: files_to_delete.append(file)
        dirs_to_delete.reverse()
        if not user.query(_(u"Eliminare definitivamente:\n%i file(s) e %i cartella(e)?")%(len(files_to_delete),len(dirs_to_delete)),_(u"Conferma eliminazione"),left=_(u"Elimina")):
            del files_to_delete,dirs_to_delete
            return
        f_i=0
        d_i=0
        delete_also_readonly=0
        errors=[]
        d=progress_dialog(_(u"Eliminazione in corso..."), max = len(files_to_delete) + len(dirs_to_delete))
        for path in files_to_delete:
            e32.ao_yield()
            d.forward()
            d.title = ru(os.path.split(path)[1])
            #d.set_title(ru(os.path.split(path)[1]))
            d.draw()
            try:
                os.remove(path)
                f_i+=1
            except Exception,e:
                #Se c'è un errore potrebbe essere perchè il file è di sola lettura, tolgo quindi l'attributo e riprova la cancellazione
                try:
                    # if fileutils.is_readonly(os.path.normpath(to_unicode(path))):
                        # if user.query(u"Rimuovere il file di sola lettura %s?"%to_unicode(os.path.split(path)[1]),u"File di sola lettura"):
                            # pass
                        # else: raise
                    # else:
                        # raise
                    fileutils.unset_readonly(os.path.normpath(to_unicode(path)))
                    os.remove(path)
                    f_i+=1
                except:
                    errors.append(str(e)) #Se nemmeno questo funziona, allora significa che è in uso o su disco protetto.

        for path in dirs_to_delete:
            e32.ao_yield()
            d.forward()
            d.set_title(ru(os.path.split(path)[1]))
            d.draw()
            try:
                os.rmdir(path)
                d_i+=1
            except Exception,e:
            #errors.append(str(e))
                #Se c'è un errore potrebbe essere perchè il file è di sola lettura, tolgo quindi l'attributo e riprova la cancellazione
                try:
                    # if fileutils.is_readonly(os.path.normpath(to_unicode(path))):
                        # if user.query(u"Rimuovere il file di sola lettura %s?"%to_unicode(os.path.split(path)[1]),u"File di sola lettura"):
                            # pass
                        # else: raise
                    # else:
                        # raise
                    fileutils.unset_readonly(os.path.normpath(to_unicode(path)))
                    os.remove(path)
                    f_i+=1
                except:
                 #   print e
                    errors.append(str(e)) #Se nemmeno questo funziona, allora significa che è in uso o su disco protetto.
        if errors:
            user.note(_(u"Non tutti gli elementi sono stati rimossi.\nCorrettamente rimossi:\n%i file(s) e %i cartella(e)\nErrori: %i")%(f_i,d_i,len(errors)),_(u"Rimozione completata"))
        else:
            user.note(_(u"Elementi rimossi:\n%i file(s) e %i cartella(e)")%(f_i,d_i),_(u"Rimozione completata"))
        d.close()
        del d
       # print errors
        explorer.refresh()
        #user_message(okimg,timeout=2,title="Elementi rimossi",text="Elementi rimossi:\r\n%i file(s) e %i cartella(e)\r\nErrori: %i"%(f_i,d_i,len(errors)),type="normal")
    def removedir(s, path, subdirs=1):  #Rimuove le cartelle e le sottocartelle (compresi i file ovviamente)
            if os.path.exists(path):
                names = os.listdir(path)
                for child in names:
                    tpath = os.path.join(path,child)
                    if os.path.isdir(tpath):
                        if subdirs:
                            s.removedir(tpath)
                    else:
                        os.remove(tpath)
                if subdirs:
                    os.rmdir(path)
    def rinomina(s,source=None):
        ok=0
        fail=0
        if not source:
            source=explorer.get_file() #No unicode
        dire,name=os.path.split(source)
        while not ok:
            new_name = appuifw.query(_(u"Rinomina:"), 'text', to_unicode(name))
            if not new_name:
                return
#            e32.ao_sleep(0.15)
            target = ("%s\\%s")%(dire,ur(new_name))
            for i in s.denied_chars:
                if i in new_name:
                    user.note(_(u"Carattere non valido per nome file: %s\n%s")%(i,"".join(s.denied_chars)),_(u"Rinomina"))
                    fail=1
                    break
                else:
                    fail=0
            if fail==0:
                if os.path.exists(target):
                    user.note(_(u"Nome file esistente!\nSpecificare altro nome."))
                else:
                    ok=1
        try:
            os.rename(source, target)
            explorer.refresh(new_name)
            #e32.ao_sleep(0.2)
            #user.note(u"'%s'\r\nrinominato in\r\n%s"%(ru(name),new_name),u"File rinominato")
        except:
            type, value = sys.exc_info() [:2]
            user.note(_(u"Errore ridenominazione!\n%s")%(str(type)+'\n'+str(value)),_(u"Errore"))

    def nuovo(s,tipo="dir",dir=None):
        if dir==None: dir=explorer.dir
        if tipo=="dir":
            nome=appuifw.query(_(u"Nome cartella:"),"text",_(u"Nuova Cartella"))
            if not nome:
                return
            nome=ur(nome)
            try:
                if os.path.exists(dir+nome):
                    explorer.refresh(ru(nome))
                else:
                    os.mkdir(dir+nome)
                    explorer.refresh(ru(nome))
            except:
                type, value = sys.exc_info() [:2]
                user.note(unicode(str(type)+'\n'+str(value)),_(u"Errore creazione!"))
        elif tipo=="file":
            nome=appuifw.query(_(u"Nome file:"),"text",_(u"Nuovo file.txt"))
            if not nome:
                return
            nome=ur(nome)
            try:
                if os.path.exists(dir+nome):
                    explorer.refresh(ru(nome))
                else:
                    open(dir+nome,"w").close()
                    explorer.refresh(ru(nome))
            except:
                type, value = sys.exc_info() [:2]
                user.note(unicode(str(type)+'\n'+str(value)),_(u"Errore creazione!"))
    
    def copia_inbox(s,list):
        if not list: return
        s.file_array=["SIMPLECOPY",list]
        s.move_or_copy=0
        user.note(_(u"Elementi preparati per la copia."),_(u"Preparazione copia"))

    def copia(s,list=None,current_dir=None):
        s.file_array=[]
        dirs_to_copy,files_to_copy=[],[]
        if current_dir==None: current_dir=explorer.dir #\\ finale
        try:
            user.direct_note(_(u"Scansione elementi da copiare in corso..."),_(u"Preparazione copia"))
            if list:
                for file in list:
                    if os.path.isfile(file):
                        files_to_copy.append(file)
                    else:
                        f,d=s.scan_dir(file,1,1)
                        dirs_to_copy+=d
                        files_to_copy+=f
            else:
                files=explorer.get_file(1)
                for file in files:
                    if os.path.isfile(file):
                        files_to_copy.append(file)
                    else:
                        f,d=s.scan_dir(file,1,1)
                        dirs_to_copy+=d
                        files_to_copy+=f
            s.file_array=[current_dir,dirs_to_copy+files_to_copy]
            #print s.file_array
            del dirs_to_copy,files_to_copy#,temp1,temp2
            s.move_or_copy=0
            user.note(_(u"Elementi preparati per la copia."),_(u"Preparazione copia"),1)
        except:
            user.note(_(u"Errore preparazione copia"),_(u"Preparazione copia"))

    def taglia(s,list=None):
        s.file_array=[]
        try:
            if list:
                s.file_array=list
            else:
                s.file_array=[explorer.get_file()]
            s.move_or_copy=1
            user.note(_(u"Elementi preparati per lo spostamento"),_(u"Preparazione spostamento"),1)
        except:
            user.note(_(u"Errore preparazione spostamento"),_(u"Preparazione spostamento"))

    def copy_file(s, src, dst):
        #Semplice funzione di copia. Ritorna 1 se è stata eseguita correttamente
        try:
            e32.file_copy(os.path.normpath(dst), os.path.normpath(src))
            return 1
        except:# Exception,e:
            return 0

    def incolla(s,current_dir=""):
        if not s.file_array: return
        if not current_dir: current_dir=os.path.normpath(explorer.dir)
        if s.move_or_copy==0:
            fs=0
            errors=0
            l=len(s.file_array[1])
            d=progress_dialog(_(u"Copia elementi in corso...\n "), max = l)
            previous_dir=s.file_array[0]
            for file in s.file_array[1]:
                e32.ao_yield()
                d.update_state(fs+1)
                d.title = ru(os.path.split(file)[1])
                #d.set_title(ru(os.path.split(file)[1]))
                #d.to_draw[-1]=u"(%i di %i)"%(fs+1,l)
                d.update_text(u"(%i di %i)"%(fs+1,l))
                d.draw()
                try:
                    if previous_dir=="SIMPLECOPY": path=os.path.join(current_dir,os.path.basename(file))
                    else: path=os.path.join(current_dir,file[len(previous_dir):])
                    #print path
                    if os.path.isfile(file):
                        if not s.copy_file(to_unicode(file),to_unicode(path)):
                            errors+=1
                    else:
                        os.makedirs(path)
                except:# Exception,e:
                    #print str(e)
                    #errors+=1
                    pass
                fs+=1
            e32.ao_sleep(0.3)
            d.close()
            user.note(_(u"%i elementi copiati, %i non copiati")%(fs-errors,errors),_(u"Copia completata"),-1)
            explorer.refresh(ru(os.path.basename(s.file_array[1][0])))
        else:
            fs=0
            e=0
            l=len(s.file_array)
            d=progress_dialog(_(u"Spostamento elementi in corso...\n "), max=l)
            for path in s.file_array:
                e32.ao_yield()
                try:
                    d.update_state(fs+1)
                    d.title = ru(os.path.split(path)[1])
                    #d.set_title(ru(os.path.split(path)[1]))
                    #d.to_draw[-1] = u"(%i di %i elementi)"%(fs+1,l)
                    d.update_text(u"(%i di %i elementi)"%(fs+1,l))
                    d.draw()
                    target=os.path.join(current_dir,os.path.normpath(os.path.split(path)[1]))
                    os.rename(path,target)
                    fs+=1
                except:
                    e+=1
            d.close()
            user.note(_(u"%i elementi spostati, %i non spostati")%(fs,e),_(u"Spostamento completo"),-1)
            explorer.refresh(ru(os.path.split(path)[1]))
        s.file_array=[]

    def invia(s,list=[]):
        s.bt_abort=0
        import socket
        files_to_send=[]
        user.direct_note(_(u"Preparazione in corso elementi da inviare..."),_(u"Preparazione"))
        if not len(list)>0:
            list=explorer.get_file(1)
        for file in list:
            if os.path.isfile(file):
                files_to_send.append(file)
            else:
                f=s.scan_dir(file,1,0)
                files_to_send+=f
        if not files_to_send:
            user.note(_(u"Nessun file da inviare trovato!\nImpossibile inviare nessun file :)"),_(u"Errore"))
            return
        else:
            def abort():
                s.bt_abort=1
                import btutils
                btutils.off()
                e32.ao_sleep(0.3)
                btutils.on()
            d=progress_dialog(_(u"Invio in corso..."), break_cb=abort, max=len(files_to_send))
            try:
                addr, serv = socket.bt_obex_discover()
                if addr == None or serv == None:
                    raise socket.error,'Invalid address or service'
                target = (addr, serv.values()[0])
            except Exception,detail:
                    user.note(_(u"Impossibile connettersi al dispositivo remoto. Potrebbe essere spento, in modalità nascosta oppure troppo distante.\n%s")%detail,u"Bluetooth",-1)
                    d.close()
                    return
            fs,e=0,0
            for fname in files_to_send:
                e32.ao_yield()
                fname=to_unicode(fname)
                try:
                    d.update_state(fs+1)
                    d.title = os.path.split(fname)[1]
                    #d.set_title(os.path.split(fname)[1])
                    d.draw()
                    try:
                        socket.bt_obex_send_file(target[0], target[1], os.path.normpath(fname))
                    except:
                        e+=1
                    fs+=1
                except:
                    pass
                if s.bt_abort:
                    break
            d.close()
            if e:
                user.note(_(u"Inviati %i file(s)\nNon inviati: %i")%(fs-e,e),_(u"Invio completato"),-1)
            else:
                user.note(_(u"Inviati %i file(s)")%(fs),_(u"Invio completato"),-1)
            del e,fs,abort,d

    def set_attributes(s,file,rd=0,si=0,hi=0,ar=0):
        if rd:
            fileutils.set_readonly(file)
        else:
            fileutils.unset_readonly(file)
        if si:
            fileutils.set_system(file)
        else:
            fileutils.unset_system(file)
        if hi:
            fileutils.set_hidden(file)
        else:
            fileutils.unset_hidden(file)
        if ar:
            fileutils.set_archive(file)
        else:
            fileutils.unset_archive(file)

    def attributes(s,file):
        fd=[]
        dt=[]
        if type(file)==types.ListType:
            files=file
        else:
            files=[file]
        for file in files:
            if os.path.isfile(file):
                fd.append(to_unicode(os.path.normpath(file)))
            else:
                dt.append(to_unicode(os.path.normpath(file)))
        def salvataggio(s,dati,files,dirs):
            rd = bool(dati[0][2][1])
            si = bool(dati[1][2][1])
            hi = bool(dati[2][2][1])
            ar = bool(dati[3][2][1])
            if dirs:
                #sub_dirs=user.query(u"Applicare gli attributi anche alle sottocartelle?",u"Attributi")
                sub_dirs=appuifw.query(_(u"Applicare gli attributi anche alle sottocartelle?"),"query")
            else:
                sub_dirs=0
            try:
                for filename in files+dirs:
                    try: s.set_attributes(to_unicode(filename),rd,si,hi,ar)
                    except: pass
                if dirs and sub_dirs:
                    to_set=[]
                    for dirname in dirs:
                        try:
                            f,d=s.scan_dir(dirname,1,1)
                            to_set+=f+d
                        except:
                            pass
                    for filename in to_set:
                        try: s.set_attributes(to_unicode(filename),rd,si,hi,ar)
                        except: pass
            except:
                pass
            try:
                explorer.view_refresh()
            except:
                pass
        on_off_general_list=[_(u"No"),_(u"Sì")]
        s1,s2,s3,s4=0,0,0,0
        try:
            if fd:
                s1,s2,s3,s4=fileutils.is_readonly(fd[0]),fileutils.is_system(fd[0]),fileutils.is_hidden(fd[0]),fileutils.is_archive(fd[0])
                # dati = [
                # (u"Sola lettura",'combo', (on_off_general_list,bool(fileutils.is_readonly(fd[0])))),
                # (u"Sistema",'combo', (on_off_general_list,bool(fileutils.is_system(fd[0])))),
                # (u"Nascosto",'combo', (on_off_general_list,bool(fileutils.is_hidden(fd[0])))),
                # (u"Archivio",'combo', (on_off_general_list,bool(fileutils.is_archive(fd[0]))))
                # ]
            else:
                s1,s2,s3,s4=fileutils.is_readonly(dt[0]),fileutils.is_system(dt[0]),fileutils.is_hidden(dt[0]),fileutils.is_archive(dt[0])
                # dati = [
                # (u"Sola lettura",'combo', (on_off_general_list,bool(fileutils.is_readonly(dt[0])))),
                # (u"Sistema",'combo', (on_off_general_list,bool(fileutils.is_system(dt[0])))),
                # (u"Nascosto",'combo', (on_off_general_list,bool(fileutils.is_hidden(dt[0])))),
                # (u"Archivio",'combo', (on_off_general_list,bool(fileutils.is_archive(dt[0]))))
                # ]
        except:
            appuifw.note(u"Error reading file attributes","error")

        dati = [
            (_(u"Sola lettura"),'combo', (on_off_general_list,bool(s1))),
            (_(u"Sistema"),'combo', (on_off_general_list,bool(s2))),
            (_(u"Nascosto"),'combo', (on_off_general_list,bool(s3))),
            (_(u"Archivio"),'combo', (on_off_general_list,bool(s4)))
            ]
        appuifw.app.screen="normal"
        appuifw.app.title=_(u"Attributi")
        flags = appuifw.FFormEditModeOnly+appuifw.FFormDoubleSpaced
        fff = appuifw.Form(dati, flags)
        fff.save_hook =lambda x: salvataggio(s,x,fd,dt)
        fff.execute()
        appuifw.app.screen="full"
    def get_cluster_size(s, drive, retry = 5):
        sz = -1
        attempt = 0
        ok = 0
        fn = '%s\\!$&clstr_tst_sz&$'%drive
        while (not ok) and (attempt<retry):
            attempt += 1
            try:
                try:
                    os.remove(fn)
                except:
                    pass
                s1 = DriveInfo.free_drivespace()[drive]
                f = open(fn,'wb',0) #0 byte buffer: direct write on disk
                print 'drive ready...'
                f.write('\x00') #null byte
                sf = DriveInfo.free_drivespace()[drive]
                f.close()
                print 'file created...'
                # and now the trick. The difference of space is exactly the cluster size, if nothing changed in the mean time
                sz = s1-sf
                os.remove(fn)
                print 'file removed...'
                #if the disk was in use it's a problem, we need to verify if is accurate (8 multiples)
                if sz%8:
                     print 'invalid size! Retrying...'
                else:
                     print 'cluster size of',drive,' is',sz,'kB'
                     ok = 1
            except:
                print_exc()
                print drive,'not ready!'
        return sz


class cript_system:
#Criptografy system: it's very simple, but powerful...
    def __init__(s,file_list):
        import uu
        s.uu=uu
        del uu
        #Percentuale criptazione: 42% in più rispetto all'originale
        s.cripted_ext=".cripted"
        s.file_list=[]#file
        for file in file_list:
            if os.path.isfile(file): s.file_list.append(file)
        if not s.file_list:
            user.note(_(u"Nessun file corretto trovato per essere crittografato o decrittografato.\nNota: le cartelle non possono essere crittografate."),_(u"Errore crittografia"),-1)
            return
        if not user.query(_(u"%i file(s) da crittografare-decrittografare. Il processo potrebbe durare alcuni minuti.\nContinuare?")%len(s.file_list),_(u"Crittografia"),left=_(u"Continua")):
            return
        d=progress_dialog(_(u"Crittografia in corso..."),u"",max=len(s.file_list))
        fs=0
        for file in s.file_list:
            s.file_dir,s.file_name=os.path.split(file)
            s.ext=os.path.splitext(s.file_name)[1]
            d.update_state(fs+1)
            d.title = ru(s.file_name)
            #d.set_title(ru(s.file_name))
            d.draw()
            if s.ext.lower()!=s.cripted_ext:
                #try:
                    #if sysinfo.free_drivespace()[unicode(s.file_drive.capitalize())]<os.path.getsize(s.file):
                        #user.note(u"Spazio insufficiente su disco!\nLiberare memoria cancellando alcuni dati.","Errore")
                        #continue
                #except: pass
                #if not appuifw.query(u"Criptare il file:\n%s" % s.file_name,"query"): return
                #appuifw.note(u"Criptazione in corso nel file %s..." % s.file_name+s.cripted_ext,"conf")
                s.cript(file,os.path.normpath(s.file_dir+"\\"+s.file_name+s.cripted_ext))
                #appuifw.note(u"Ok! FIle criptato correttamente! %s" % s.file_name+s.cripted_ext,"conf")
            else:
             # try:
                # if sysinfo.free_drivespace()[unicode(s.file_drive.capitalize())]<os.path.getsize(s.file):
                    # appuifw.note(u"Spazio insufficiente su disco!\nLiberare memoria cancellando dati.","error")
                    # return
             # except: pass
             #if not appuifw.query(u"Decriptare il file: %s" % s.base_name,"query"): return
             #appuifw.note(u"Decriptazione in corso nel file %s..." % s.file_name,"conf")
             s.decript(file,os.path.normpath(s.file_dir+"\\"+os.path.splitext(s.file_name)[0]))
             #appuifw.note(u"Ok! File decriptato correttamente! %s" % s.base_name,"conf")
            fs+=1
        d.close()
        explorer.refresh(ru(s.file_name))

    def cript(s,file_src,file_dest):
        if os.path.exists(file_dest):
         #appuifw.note(u"File già esistente!")
            return
        try:
            s.uu.encode(file_src,file_dest)
        except:
         #appuifw.note(unicode(error),"error")
            try:
                os.remove(file_dest)
            except:
                pass
    def decript(s,file_src,file_dest):
        if os.path.exists(file_dest):
         #appuifw.note(u"File già esistente!")
            return
            try:
                s.uu.decode(file_src,file_dest)
            except:
         #appuifw.note(unicode(error),"error")
                try:
                    os.remove(file_dest)
                except:
                    pass

class Applet:

    def __init__(s, end_callback = None):
    
        pass
        #TODO:!!

class mini_viewer:
#Visualizzatore immagini
#Image viewer
#s.img-> Immagine finale da blittare al canvas
#s.fimg-> Immagine originale da usare solo come lettura
    def __init__(s, file, end_callback = None, directory = None):
        s.old_state = ui.get_state()
        s.active = 1
        s.sleeping = 0
        s.file = to_unicode(file)
        s.name = os.path.split(s.file)[1]
        #s.info=[]
        s.index = 0
        s.frame_id = 0
        s.frames = None #None when the image has no multiple frames
        if directory:
            s.images_in_dir = s.scansiona_dir(directory)
        else:
            s.images_in_dir = s.scansiona_dir()
        try:
            s.index = s.images_in_dir.index(s.file)
        except:
            pass

        #Imposta variabili immagine
        s.x,s.y = 0,0
        s.zoom = 100#842.5#27.5
        s.brightness = 0
        #s.mode=0 #0Normale;1-2 Landscape modo 1 e 2
        s.caricato = 0
        s.stats = [0,0] #Loading time; used ram
        s.img = None
        s.fimg = None
        s.osd_timer = e32.Ao_timer()
        s.menu = []
        s.end_callback = end_callback
        s.screen_change(1)
        #s.iclock = thread.allocate_lock()
        s.carica_immagine()
        s.body_init()
        s.refresh_ao()

    def body_init(s, ui_state=None):
        s.keybd = Keyboard()
        ui.unbindall()
        ui.key_callback = s.keybd.handle_event
        ui.focus_cb = s.focus
        ui.mode_callback = s.screen_change
        ui.menu.menu([
                        (_(u"Successiva"),[s.next],u"[3]"),
                        (_(u"Precedente"),[s.previous],u"[1]"),
                        (_(u"Schermo"),[ui.change_screen_mode],_(u"[Matita]")),
                        (_(u"Zoom"),[(_(u"Zoom +"),lambda: s.set("zoom",s.zoom+5,2)),
                                    (_(u"Zoom -"),lambda: s.set("zoom",s.zoom-5,2)),
                                    (_(u"Adatta"),lambda: s.fit_to_screen_resize(1)),
                                    (_(u"Originale"),lambda: s.set("zoom",100,2)),
                                    (_(u"Manuale"),lambda: s.set("zoom",appuifw.query(_(u"Inserire ingrandimento (100%->originale)"),'number',s.zoom),2))
                                    ]),
                        (_(u"Luminosità"),[(_(u"Aumenta"),s.lum_up),
                                          (_(u"Diminuisci"),s.lum_down),
                                          (_(u"Reimposta"),lambda: s.set("brightness",0,1))
                                    ]),
                        (_(u"Modifica"),[s.edit]),
                        (_(u"Dettagli immagine"),[s.show_info]),
                        (_(u"Indietro"),[s.esci])
                    ]
                    )
        ui.right_key=[s.esci,u'']
        ui.left_key=[None,u'']
        s.touch_control.start()
        if ui_state:
            s.screen_change()
        s.redraw_img()

    def show_info(s):
        testo=u""
        # bpp_dict={'1':u"1 (bianco e nero)",'L':u"8 (256, scala di grigio)",
                # 'RGB12':u"12 (4096 colori)",'RGB16':u"16 (65536 colori)",
                # 'RGB':u"24 (16.7 milioni di colori)"}
        # try: bpp=bpp_dict[s.fimg.mode]
        # except: bpp=u"-"
        ix,iy=s.fimg.size
        df = (ix-iy)
        if df:
            aspect=(abs(ix/df),abs(iy/df))
        else:
            aspect=(1,1)
        for t,v in [(_(u"Nome immagine: %s"),s.name),
                    (_(u"Cartella: %s"),os.path.split(s.file)[0]),
                    (_(u"Risoluzione: %i x %i"),s.fimg.size),
       # (u"Profondità colore: %s",bpp),
                    (_(u"Aspetto: %i:%i"),aspect),
                    (_(u"Ram utilizzata per l'immagine: %s"),dataformatter.sizetostr(s.stats[0])),
                    (_(u"Immagine caricata in: %f sec"),s.stats[1])]:
            testo+=t%v
            testo+="\r\n"
        s.osd_timer.cancel()
        ui.key_callback=None
        ui.focus_cb=None
        ui.mode_callback=None
        text_viewer(text=testo,end_callback=lambda n,b: s.body_init(b),title=_(u"Dettagli immagine"))

    def screen_change(s, at_init=0):
        s.osd_timer.cancel()
        try:
            s.img.stop()
        except:
            pass
        # if ui.landscape==0:
           # s.mode=0
            # del s.img
            # s.img=Image.new(ui.screen_size)
        # elif ui.landscape==1:
           # s.mode=2
            # del s.img
            # s.img=Image.new(ui.landscape_size)
        # elif ui.landscape==2:
           # s.mode=1
        s.touch_control = TouchDriver(skinUI.text_area_rect, (s.touch_cb, None, None,))
        s.img = None
        s.img = Image.new(ui.display_size)
        if not at_init:
            s.fit_to_screen_resize()
            s.create_image()
            s.redraw_img()

    def focus(s,state):
        if state:
            s.sleeping=0
        else:
            s.sleeping=1

    def loaded(s, err):
    
        if err == 0:
        #OK.Image sucefully loaded
            s.stats[1] = time.clock() - s.stats[1]
        else:
        #Some errors
            s.fimg = Image.new(s.img.size)
            s.fimg.clear(0)
            #text_center(s.fimg, (s.fimg.size[1]/2)-10 , _(u"Immagine non valida!"),(255,0,0))
            text_render(s.fimg, (0, (s.fimg.size[1]/2)-10), _(u"Immagine non valida!"), (255,0,0), alignment = ALIGNMENT_CENTER)
            #text_cut(s.fimg, (2,(s.fimg.size[1]/2)+10) , unicode(e), (0,0,255))
            text_render(s.fimg, (2,(s.fimg.size[1]/2)+10), unicode(err), (0,0,255), alignment = ALIGNMENT_CENTER, cut = 1)
        s.caricato = 1
        s.fit_to_screen_resize()
        s.create_image()
        s.redraw_img(1)
        s.hide_info()

    def carica_immagine(s):
        s.stats = [0,0]
        s.fimg = None
        try:
            try:
                rm = sysinfo.free_ram()
                tu = time.clock()
            except:
                pass
            s.fimg = Image.new(Image.inspect(os.path.normpath(s.file))['size'])#Image.open(os.path.normpath(s.file))
            try:
                s.stats[0] = rm - sysinfo.free_ram()
                s.stats[1] = tu#time.clock() - tu
            except:
                pass
            s.fimg.load(os.path.normpath(s.file), s.loaded)
        except Exception, e:
            s.loaded(e)
            return
          #  s.fimg = Image.new(s.img.size)
          #  s.fimg.clear(0)
            #text_center(s.fimg, (s.fimg.size[1]/2)-10 , _(u"Immagine non valida!"),(255,0,0))
          #  text_render(s.fimg, (0, (s.fimg.size[1]/2)-10), _(u"Immagine non valida!"), (255,0,0), alignment = ALIGNMENT_CENTER)
            #text_cut(s.fimg, (2,(s.fimg.size[1]/2)+10) , unicode(e), (0,0,255))
          #  text_render(s.fimg, (2,(s.fimg.size[1]/2)+10), unicode(e), (0,0,255), alignment = ALIGNMENT_CENTER, cut = 1)
        #s.caricato=1
        s.fit_to_screen_resize()
        s.create_image()
        s.redraw_img(1)
        s.hide_info()

    def fit_to_screen_resize(s, r=0):
        ix = float(s.fimg.size[0])#dimensione x foto
        iy = float(s.fimg.size[1])#dimensione y foto
        x,y = 0,0
        dx,dy = s.img.size
        if ix>dx or iy>dy:
            if (dx/(ix/iy))<=dy:
                target = int(dx/(ix/iy))#(x,((int(dx/(ix/iy))))/2,dx,dy-(((int(dx/(ix/iy))))/2))
                s.zoom = int((float(target)/float(iy))*100)
            else :
                target = int(dy/(iy/ix))#((dx-(int(dy/(iy/ix))))/2,y,dx-((dx-(int(dy/(iy/ix))))/2),dy)
                s.zoom = int(float(target)/float(ix)*100)
        else:
            s.zoom = 100#target=((dx-ix)/2,(dy-iy)/2)
        if r:
            s.create_image()
            s.redraw_img(1)
            s.hide_info()

    def coord_check(s, xc, yc):
        x,y = s.img.size
        xd = (xc-x)/2
        yd = (yc-y)/2
        #X coord
        if xc <= x:
            s.x = 0
        elif s.x < -xd:
            s.x = -xd
        elif s.x > xd:
            s.x = xd
        #Y coord
        if yc <= y:
            s.y = 0
        elif s.y < -yd:
            s.y = -yd
        elif s.y > yd:
            s.y = yd

    def create_image(s):
        ix,iy=s.fimg.size
        dx,dy=s.img.size
        xf=(ix*s.zoom)/100.0
        yf=(iy*s.zoom)/100.0
        # print 'Zoom: %i'%(s.zoom)
        # print 'Resize: %i,%i'%(xf,yf)
        # try: #Se diverso da 1:1
            # print 'Aspect Ratio %i:%i'%(xf/(xf-yf),yf/(xf-yf))
        # except:
            # print 'Aspect Ratio 1:1'
        s.coord_check(xf,yf)
        dxxf=(dx-xf)/2
        dyyf=(dy-yf)/2
        s.img.clear(0)
        s.img.blit(s.fimg,target=( dxxf + s.x, dyyf + s.y, dx-dxxf + s.x, dy - dyyf + s.y), scale=1)

    def redraw_img(s,info=0):
        x,y = ui.canvas_image.size
        ui.canvas_image.clear(skinUI.IV_bg_color)
        if s.caricato:
            ui.canvas_image.blit(luminosita(s.img,s.brightness))
            if info:
                #text_cut(ui.canvas_image,(2,12),s.name,fill=0x00ff00)
                #lines_render(ui.canvas_image, (2,None), s.name, 0x00ff00, None, ALIGMENT_UP, 1
                text_render(ui.canvas_image, (2,None), s.name, 0x00ff00, None, ALIGNMENT_UP, 1)
                ui.canvas_image.text((3,24),_(u"Luminosità: %i %%")%s.brightness,fill=0x00ff00)
                ui.canvas_image.text((3,36),_(u"Zoom: %i")%s.zoom,fill=0x00ff00)
                if s.images_in_dir:
                    text_render(ui.canvas_image, (0, y), u"%i / %i"%(s.index+1,len(s.images_in_dir)), 0x00ff00, None, ALIGNMENT_CENTER)
                    #text_center(ui.canvas_image,y-4,u"%i / %i"%(s.index+1,len(s.images_in_dir)),0x00ff00)
        else:
            #ui.canvas_image.text((5,20),_(u"Caricamento ..."),fill=(255,255,255),font=(None,16,16))
            #text_center(ui.canvas_image, y/2, _(u"Caricamento ..."), (255,255,255), (None,16,16))
            text_render(ui.canvas_image, (0, y/2), _(u"Caricamento ..."), (255,255,255), (None,16,16), ALIGNMENT_CENTER)
        if ui.menuopened:
            ui.menu.update_background(ui.canvas_image)
        ui.canvas_refresh()

    def normal_key_cb(s):
            #Scorrimento immagine
            if s.keybd.is_down(EScancodeLeftArrow):
                s.x += 5
            elif s.keybd.is_down(EScancodeRightArrow):
                s.x -= 5
            elif s.keybd.is_down(EScancodeDownArrow):
                s.y -= 5
            elif s.keybd.is_down(EScancodeUpArrow):
                s.y += 5
            #Zoom
            if s.keybd.is_down(EScancode2):
                s.zoom+=5
            elif s.keybd.is_down(EScancode8):
                if s.zoom-5<=0: return
                s.zoom-=5
            elif s.keybd.pressed(EScancode5):
                s.fit_to_screen_resize()
            #Luminosità
            if s.keybd.is_down(EScancode4):
                s.lum_down()
                e32.ao_sleep(0.05)
            elif s.keybd.is_down(EScancode6):
                s.lum_up()
                e32.ao_sleep(0.05)
            #Immagni
            if s.keybd.pressed(EScancode1):
                s.previous()
            elif s.keybd.pressed(EScancode3):
                s.next()

    def landscape2_key_cb(s):
            #Scorrimento immagine
            if s.keybd.is_down(EScancodeUpArrow):
                s.x += 5
            elif s.keybd.is_down(EScancodeDownArrow):
                s.x -= 5
            elif s.keybd.is_down(EScancodeLeftArrow):
                s.y -= 5
            elif s.keybd.is_down(EScancodeRightArrow):
                s.y += 5
            #Zoom
            if s.keybd.is_down(EScancode5):
                s.zoom+=5
            elif s.keybd.is_down(EScancode4):
                if s.zoom-5<=0: return
                s.zoom-=5
            elif s.keybd.pressed(EScancode2):
                s.fit_to_screen_resize()
            #Luminosità
            if s.keybd.is_down(EScancode7):
                s.lum_down()
            elif s.keybd.is_down(EScancode8):
                s.lum_up()
            #Immagni
            if s.keybd.pressed(EScancode3):
                s.previous()
            elif s.keybd.pressed(EScancode9):
                s.next()

    def landscape1_key_cb(s):
            #Scorrimento immagine
            if s.keybd.is_down(EScancodeDownArrow):
                s.x += 5
            elif s.keybd.is_down(EScancodeUpArrow):
                s.x -= 5
            elif s.keybd.is_down(EScancodeRightArrow):
                s.y -= 5
            elif s.keybd.is_down(EScancodeLeftArrow):
                s.y += 5
            #Zoom
            if s.keybd.is_down(EScancode5):
                s.zoom+=5
            elif s.keybd.is_down(EScancode6):
                if s.zoom-5<=0: return
                s.zoom-=5
            elif s.keybd.pressed(EScancode2):
                s.fit_to_screen_resize()
            #Luminosità
            if s.keybd.is_down(EScancode9):
                s.lum_down()
            elif s.keybd.is_down(EScancode8):
                s.lum_up()
            #Immagni
            if s.keybd.pressed(EScancode7):
                s.previous()
            elif s.keybd.pressed(EScancode1):
                s.next()

    def touch_cb(s, direction, dx, dy):
        if direction & MOVE_RIGHT:
            s.next()
        if direction & MOVE_LEFT:
            s.previous()
        if direction & MOVE_UP:
            s.zoom+=5
        if direction & MOVE_DOWN:
            if s.zoom-5<=0:
                return
            s.zoom-=5

    def refresh_ao(s):
        while s.active:
            if not s.caricato or s.sleeping:
                e32.ao_sleep(0.3)
                continue
            old=(s.x,s.y,s.zoom)
            if ui.landscape==2:
                s.landscape2_key_cb()
            elif ui.landscape==1:
                s.landscape1_key_cb()
            else:
                s.normal_key_cb()
            if old!=(s.x,s.y,s.zoom):
                s.create_image()
                s.redraw_img()
            e32.ao_yield()

    def scansiona_dir(s,d=None):
        imgs=[]
        eu=ext_util
        exts=eu.imgextensions
        if d:
            directory=to_unicode(os.path.normpath(d))
            files=os.listdir(directory)
            for file in files:
                file=to_unicode(file)
                ext=eu.splitext(file).lower()
                if ext in exts:
                    imgs.append(os.path.join(directory,file))
        else: 
            for elem in explorer.content_of_dir:
                f=to_unicode(elem[0])
                ext=eu.splitext(f).lower()
                if ext in exts:
                    imgs.append(f)
        return imgs

    def esci(s):
        s.active=0
        ui.shutdown_effect(-20)
        #image object cleaning
        try:
            s.fimg.stop()
        except:
            pass
        s.fimg = None
        s.img = None
        s.osd_timer.cancel()

        if s.end_callback:
            s.end_callback(s.name,s.old_state)

    def next(s):
        if not s.images_in_dir: return
        if s.index>=len(s.images_in_dir)-1:
            s.index=0
        else:
            s.index+=1
        s.caricato=0
        s.brightness=0
        s.file=s.images_in_dir[s.index]
        s.name=os.path.split(s.file)[1]
        s.carica_immagine()
        s.create_image()
        s.redraw_img()
    def previous(s):
        if not s.images_in_dir: return
        if s.index==0:
            s.index=len(s.images_in_dir)-1
        else:
            s.index-=1
        s.caricato=0
        s.brightness=0
        s.file=s.images_in_dir[s.index]
        s.name=os.path.split(s.file)[1]
        s.carica_immagine()
        s.create_image()
        s.redraw_img()
    def set(s,n,v,r=0,i=1):
        if v==None:
            return
        if v=="switch":
            vo=eval("s.%s"%n)
            if vo:
                exec("s.%s=0"%n)
            else:
                exec("s.%s=1"%n)
        else:
            exec("s.%s=%s"%(n,v))
        if r:
            if r==2:
                s.create_image()
            s.redraw_img(i)
            if i:
                s.hide_info()
    def lum_up(s):
        if s.brightness>=100:
            return
        s.brightness+=5
        s.redraw_img(1)
        s.hide_info()
    def lum_down(s):
        if s.brightness<=-100:
            return
        s.brightness-=5
        s.redraw_img(1)
        s.hide_info()
    def hide_info(s):
        s.osd_timer.cancel()
        s.osd_timer.after(2, s.redraw_img)
    def edit(s):
        # Open the image editor application
        #TODO: check for these methods
        s.sleeping=1
        if main.S60v2:
            e32.start_exe(u'apprun.exe',u'Z:\\System\\Apps\\ImageEditor\\ImageEditor.app O"%s"'%s.file)
        else:
            e32.start_exe(u'Z:\\sys\\bin\\ImageEditor.exe',s.file)

class lrc:
        def __init__(s,fn):
            s.L = []
            s.total = 0
            t = []
            s.C = (s.load(fn)).splitlines()
            for i in s.C:
                if i[0]=='[': #Evitiamo roba non standard e linee vuote not s.C in ['','\r\n','\n'] or
                        try:
                            #If it is a number, int doesn't raise exception
                            int(i[1:3])
                            t.append(i)
                        except:
                            pass
            for i in t:
                time = i.replace('][',',')
                l = time.find(']')
                time = time[1:l]
                min = time.split(':')[0]
                sec = time.split(':')[1].split('.')[0]
                hs = time.split(':')[1].split('.')[1]
                time = s.mshs_to_ms(min,sec,hs)
                text = i[l+1:]
                s.L.append((time,text))
            s.total = len(s.L)
        def mshs_to_ms(self,m,sec,hs):
                s = 0.0
                s +=  float(m)*60.0
                s += float(sec)
                try:
                    #Su certi file da problemi..non ho capito il motivo ma con un bel try\except tutto va bene ;)
                    s += float(hs)/100.0
                except:
                    pass
                return long(s*1000000)
        def load(s,file):
            # if file == None:
                # raise IOError('Nessun file!')
            f = open(file, 'r')
            text = f.read()
            f.close()
            return decode_text(text)
        def get(s,tm): #Ritorna il testo alla determinata posizione
            if not s.L:
                return None#"Nessun lyrics"
           # prev=s.L[0][0] #X il tempo in ms usiamo tipo 'long'
           # prev=0L
            #t=''
            for i in xrange(0,s.total):
                if i==s.total-1 and s.L[-1][0]<=tm:
                    return s.L[-1][1]
                elif s.L[i][0]<tm<s.L[i+1][0]:
                    #prev=s.L[i][1]
                    return s.L[i][1] #Riga prima
            # for tempo,testo in s.L:
                # tempo=long(tempo)
                # if prev<tm<tempo: #Confrontiamo l'input con il tempo del testo lyrics con quello della canzone e ritorna il testo se in quella posizione c'e', altrimenti None
                    # prev=tempo#s.L[s.L.index((tempo,testo))+1][0]
                    # return s.L[s.L.index((tempo,testo))-1][1] #Riga prima

class mini_player:
    def __init__(s, fi, end_callback = None, playlist = None):
        #TODO: fade in-out
        try:
            if explorer.is_playing:
                if not user.query(_(u"E' in corso la riproduzione di un altro file multimediale.\nInterromperlo?"),_(u"Riproduttore musicale")):
                    explorer.is_playing.restore()
                    print "Another song is playing. Exiting..."
                    return
                else:
                    explorer.is_playing.esci(0)
        except:
            pass
        try:
            from player import player
            s.player=player
            del player
        except:
            appuifw.note(_(u"Impossibile avviare %s.\nReinstallare l'applicazione o il modulo.")%"player")
            return
        s.t = e32.Ao_timer()
        s.main = None
        s.filename = None
        s.file = fi
        s.end_callback = end_callback
        s.audio_index = 0
        s.audio_list = []
        s.playlist_name = None
        if playlist:
            s.playlist_name=os.path.basename(s.file)
            try:
                if playlist==".pyl":
                    pyl = ur(open(ur(s.file)).read())
                    for path,name in eval(pyl):
                        s.audio_list.append(os.path.normpath(path))
                elif playlist==".m3u":
                    import m3u
                    s.audio_list=m3u.read_playlist(ur(s.file),(1,os.path.dirname(ur(s.file))))
                else:
                    appuifw.note(_(u"Formato playlist illeggibile."))
                #if not s.audio_list: return
                if s.audio_list:
                    s.file=s.audio_list[0]
                else:
                    return
            except Exception,e:
                appuifw.note(_(u"Impossibile caricare la playlist!"),"error")
                #appuifw.note(unicode(e))
                #print str(e)
                return
        else:
            try: 
                s.audio_list=s.scansiona_dir()
                s.audio_index=s.audio_list.index(os.path.normpath(s.file))
            except:
                s.audio_list=[s.file]
                s.audio_index=0

        s.audio_running = 1
        s.not_hidden = 1
        s.changing = 0
        s.explorer_update = 0

        s.load_audio()
        s.set_ui()
        s.screen_change(1)
        s.vol_bar = StatusBar(s.set_vol)
        s.vol_bar.position = skinUI.volume_bar_rect#(100,200,110,300)
        #s.vol_bar.orientation = ORIENTATION_VERTICAL
        s.vol_bar.max_value = 10
        s.vol_bar.init_values()

        s.seek_bar = StatusBar(s.set_seek)
        s.seek_bar.formatter = long
        s.seek_bar.position = skinUI.seek_bar_rect#(50,50,100,60)
        #s.seek_bar.max_value = 10
        s.seek_bar.init_values()
        
        #s.touch_control = TouchDriver(skinUI.main_drawable_rect, s.touch_cb)#{MOVE_RIGHT: s.next, MOVE_LEFT, s.previous})

        s.redraw_screen()
        s.canvas_refresh()
        s.bind()
        s.t.after(0.1,s.refresh_ao)

    def set_seek(s, v):
        s.audio_istance.sound_opened.set_position(v)

    def set_vol(s, v):
        s.audio_istance.sound_opened.set_volume(v)
        s.audio_istance.volume = v

    def hide(s):
        explorer.is_playing = s
        s.not_hidden = 0
        if s.end_callback:
            if s.playlist_name:
                s.end_callback(s.playlist_name)
            else:
                s.end_callback(s.filename)

    def restore(s):
        explorer.is_playing = None
        s.not_hidden = 1
        s.set_ui()
        s.screen_change(1)
        s.redraw_screen()
        s.canvas_refresh()
        s.bind()

    def esci(s, cb = 1):
        s.audio_running=0
        try:
            s.audio_istance.stop()
            s.audio_istance.close()
        except:
            pass
        del s.main
        if s.end_callback and cb:
            if s.playlist_name:
                s.end_callback(s.playlist_name)
            else:
                s.end_callback(s.filename)

    def refresh_ao(s):
        try:
            state,volume,duration,current_position = s.audio_istance.getstate()
            s.vol_bar.actual_value = volume
            s.seek_bar.max_value = duration
            s.seek_bar.actual_value = current_position
            settings.volume = volume
            #TODO: seek sec value set by user
            if duration > 10000000:
                #nei file molto corti altrimenti diventa impossibile il seeking
                s.audio_istance.sec_rew_ff = int(duration*0.0000001)
            else:
                s.audio_istance.sec_rew_ff = 1
            if (state == 1) and (s.audio_istance.in_pause == 0):
                if settings.audio_repeat == 0: #Senza ripetizione, alla fine della playlist si ferma
                    s.next(0)
                elif (settings.audio_repeat == 1) and s.audio_running: #Ripetizione singola canzone
                    s.audio_istance.play_audio(0)
                elif (settings.audio_repeat == 2) and s.audio_running: #Ripetizione playlist intera
                    s.next()
        except:
            pass
        if s.audio_running and ui.focus_state and s.not_hidden:
            s.redraw_screen()
            s.canvas_refresh()
        if s.audio_running:
            s.t.after(0.1,s.refresh_ao)

    def touch_cb(s, direction):
        
        if direction&MOVE_RIGHT:
            s.next()
        elif direction&MOVE_LEFT:
            s.previous()

    def bind(s):
        ui.unbindall()
        s.seek_bar.set_touch()
        s.vol_bar.set_touch()
        #s.touch_control.start()
        ui.bind(EScancodeSelect,lambda: s.audio_istance.pause())
        ui.bind(EStdKeyIncVolume,lambda: s.audio_istance.vol_up())
        ui.bind(EStdKeyDecVolume,lambda: s.audio_istance.vol_down())
        if ui.landscape==1:
            ui.bind(EScancodeLeftArrow,lambda: s.audio_istance.vol_up())
            ui.bind(EScancodeRightArrow,lambda: s.audio_istance.vol_down())
            ui.bind(EScancodeDownArrow,lambda: s.audio_istance.rew())
            ui.bind(EScancodeUpArrow,lambda: s.audio_istance.ff())
            ui.bind(EScancode7,s.previous)
            ui.bind(EScancode1,s.next)
        elif ui.landscape==2:
            ui.bind(EScancodeRightArrow,lambda: s.audio_istance.vol_up())
            ui.bind(EScancodeLeftArrow,lambda: s.audio_istance.vol_down())
            ui.bind(EScancodeUpArrow,lambda: s.audio_istance.rew())
            ui.bind(EScancodeDownArrow,lambda: s.audio_istance.ff())
            ui.bind(EScancode3,s.previous)
            ui.bind(EScancode9,s.next)
        else:
            ui.bind(EScancodeUpArrow,lambda: s.audio_istance.vol_up())
            ui.bind(EScancodeDownArrow,lambda: s.audio_istance.vol_down())
            ui.bind(EScancodeLeftArrow,lambda: s.audio_istance.rew())
            ui.bind(EScancodeRightArrow,lambda: s.audio_istance.ff())
            ui.bind(EScancode1,s.previous)
            ui.bind(EScancode3,s.next)

    def set_ui(s):
        #TODO: backlight on if lyrics
        #TODO: song info popup
        #TODO: help popup
        ui.save_state()
        ui.mode_callback=s.screen_change
        ui.menu.menu([#(u"Modifica tag",[lambda: id3tag_edit_form(s.file,s.leggi_tags)]),
                    (_(u"Modalità riproduzione"),[(_(u"Normale"),lambda: settings.set("audio_repeat","0")),
                                               (_(u"Ripeti"),lambda: settings.set("audio_repeat","1")),
                                               (_(u"Ripeti tutto"),lambda: settings.set("audio_repeat","2")),
                                               (_(u"Casuale"),lambda: settings.set("audio_shuffle","switch"))]),
                    # (u"Controllo",[(u"Pausa-riprendi",lambda: settings.set("audio_repeat","0")),
                                               # (u"Riavvolgi",lambda: settings.set("audio_repeat","1")),
                                               # (u"Avanzamento",lambda: settings.set("audio_repeat","2")),
                                               # (u"Casuale",lambda: settings.set("audio_shuffle","switch"))]),
                    # (u"Luce attiva con lyrics",[lambda: exec('''
                                                                # if s.backlight_on:
                                                                    # s.backlight_on=0
                                                                # else:
                                                                    # s.backlight_on=1
                                                                # ''')]),
                    (_(u"Crea Playlist"),[s.create_playlist]),
                    (_(u"Usa come sottofondo"),[s.hide]),
                    (_(u"Nascondi"),[main.switch_to_bg]),
                    (_(u"Indietro"),[s.esci])
                    ])
        ui.right_key=[s.esci,_(u'Indietro')]
        ui.left_key=[None,_(u'Menu')]

    def load_audio(s, play_init = 1):
        s.leggi_tags() #Tag ID3, LRC (Lyrics se presenti) e nome file
        try:
            s.audio_istance.stop()
            s.audio_istance.close()
        except:
            pass
        try:
            s.audio_istance = s.player(audiofile=os.path.normpath(s.audio_list[s.audio_index]),volume=settings.volume)
            if play_init:
                s.audio_istance.play_audio()
        except Exception, e:
            appuifw.note(unicode(e))

    def leggi_tags(s):
        fn = s.audio_list[s.audio_index]
        s.title = u""
        s.album = u""
        s.artist = u""
        s.year = u""
        s.genre = u""
        s.tags = None
        ext=os.path.splitext(fn)[1].lower()
        s.filename=os.path.basename(fn)
        try:
            #'Titolo':title, 'Artista':artist, 'Album':album, 'Anno':year,'Commento':comment,'Genere':genere
            if ext == u".mp3":
                import id3
                s.tags = id3.getID3(ur(fn))
            elif ext == u".ogg":
                import oggtag
                s.tags = oggtag.readOggTag(ur(fn))
        except:
            pass

        if s.tags:
            s.title = s.tags["Titolo"]
            s.album = s.tags["Album"]
            s.artist = s.tags["Artista"]
            s.year = s.tags["Anno"]
            s.genre = s.tags["Genere"]

        try:
            s.lyric = lrc('%s.lrc'%ur(os.path.splitext(fn)[0]))
        except:
            s.lyric=None

    def create_playlist(s):
        import m3u
        name = appuifw.query(_(u"Nome playlist"),"text",u"Playlist")
        if name:
            try:
                m3u.write_playlist(os.path.join(explorer.dir,"%s.m3u"%ur(name)),s.audio_list)
                appuifw.note(_(u"Playlist %s scritta correttamente!")%name)
            except:
                appuifw.note(_(u"Errore nella creazione della playlist."),'error')

        s.explorer_update = 1

    def scansiona_dir(s, d = None):
        sng = []
        eu = ext_util
        exts = eu.audioextensions
        if d:
            directory = to_unicode(os.path.normpath(d))
            files = os.listdir(directory)
            for file in files:
                file = to_unicode(file)
                ext = eu.splitext(file).lower()
                if ext in exts:
                    sng.append(os.path.join(directory,file))
        else: 
            for elem in explorer.content_of_dir:
                f = to_unicode(elem[0])
                ext = eu.splitext(f).lower()
                if ext in exts:
                    sng.append(f)
        return sng

    def next(s,user = 1):
        if (not s.audio_running) or s.changing:
            return
        if settings.audio_repeat==0 and (len(s.audio_list)-1==s.audio_index) and (not user):
            return
        s.changing = 1
        if settings.audio_shuffle:
            s.audio_index = random.randint(0,len(s.audio_list)-1)%len(s.audio_list)
        else:
            s.audio_index = (s.audio_index+1)%len(s.audio_list)

        s.load_audio()
        s.changing=0

    def previous(s):
        if (not s.audio_running) or s.changing:
            return
        s.changing = 1

        if settings.audio_shuffle:
            s.audio_index = (random.randint(0,len(s.audio_list)-1))%len(s.audio_list)
        else:
            s.audio_index = (s.audio_index-1)%len(s.audio_list)

        s.load_audio()
        s.changing=0

    def ms_to_hh_mm(s, ms):
        num=ms/1000000
        return u"%02i:%02i" % (num/60,num%60)

    def screen_change(s, at_init = 0):

        s.main = None
        s.main=Image.new(ui.display_size)
        if not at_init:
            s.bind()
            s.redraw_screen()
            s.canvas_refresh()

    def redraw_screen(s):
        s.main.blit(grafica.bg_img)
        try:
            state,volume,duration,current_position = s.audio_istance.getstate()
        except:
            state,volume,duration,current_position = 0,0,0,0
        #text_cut(s.main, (2,13) , u'%s' % (s.filename), settings.text_color, None)
        text_render(s.main, skinUI.title_rect, u'%s' % (s.filename), settings.text_color, None, ALIGNMENT_MIDDLE|ALIGNMENT_CENTER, 1)
        if s.tags:
            #s.main.text((6,40),u'%s: %s' % (_(u"Titolo"),s.title), settings.text_color)
            #s.main.text((6,52),u'%s: %s' % (_(u"Artista"),s.artist), settings.text_color)
            #s.main.text((6,64),u'%s: %s' % (_(u"Album"),s.album), settings.text_color)
            lines = [u'%s: %s' % (_(u"Titolo"),s.title),
                     u'%s: %s' % (_(u"Artista"),s.artist),
                     u'%s: %s' % (_(u"Album"),s.album)
                    ]
            lines_render(s.main, skinUI.tags_position, lines, 4, settings.text_color, None,cut = 1)
        else:
            s.main.text(skinUI.tags_position, _(u"Nessun tag presente"), settings.text_color)
        if s.lyric:
            try:
                tt = s.lyric.get(current_position)
                if tt:
                    ln = wrap_text_to_array(tt, 'dense', s.main.size[0])
                    #lines_render(s.main, skinUI.lyrics_pos, ln, 4, settings.lyrics_color, 'dense', ALIGNMENT_CENTER)
                    dy = skinUI.lyrics_pos[1]
                    for i in ln:
                        coord, b, r, n = text_render(s.main, (None, dy), i, settings.lyrics_color, 'dense', ALIGNMENT_CENTER)
                        dy = coord[1] + abs(b[1])+abs(b[3])
                        # text_center(s.main,80+(12*y),i,settings.lyrics_color,'dense')
                        # y+=1
                        #text_render(s.main, skinUI.lyrics_pos
            except Exception,e:
                print str(e)
        # try:
            # per1 = (float(current_position) / float(duration)) * 100.0
            # x_per = per1 + 6.0
        # except:
            # x_per = 6
        lines_render(s.main, skinUI.audio_info_rect, [u'%s' % (s.ms_to_hh_mm(current_position)), _(u"%s di %s")%(s.audio_index+1,len(s.audio_list))], 4, settings.text_color, "legend", ALIGNMENT_DOWN)
        text_render(s.main, skinUI.audio_info_rect, u'%s' % (s.ms_to_hh_mm(duration)), settings.text_color, "legend", ALIGNMENT_RIGHT|ALIGNMENT_DOWN)
        # if ui.landscape:
            # text_right(s.main, 148, u'%s' % (s.ms_to_hh_mm(duration)), settings.text_color, "legend", 106)
            # s.main.text((6,148),, settings.text_color, "legend")
            # s.main.text((6,138),, settings.text_color, "legend")
            # s.main.rectangle((5,151,106,158),settings.text_color)
            # s.main.rectangle((6,152,x_per,157), settings.playerbar_color1, settings.playerbar_color2)
            # s.main.rectangle((194,157-(settings.volume*4),199,157),settings.playerbar_color1, settings.playerbar_color2)
            # s.main.rectangle((193,116,200,158),settings.text_color)
            #x,y=110,150
        # else:
            # text_right(s.main,168,, settings.text_color, "legend", 106)
            # s.main.text((6,168),u'%s' % (s.ms_to_hh_mm(current_position)), settings.text_color, "legend")
            # s.main.text((6,156),_(u"%s di %s")%(s.audio_index+1,len(s.audio_list)), settings.text_color, "legend")
            # s.main.rectangle((5,171,106,178), settings.text_color)
            # s.main.rectangle((6,172,x_per,177), settings.playerbar_color1, settings.playerbar_color2)
            # s.main.rectangle((162,177-(settings.volume*4),167,177), settings.playerbar_color1, settings.playerbar_color2)
            # s.main.rectangle((161,136,168,178), settings.text_color)
            #x,y=110,170
            
        s.vol_bar.draw(s.main)
        s.seek_bar.draw(s.main)
        x,y=skinUI.icons_pos
        if settings.audio_repeat:
            s.main.line((x,y+1,x,y,x+9,y,x+9,y+8,x,y+8,x,y+4,x+3,y+4,x+3,y+2,x+5,y+4,x+3,y+6,x+3,y+4), settings.text_color)
        if settings.audio_shuffle:
            x+=15
            s.main.rectangle((x,y,x+10,y+9), settings.text_color)
            for i in [(x+2,y+2),(x+2,y+6),(x+7,y+6),(x+7,y+2)]:
                s.main.point(i, settings.text_color)

    def canvas_refresh(s):
        if ui.menuopened:
            ui.menu.update_background(s.main)
        else:
            ui.draw(s.main)

class text_viewer:
    def __init__(s, file = None, text = u"", end_callback = None, line_sep = u"\r\n", title = u"", read_only=0):
        #TODO: visualizzazione full screen testo con sfondo personalizzabile
        #TODO: zoom testo
        s.timg = None
        s.text = text
        s.read_only = read_only
        s.fullscreen_mode = 0
        s.zoom = 1
        s.file = file
        s.title = title
        s.total_char = 0
        s.codifica = "ascii"
        s.line_sep = line_sep
        if s.file:
            s.file_name = os.path.split(file)[1]
            try:
                s.text,s.codifica,s.total_char,s.line_sep = s.load()
            except Exception,e:
                user.note(_(u"Errore di lettura:\n%s")%e, _(u"Visualizzatore testi"), -1)
                return
        else:
            s.file = s.title
            s.file_name = s.title
        s.text_lines = []
        #s.line_no = 0
        s.end_callback = end_callback
        # How many pixel to add to text height
        s.spacing = 1
        # s.x = 5
        # s.text_width = 164
        # s.min_x = s.x
        #s.y = 30
        #s.first_line = 0
        #s.end_line = 10
        #s.scroll_offset = 5
        s.line_query = 1
        s.VScrollbar = ScrollBar(lambda x: s.goto_line(x))
        #s.VScrollbar.orientation = ORIENTATION_VERTICAL
        # s.HScrollbar = ScrollBar(lambda x: s.set_x(-x))
        # s.HScrollbar.orientation = ORIENTATION_HORIZONTAL
        
        #s.touch_control = TouchDriver(skinUI.text_area_rect, s.touch_move, 1, 1)
        #s.touch_control.x_speed = 0.99
        #s.touch_control.y_speed = 0.99
        # s.HSrollbar = Scrollbar()
        # s.HScrollbar = ORIENTATION_HORIZONTAL
        #s.screen_change(1)
        if s.text_init(s.line_sep):
            s.screen_change(1)
            s.body_init()
    #TODO: file position saving
    # def file_position(s,r=1):
        # fn=directory.data_dir+"\\position.dat"

    def load(s):
        #TODO: improve utf-16 detection
        f = open(s.file, 'r')
        text = f.read()
        f.close()
        if text.startswith('\xff\xfe') or text.startswith('\xfe\xff'):# or text.find("\x20\x29")!=-1 or text.find("\x0d\x00\x0a\x00")!=-1: #Se è unicode (utf16)
            enc = 'utf16' #Codifica x l'unicode
            text = text.decode(enc)
        elif text.startswith('\xef\xbb\xbf'): #Se è utf8
            enc = 'utf8'
            text = text.decode(enc)
        else:
            for enc in __supported_encodings__:
                try:
                    text = text.decode(enc).replace(u"\x00","")
                    break
                except UnicodeError:
                    pass
            else:
                raise UnicodeError
        return text.replace(u'\r\n', u'\u2029').replace(u'\n', u'\u2029') , enc , len(text) , u'\u2029'

    def text_init(s, line_sep):
    
        s.text_lines = []
        
        s.text = s.text.replace(u"\t",u"    ") #Sostituiamo i tabulatori con 4 spazi (cosi non si vede il quadratino)
        lines = s.text.split(line_sep)
        
        if (settings.text_viewer_view_mode == 0) and (not s.read_only):
            # No screen wrap
            s.text_lines = lines#s.text.split(line_sep)
            #s.line_no = len(s.text_lines)
#            return 1
        elif (settings.text_viewer_view_mode == 1) or s.read_only:
            # Text wrap
            
            for line in lines:
                t = wrap_text_to_array(line, skinUI.text_viewer_font, skinUI.TV_text_width)
                # if ui.landscape:
                    # t=wrap_text_to_array(line,'dense',192)
                # else:
                    # t=wrap_text_to_array(line,'dense',164)
                if t!=():
                    s.text_lines+=t
                else:
                    s.text_lines.append(u"")
      #  del lines
#            return 1
        else:
            # In case of some errors
            settings.text_viewer_view_mode = 0
            return s.text_init(line_sep)
        # Maximum width of the text in the normal (non-wrap) mode
        s.max_x = 0
        # The maximum text height
        s.text_height = 0
        # Scan every line for these results
        for line in s.text_lines:
        
            bbox, p, n_char = TEST_IMG.measure_text(line, skinUI.text_viewer_font)
            h = abs(bbox[1]) + abs(bbox[3])
            if h>s.text_height:
                s.text_height = h
            if p>s.max_x:
                s.max_x = p
        s.max_x -= skinUI.TV_text_width
        
        s.line_no = len(s.text_lines)
        return 1

    def set_menu(s):

        if settings.text_viewer_view_mode:
            mdm = (_(u"Adatta a schermo"),[s.cambia_visualizzazione],_(u"Sì"))
        else:
            mdm = (_(u"Adatta a schermo"),[s.cambia_visualizzazione],_(u"No"))
        s.menu = [mdm,(_(u"Cerca..."),[s.cerca_parola],u"[5]"),(_(u"Vai a linea..."),[s.goto_line]),
                    (_(u"Pagina su"),[lambda: s.pag_su(-10)],u"[9]"),(_(u"Pagina giù"),[lambda: s.pag_giu(10,1)],u"[#]"),
                    (_(u"Inizio"),[lambda: s.goto_line(0)],u"[7]"),(_(u"Fine"),[lambda: s.goto_line(s.line_no-1)],u"[*]")
                ]

        if ui.landscape == 1:
            s.menu = [mdm,(_(u"Cerca..."),[s.cerca_parola],u"[5]"),(_(u"Vai a linea..."),[s.goto_line]),
                        (_(u"Pagina su"),[lambda: s.pag_giu(10,1)],u"[0]"),(_(u"Pagina giù"),[lambda: s.pag_su(-10)],u"[*]"),
                        (_(u"Inizio"),[lambda: s.goto_line(0)],u"[8]"),(_(u"Fine"),[lambda: s.goto_line(s.line_no-1)],u"[7]")
                    ]
        elif ui.landscape == 2:
            s.menu = [mdm,(_(u"Cerca..."),[s.cerca_parola],u"[5]"),(_(u"Vai a linea..."),[s.goto_line]),
                        (_(u"Pagina su"),[lambda: s.pag_giu(10,1)],u"[0]"),(_(u"Pagina giù"),[lambda: s.pag_su(-10)],u"[#]"),
                        (_(u"Inizio"),[lambda: s.goto_line(0)],u"[7]"),(_(u"Fine"),[lambda: s.goto_line(s.line_no-1)],u"[8]")
                    ]

        ui.menu.menu(s.menu)

    def screen_change(s,at_init = 0):
        dx, dy = ui.display_size
        old = ui.landscape
        s.touch_control = TouchDriver(skinUI.text_area_rect, (s.touch_move, None, None,), .90, .96)
        s.timg = Image.new(ui.display_size)

        s.text_dy = (s.text_height + s.spacing)
        # Start Y pos
        s.y = skinUI.title_rect[3] + s.text_dy
        s.x = skinUI.TV_x
        s.min_x = s.x
        s.scroll_offset = s.x
        
        s.max_lines = int( (skinUI.main_drawable_rect[3] - skinUI.title_rect[3]) / float((s.text_height + s.spacing)))
        s.first_line = 0
        s.end_line = s.max_lines
        s.VScrollbar.max_page = s.max_lines
        s.VScrollbar.min_value = 0
        s.VScrollbar.position = skinUI.scrollbar_rect#(dx-20,20,dy-41,15)
        s.VScrollbar.init_values()
        
        # s.HScrollbar.max_page = skinUI.TV_text_width
        # s.HScrollbar.min_value = - s.min_x
        # s.HScrollbar.max_value = s.max_x# - s.min_x
        # s.HScrollbar.position = skinUI.v_scrollbar_rect#(dx-20,20,dy-41,15)
        # s.HScrollbar.init_values()
        
        if not at_init:
            #Se si cambia risoluzione ed è attiva l'impostazione di adattamento a schermo, bisogna riadattare tutto il testo
            #Mettiamo a posto la posizione del testo (riga prima e riga ultima)
            if s.line_no > s.max_lines:
                s.end_line = s.first_line+s.max_lines
            if s.end_line > s.line_no:
                s.first_line = s.line_no-s.max_lines
                s.end_line = s.first_line+s.max_lines
                #print "Riadattato per la modalita':",ui.landscape
            if settings.text_viewer_view_mode==1 and (old==0 or old==2):
                s.text_init(s.line_sep)
            else:
                if settings.text_viewer_view_mode==1:
                    s.first_line = 0
                    s.end_line = s.max_lines
            s.bind()
            s.text_redraw()

    def text_init2(s, line_sep):
        s.text_lines = [] #Prepariamo e puliamo la variabile da cose vecchie.
        # s.first_line = 0
        # s.end_line = s.max_lines
        s.text = s.text.replace(u"\t",u"    ") #Sostituiamo i tabulatori con 4 spazi (cosi non si vede il quadratino)
        if settings.text_viewer_view_mode==0 and (not s.read_only):
            s.text_lines = s.text.split(line_sep)
            s.line_no = len(s.text_lines)
            return 1
        elif settings.text_viewer_view_mode==1 or s.read_only:
            lines=s.text.split(line_sep)
            for line in lines:
                t = wrap_text_to_array(line, 'dense', s.text_width)
                # if ui.landscape:
                    # t=wrap_text_to_array(line,'dense',192)
                # else:
                    # t=wrap_text_to_array(line,'dense',164)
                if t!=():
                    s.text_lines+=t
                else:
                    s.text_lines.append(u"")
            s.line_no = len(s.text_lines)
            del lines
            return 1
        else:
            settings.text_viewer_view_mode=0
            s.text_init(line_sep)

    def esci(s):
        del s.text,s.text_lines,s.line_no
        if s.read_only:
            s.end_callback(None, s.old_ui)
        else:
            s.end_callback(to_unicode(s.file_name), s.old_ui)

    def cambia_visualizzazione(s):
        s.x = s.scroll_offset
        settings.text_viewer_view_mode = settings.text_viewer_view_mode^1
        ok = s.text_init(s.line_sep)
        s.set_menu()
        s.bind()
        if ok:
            s.text_redraw()

    def set_orizzontal_position(s, text):
        if (settings.text_viewer_view_mode != 1) and (not s.read_only):

            s.x = -(s.timg.measure_text(text, skinUI.text_viewer_font)[1])

    def cerca_parola(s):

        parola = appuifw.query(_(u"Parola chiave da cercare:"),"text",settings.text_viewer_search_string)
        if not parola:
            return
        settings.text_viewer_search_string = parola
        parola = parola.lower()
        index = 0
        for i in s.text_lines:
            pos = i.lower().find(parola)
            if pos != -1:
                s.goto_line(index)
                s.set_orizzontal_position(i[0:pos]) #Move orizzontally the text to find the searched word
                s.text_redraw()
                if not user.query(_(u"Parola trovata in\n linea %i - colonna %i\nContinuare la ricerca?")%(index+1,pos+1),_(u"Ricerca testo")):
                    break
            index += 1

        user.note(_(u"Ricerca completa: fine del testo raggiunta."),_(u"Ricerca testo"))

    def body_init(s):
        s.old_ui = ui.get_state()
        ui.mode_callback = s.screen_change
        ui.right_key = [s.esci,_(u'Indietro')]
        if not s.read_only:
            s.set_menu()
            ui.left_key = [None,_(u'Menu')]
        else:
            ui.menu.menu([])
            ui.left_key = [None,u'']
        s.bind()
        s.text_redraw()

    def bind(s):
        ui.unbindall()
        s.VScrollbar.set_touch()
        #s.HScrollbar.set_touch()
        s.touch_control.start()
        #ui.bind_touch(EDrag, lambda x: s.touch_move(), skinUI.text_area_rect)
        if ui.landscape==1:
            ui.bind(EScancodeUpArrow,s.pag_su)
            ui.bind(EScancodeLeftArrow,s.pag_giu)
            if not settings.text_viewer_view_mode:
                if not s.read_only:
                    ui.bind(EScancodeDownArrow,s.sx)
                    ui.bind(EScancodeUpArrow,s.dx)
            ui.bind(EScancode9, lambda: s.goto_line(s.line_no-1))
            ui.bind(EScancode8, lambda: s.goto_line(0))
            # ui.bind(53, s.cerca_parola)
            # ui.bind(49, s.inizio_linea)
            ui.bind(EScancode0, lambda: s.pag_su(s.max_lines))
            ui.bind(EScancodeHash, lambda: s.pag_giu(s.max_lines))
        elif ui.landscape==2:
            ui.bind(EScancodeLeftArrow,s.pag_su)
            ui.bind(EScancodeRightArrow,s.pag_giu)
            if not settings.text_viewer_view_mode:
                if not s.read_only:
                    ui.bind(EScancodeUpArrow,s.sx)
                    ui.bind(EScancodeDownArrow,s.dx)
            ui.bind(EScancode7, lambda: s.goto_line(s.line_no-1))
            ui.bind(EScancode8, lambda: s.goto_line(0))
            # ui.bind(53, s.cerca_parola)
            # ui.bind(49, s.inizio_linea)
            ui.bind(EScancode0, lambda: s.pag_su(s.max_lines))
            ui.bind(EScancodeStar, lambda: s.pag_giu(s.max_lines))
        else:
            ui.bind(EScancodeUpArrow,s.pag_su)
            ui.bind(EScancodeDownArrow,s.pag_giu)
            if not settings.text_viewer_view_mode:
                if not s.read_only:
                    ui.bind(EScancodeLeftArrow,s.sx)
                    ui.bind(EScancodeRightArrow,s.dx)
            ui.bind(EScancodeStar, lambda: s.goto_line(s.line_no-1))
            ui.bind(EScancode7, lambda: s.goto_line(0))
            ui.bind(EScancode9, lambda: s.pag_su(s.max_lines))
            ui.bind(EScancodeHash, lambda: s.pag_giu(s.max_lines))
        #Common keys
        ui.bind(EScancode5, s.cerca_parola)
        ui.bind(EScancode1, lambda: s.set_x(s.min_x))
        ui.bind(EScancode3, lambda: s.set_x(-(s.max_x - s.min_x)))
        #TODO: key 3 to go a the end of the line
        #TODO: add qwerty specific keys

    def touch_move(s, d, x, y):
    
        if d%MOVE_RIGHT:
            s.set_x(s.x - x)
        elif d%MOVE_LEFT:
            s.set_x(s.x + x)
        if d%MOVE_UP:
            s.pag_su()
        elif d%MOVE_RIGHT:
            s.pag_giu()

    def pag_giu(s,plus=1):
        if s.line_no>s.max_lines:
            if plus+s.end_line>s.line_no:
                s.end_line = s.line_no
                s.first_line = s.end_line-s.max_lines
            else:
                s.first_line += plus
                s.end_line += plus
            s.text_redraw()

    def pag_su(s,lines=1):
        if s.line_no>s.max_lines:
            s.first_line -= lines
            s.end_line -= lines
            if s.first_line<0:
                s.end_line = s.max_lines
                s.first_line = 0
            s.text_redraw()
    def goto_line(s, linea = None):
        m = linea
        if linea == None:
            linea = appuifw.query(_(u"Linea (att:%i,max:%i):")%(s.first_line+1,s.line_no),"number",s.line_query)
            if not linea:
                return
            linea -= 1
        if s.line_no<=s.max_lines:
            return
        if ((linea+1)>s.line_no) and (m!=None):
            user.note(_(u"Linea inesistente!\nMax: %i\nInserito: %i")%(s.line_no,linea+1),_(u"Visualizzatore testi"),-1)
        else:
            if not linea>s.line_no-s.max_lines:
                s.end_line = linea+s.max_lines
                s.first_line = linea
            else:
                s.end_line = s.line_no
                s.first_line = s.line_no-s.max_lines
            s.line_query = linea+1
            s.text_redraw()

    def set_x(s, x):
        # Remember that s.max_x must be a negative number!
        if (-s.max_x <= x <= s.min_x):
            s.x = x
        s.text_redraw()

    def sx(s):
        if not (s.x == s.min_x):
            s.x += s.scroll_offset
            if (s.x%s.scroll_offset):
                s.x -= (s.x%s.scroll_offset) #be sure to have the right position
            s.text_redraw()

    def dx(s):
        #s.x -= s.scroll_offset
        #s.text_redraw()
        s.x = max(-s.max_x, s.x - s.scroll_offset)
        s.text_redraw()

    def text_redraw(s,rect=None):
        s.timg.blit(grafica.bg_img)
        #lines_render(s.timg, skinUI.main_drawable_rect, s.text_lines[s.first_line : s.end_line], 1, settings.text_color, skinUI.text_viewer_font)
        i = 0
        for line in s.text_lines[s.first_line:s.end_line]:
            s.timg.text((s.x, s.y + (s.text_dy*i)), line, settings.text_color, skinUI.text_viewer_font)
            i += 1
        # if not s.title:
            
        # else:
            
        if not s.title:
            xr = text_render(s.timg, skinUI.title_rect, u"%i/%s"%(s.total_char, s.codifica), settings.path_color, (None, int(skinUI.title_rect[3]*.70)), ALIGNMENT_MIDDLE|ALIGNMENT_RIGHT)[2]
            #text_cut(s.timg, (3,11), to_unicode(s.file_name), settings.path_color, None)
            text_render(s.timg, skinUI.title_rect, to_unicode(s.file_name), settings.path_color, (None, int(skinUI.title_rect[3]*0.90)), ALIGNMENT_MIDDLE|ALIGNMENT_LEFT, width = xr)
        else:
        
            text_render(s.timg, skinUI.title_rect, to_unicode(s.title), settings.path_color, (None, int(skinUI.title_rect[3]*0.90)), ALIGNMENT_MIDDLE|ALIGNMENT_LEFT)
            #s.timg.text((3,11), to_unicode(s.title), settings.path_color)
            #text_render(s.timg, skinUI.title_rect, unicode(s.total_char), settings.path_color, (None, int(skinUI.title_rect[3]/2.0)), ALIGNMENT_UP|ALIGNMENT_RIGHT)
            #text_render(s.timg, skinUI.title_rect, to_unicode(s.codifica), settings.path_color, (None, int(skinUI.title_rect[3]/2.0)), ALIGNMENT_DOWN|ALIGNMENT_RIGHT)
            #s.timg.text((3,24),_(u"Codifica: '%s'")%s.codifica,fill=settings.path_color)
            #text_right(s.timg,24,u"%i"%s.total_char,settings.path_color,u"Nokia Sans S60",s.timg.size[0]-8)
        # Scroll Bar (Vertical: line count)
        if s.line_no>s.max_lines:
            #text_render(s.timg, (None,None), u"%i%%"%(float(s.line_no-1) / 100 * s.first_line), settings.label_color, ('digital', int(skinUI.softkeys_rect[3]/2.0)), 
            s.VScrollbar.current = s.first_line# - s.max_lines
            s.VScrollbar.max_value = s.line_no# - s.max_lines
            s.VScrollbar.draw(s.timg)
            
        # s.HScrollbar.current = - s.x# - s.min_x)
        # s.HScrollbar.draw(s.timg)

        ui.draw(s.timg)

class id3tag_edit_form:
#The id3 tag editor class, based on appuifw.Form widget
    def __init__(s, file, end_callback = None, read_tag = 1, title = u"", artist = u"", album = u"", year = 0, comment = u"", track = None, genre = 255):

        s.file=file
        try:
            import id3
            s.id3=id3
            del id3
        except:
            user.note(_(u"Impossibile avviare %s.\nReinstallare l'applicazione o il modulo.")%"id3")
            return
        s.callback = end_callback
        if read_tag:
            s.tags = s.id3.getID3(s.file) #'Titolo':title, 'Artista':artist, 'Album':album, 'Anno':year,'Commento':comment,'Genere':genere
            if not s.tags:
                s.title = title
                s.album = album
                s.artist = artist
                s.year = year
                s.comment = comment
                #s.track=track
                s.genre = genre
            else:
                s.title = s.tags["Titolo"]
                s.album = s.tags["Album"]
                s.artist = s.tags["Artista"]
                s.year = s.tags["Anno"]
                #if s.year=="-" or s.year=="": s.year="0"
                try:
                    s.year = int(s.year)
                except:
                    s.year = 0
                s.comment = s.tags["Commento"]
                #s.track=None
                s.genre = s.tags["Genere"]
        else:
            s.title = title
            s.album = album
            s.artist = artist
            s.year = year
            s.comment = comment
            #s.track=track
            s.genre = genre

    def remove_tags(s):
        if user.query(u"Eliminare tutti i tag esistenti?",u"MP3 Advanced Settings"):
            s.id3.remove_all_tags(s.file)
            if s.callback: s.callback()
    def salvataggio(s,dati):
        s.salvato = 1
    def editor(s):
        appuifw.app.screen="normal"
        try:
            appuifw.app.title=u"Modifica tag: %s"%to_unicode(os.path.split(s.file)[1])
        except:
            appuifw.app.title=u"Modifica tag: %s"%""
        generi = map(unicode,s.id3.generi)
        try:
            index = generi.index(s.genre)
        except:
            index = 0
        dati = [
            (_(u"Artista"),'text',s.artist),
            (_(u"Titolo"),'text',s.title),
            (_(u"Album"),'text',s.album),
            (_(u"Anno"),'number',int(s.year)),
            (_(u"Commento"),'text',s.comment),
            (_(u"Genere"),'combo',(generi, index)),
           ]
        flags = appuifw.FFormEditModeOnly + appuifw.FFormDoubleSpaced
        fff = appuifw.Form(dati, flags)
        fff.save_hook = s.salvataggio
        s.salvato = 0
        fff.execute()
        if s.salvato:
            try:
                s.artist = (fff[0][2]).encode("latin-1")
                s.title = (fff[1][2]).encode("latin-1")
                s.album = (fff[2][2]).encode("latin-1")
                s.year = int(fff[3][2])
                s.comment = (fff[4][2]).encode("latin-1")
                s.genre = int(fff[5][2][1])
                s.id3.updateID3(s.file,s.title,s.artist,s.album,s.year,s.comment,None,s.genre)
                appuifw.note(_(u"Tag salvati con successo."),"conf")
            except:
                appuifw.note(_(u"Errore nell' aggiornamento dei tag."),"error")
        else:
            appuifw.note(_(u"Modifiche non aggiornate."),"conf")

        appuifw.app.screen="full"
        if s.callback:
            s.callback()

class info_box:
# This is the class wich views properties of files, dirs and system!
    def __init__(s, file, end_callback=None):
        if not file:
            return
        s.main = None
        s.language()
        s.file = os.path.normpath(file)
        try:
            s.set_fname(file)
        except:
            s.filename = u""
        s.title_text = u""
        s.ext = u""
        s.info_totali = []
        s.info_extra = []
        s.len_info = 0
        s.max_lines = 10
        s.end_callback = end_callback
        s.advanced_menu = {u".mp3": [(_(u"Modifica ID3 Tag"),[lambda: id3tag_edit_form(s.file,s.re_init).editor()]),
                                   (_(u"Rimuovi ID3 Tag"),[lambda: id3tag_edit_form(s.file,s.re_init).remove_tags()])],
                         u".sysinfo": [(_(u"Aggiorna"),[s.re_init])]
                        }
        s.x = 5
        s.min_x = s.x
        s.y = 30
        s.first_line = 0
        s.end_line = s.max_lines
        s.scroll_offset = 5
        user.direct_note(_(u"Scansione..."),_(u"Informazioni"))
        if s.info_init():
            s.body_init()
        else:
            ui.canvas_refresh()

    def set_fname(s,fn):
        s.filename = to_unicode(os.path.split(fn)[1])

    def re_init(s):
        s.info_init()
        s.info_redraw()

    def language(s):
        s.size_text = _(u"Dimensione")
        s.size2_text = _(u"Dimensione totale")
        s.size3_text = _(u"Spazio occupato")
        s.size4_text = _(u"Spazio libero")
        s.date_text = _(u"Data modifica")
        s.hour_text = _(u"Ora modifica")
        s.file_text = _(u"Files totali")
        s.dirs_text = _(u"Cartelle Totali")
        s.string_mapping = {  'Files':s.file_text,
                            'Langs':_(u"Lingue disponibili"),
                            'Drive':_(u"Disco di destinazione"),
                            'Version':_(u"Versione"),
                            'UID':u"UID",
                            'Options':_(u"Opzioni"),
                            'Type':_(u"Tipo"),
                            'MIDlet-Name':_(u"Nome"),
                            'MIDlet-Version':_(u"Versione"),
                            'MIDlet-Vendor':_(u"Produttore"),
                            'Midlet-Description':_(u"Descrizione"),
                            'MicroEdition-Profile':u"",
                            'MicroEdition-Configuration':u""
                        }
        s.type_names = [_(u"Non presente"),_(u"Sconosciuto"),_(u"Floppy"),_(u"Hard Disk (MMC)"),_(u"CD-Rom"),_(u"Ram Drive"),_(u"Flash"),_(u"Rom"),_(u"Remoto")]
        s.media_attr = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80]
        s.media_attr_names = [_(u"Dimensione variabile"),_(u"Doppia densità"),_(u"Formattabile"),_(u"Sola lettura"),_(u"Bloccabile"),_(u"Bloccato"),_(u"Ha una password"),_(u"Legge mentre scrive")]
        s.drive_attr = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80]
        s.drive_attr_names = [_(u"Locale"),_(u"Rom"),_(u"Rediretta"),_(u"Virtuale"),_(u"Interna"),_(u"Removibile"),_(u"Remota"),_(u"Transazione")]

    def get_attr(s):
        l = [(_(u"Attributi:"),"")]
        try:
            f = to_unicode(s.file)
            if fileutils.is_hidden(f):
                l.append((u'\t-%s'%_(u"Nascosto"),''))
            if fileutils.is_system(f):
                l.append((u'\t-%s'%_(u"Sistema"),''))
            if fileutils.is_readonly(f):
                l.append((u'\t-%s'%_(u"Sola lettura"),''))
            if fileutils.is_archive(f):
                l.append((u'\t-%s'%_(u"Archivio"),''))
        except:
            pass
        if len(l)>1:
            return l
        else:
            return []

    def get_drv_attr(s):
        l = []
        t1 = []
        try:
            type = s.type_names[DriveInfo.drive_type()[s.file]]
            fs = str(DriveInfo.drives_fs()[s.file]).decode('utf16')
            ui = hex(DriveInfo.drives_uid()[s.file])
            attr = DriveInfo.drives_attr()[s.file]
            vol_attr = DriveInfo.medias_attr()[s.file]
            for n in s.drive_attr:
                if attr&n:
                    t1.append(('\t-'+s.drive_attr_names[s.drive_attr.index(n)],''))
            for n in s.media_attr:
                if vol_attr&n:
                    t1.append(('\t-'+s.media_attr_names[s.media_attr.index(n)],''))
            l = [(_(u"Tipo"),type),
                 (_(u"File System"),fs),
                 (u"UID",ui),
                 (_(u"Attributi:"),"")] + t1
        except:
            pass
        return l

    def ms_to_hh_mm(s,ms):
        num = ms/1000000.0
        return u"%02i:%02i" % (num/60,num%60)

    def info_init(s):
        rf = to_unicode(s.file)
        s.info_totali = []
        s.info_extra = []
        s.len_info = 0
        if s.file == "<SYS.INFO>":
            try:
                s.filename = _(u"Symbian OS S60 %s.%s")%(e32.s60_version_info[0:2])
            except:
                s.filename = _(u"Symbian OS S60")
            s.title_text = _(_(u"Informazioni sistema"))
            s.ext = u".sysinfo"
            try:
                f = codecs.open("Z:\\system\\versions\\sw.txt",'r','utf16')
                c = f.read()
                c = c.splitlines()[0].split('\\n')[0:3]
                f.close()
                for i in c:
                    s.info_totali.append((i,""))
            except:
                pass
            s.info_totali += s.get_system_info()
            s.len_info = len(s.info_totali)
            return 1
        elif rf in e32.drive_list():
            s.title_text = _(u"Informazioni disco %s")%rf
            attr_list = s.get_drv_attr()
            s.tot_files,s.tot_dir,s.tot_size = 0,0,0
            try:
                        #t1=time.clock()
                s.scan_dir_info(os.path.normpath(s.file))
                        #print "Taken: ",time.clock()-t1
            except:
                pass
            s.filename = u""
            if DriveInfo:
                total_size = dataformatter.sizetostr(DriveInfo.total_drivespace()[s.file])
                try:
                    s.filename = DriveInfo.drive_names()[s.file]
                except:
                    pass
            else:
                total_size = "?"
            try:
                s.info_totali = [(s.size_text, total_size),
                               (s.size4_text, dataformatter.sizetostr(sysinfo.free_drivespace()[s.file])),
                               (s.size3_text, dataformatter.sizetostr(s.tot_size)),
                               (s.file_text, unicode(s.tot_files)),
                               (s.dirs_text, unicode(s.tot_dir))] + attr_list
            except:
                s.info_totali = [(_(u"Disco non pronto o inesistente"),"")]
            s.len_info = len(s.info_totali)
            return 1
        elif os.path.isfile(s.file):
            try:
                try:
                    attr_list = s.get_attr()
                    date = os.path.getmtime(s.file) + main.time_zone
                    tm = time.gmtime(date)
                    ora = dataformatter.gethour(tm)#time.ctime(date).split(" ")[3]
                    data = dataformatter.getdate(tm)
                    sz = os.path.getsize(s.file)
                    size = dataformatter.sizetostr(sz)
                    try:
                        clustersize = gestione_file.get_cluster_size(s.file[:2])
                        sizeondisk = clustersize * ((sz + clustersize - 1) / clustersize)
                    except:
                        sizeondisk = -1
                    s.ext = os.path.splitext(rf)[1].lower()
                    s.title_text = _(u"Informazioni file (%s)")%s.ext
                    s.info_totali = [(s.size_text, size),(_(u"Spazio su disco"), dataformatter.sizetostr(sizeondisk)),(s.date_text,data),(s.hour_text,ora)]+attr_list
                except:
                    s.info_totali = [(_(u"File inaccessibile"), '')]
                    traceback.print_exc()

                if s.ext == u".sis":
                    try:
                        import sistools
                        temp = sistools.read_sis_file(s.file) #dict
                        for info in temp:
                            try:
                                s.info_extra.append( (s.string_mapping[info], temp[info]) )
                            except:
                                s.info_extra.append( (info, temp[info]) )
                    except:
                        pass
                elif s.ext == u".jar":
                    try:
                        import sistools
                        info_list = sistools.read_jar_info(s.file)
                        m = []
                        p = []
                        for elem in info_list:
                            try:
                                name = s.string_mapping[elem[0]]
                                if name:
                                    m.append((name,elem[1]))
                                else:
                                    p.append((elem[1].strip(" "),""))
                            except:
                                pass
                        s.info_extra = m + p
                        #del info_list,m,p
                    except:
                        pass
                elif s.ext in [u".app",u".dll",u".exe",u".mdl",u".aif"]:
                    try :
                        s.info_extra = [(u"UID",get_UID(s.file)[2])]
                    except:
                        pass
                elif s.ext == u".m3u":
                    try:
                        import m3u
                        s.info_extra = [(_(u"Canzoni totali"),len(m3u.read_playlist(s.file)))]
                    except:
                        pass
                elif s.ext == u".pyl":
                    try:
                        pyl = eval(ur(open(s.file).read()))
                        s.info_extra = [(_(u"Canzoni totali"),len(pyl))]
                        del pyl
                    except:
                        pass
                elif s.ext in ext_util.audioextensions:
                    try:
                        import audio
                        snd = audio.Sound().open(rf)
                        d = snd.duration()
                        snd.close()
                        del snd
                        s.info_extra = [(_(u"Durata"),s.ms_to_hh_mm(d))]
                        del audio
                    except: pass
                    if s.ext == u".mp3":
                        try:
                            import id3
                            i = id3.getID3(s.file) #dict
                            if i:
                                s.info_extra += i.items()
                            else:
                                s.info_extra += [(_(u"Nessun tag presente"),"")]
                            del i
                        except:
                            pass
                    elif s.ext == u".ogg":
                        try:
                            import oggtag
                            i = oggtag.readOggTag(s.file) #dict
                            s.info_extra += i.items()
                            del i
                        except:
                            pass
                    else:
                        s.info_extra += [(_(u"Nessun tag presente"),'')]
                elif s.ext in ext_util.imgextensions:
                    try:
                        try:
                            s.info_extra = [(_(u"Risoluzione"),u"%i x %i"%(Image.inspect(rf)['size']))]
                        except:
                            pass
                        import exif
                        s.info_extra += (exif.process_file(open(s.file,'rb'))).items()
                    except:
                        pass
                elif s.ext == u".zip":
                    try:
                        import zipfile
                        f = zipfile.ZipFile(s.file)
                        sz = 0
                        tf = 0
                        tc = 0
                        for af in f.namelist():
                            fi = f.getinfo(af)
                            sz += fi.file_size
                            if af.endswith("/"):
                                tc += 1
                            else:
                                tf += 1
                        f.close()
                        s.info_extra = [(_(u"Dimensione non compressa"),dataformatter.sizetostr(sz)),
                                      (_(u"Files"),unicode(tf)),
                                      (_(u"Cartelle"),unicode(tc))]
                    except:
                        pass
                elif s.ext == u".rar":
                    try:
                        import rarfile
                        f = rarfile.RarFile(s.file)
                        sz = 0
                        tf = 0
                        tc = 0
                        for af in f.namelist():
                            fi = f.getinfo(af)
                            sz += fi.file_size
                            if fi.isdir():
                                tc += 1
                            else:
                                tf += 1
                        f.close()
                        s.info_extra = [(_(u"Dimensione non compressa"),dataformatter.sizetostr(sz)),
                                      (_(u"Files"),unicode(tf)),
                                      (_(u"Cartelle"),unicode(tc))]
                    except:
                        pass
                elif s.ext == u".txt":
                    try:
                        f = open(s.file,'r')
                        t = f.read()
                        f.close()
                        t = decode_text(t)
                        s.info_extra = [(_(u"N. caratteri"),len(t)),
                                        (_(u"N. parole"),len(t.split(' '))),
                                        (_(u"N. righe"),len(t.splitlines()))]
                    except:
                        pass
                try:
                    s.info_totali += s.info_extra
                except:
                    pass
                s.len_info = len(s.info_totali)
                return 1
            except Exception,e:
                traceback.print_exc()
                return 0
        elif os.path.isdir(s.file):

            s.title_text = _(u"Informazioni cartella")
            try:
                try:
                    attr_list = s.get_attr()
                    tm = time.gmtime(os.path.getmtime(s.file))
                    data = dataformatter.getdate(tm)
                    ora = dataformatter.gethour(tm)
                    try:
                        s.tot_files,s.tot_dir,s.tot_size = 0,0,0
                        #t = time.clock()
                        s.scan_dir_info(s.file)
                        #print time.clock() - t
                        #s.info_extra=[(s.file_text,str(tot_files)),(s.dirs_text,str(tot_dir)),(s.size2_text,dataformatter.sizetostr(tot_size))]
                        #tot_files,tot_dir,tot_size=0,0,0
                    except:
                        pass
                    s.info_totali = [(s.date_text,data),(s.hour_text,ora),(s.file_text,unicode(s.tot_files)),(s.dirs_text,unicode(s.tot_dir)),(s.size2_text,dataformatter.sizetostr(s.tot_size))]+attr_list
                except:
                    # s.info_totali=[(s.date_text,'-'),(s.hour_text,'-'),(s.file_text,'-'),(s.dirs_text,'-'),(s.size2_text,'-')]
                    # s.len_info=len(s.info_totali)
                    s.info_totali = [(_(u"Cartella non accessibile"),"")]
                s.len_info = len(s.info_totali)
                return 1
            except:
                return 0
    # def scan_dir_info2(s, path):
        # for d, dirs, files in gestione_file.walk(path):
            # s.tot_files += len(files)
            # s.tot_dir += len(dirs)
            # for i in files:
                # s.tot_size += os.path.getsize(os.path.join(d, i))
            
    def scan_dir_info(s, path):
        if os.path.exists(path):
            try:
                # Unavailable path, return
                names = os.listdir(path)
            except:
                return
            for child in names:
                tpath = "%s\\%s"%(path,child)
                if os.path.isdir(tpath):
                    s.tot_dir += 1
                    s.scan_dir_info(tpath)
                else:
                    s.tot_files += 1
                    s.tot_size += os.path.getsize(tpath)

    def get_op(s):
        f=codecs.open(u'Z:\\System\\BootData\\Operinfo.txt','r','utf-16')
        c=f.readlines()
        f.close()
        t=[]
        mccemcn=[]
        name=[]
        #Puliamo le linee che non servono
        for linea in c:
            if linea.startswith(u";") or linea==u'':
                pass
            else:
                t.append(linea.strip(u'\r\n'))
        #Riordiniamo le informazioni in liste
        for operator in t:
            try: a,b,c=operator.split(u',')
            except: continue
            mccemcn.append((int(a),int(b)))
            name.append(c)
        #Proviamo!
        from location import gsm_location
        x,y,f,d=gsm_location()
        try: return name[mccemcn.index((x,y))]
        except: return u"%i,%i"%(x,y) #Se non abbiamo il nome mostra solo mcc mcn

    def get_system_info(s):
        try:
            from miso import get_hal_attr
        except:
            traceback.print_exc()
            user.note(_(u"Impossibile avviare %s.\nReinstallare l'applicazione o il modulo.")%"msys")
        r = []
        info = [
                (_(u"IMEI"), "sysinfo.imei()"),
                (_(u"Batteria"), "'%i %%'%sysinfo.battery()"),
                (_(u"Frequenza cpu"), 'u"%i MHz"%(get_hal_attr(11)/1000)'),
                (_(u"Schermo"), '"%i x %i"%sysinfo.display_pixels()'),
                (_(u"Ram totale"), "dataformatter.sizetostr(sysinfo.total_ram())"),
                (_(u"Ram libera"), "dataformatter.sizetostr(sysinfo.free_ram())"),
                (_(u"Operatore"), "s.get_op()"),
                (_(u"Segnale"), "'%i %%'%sysinfo.signal_bars()"),
                (_(u"Potenza segnale"), "'%i dbm'%sysinfo.signal_dbm()"),
                (_(u"Versione Python"),"e32.pys60_version")
            ]
        for p,v in info:
            try:
                r.append((p,eval(v)))
            except:
                pass
        return r

    def esci(s):
        #del s.main,s.info_totali,s.info_extra
        if s.end_callback:
            s.end_callback()

    def bind(s):
        ui.unbindall()
        if ui.landscape==1:
            ui.bind(EScancodeLeftArrow,s.pag_su)
            ui.bind(EScancodeRightArrow,s.pag_giu)
            ui.bind(EScancodeUpArrow,s.dx)
            ui.bind(EScancodeDownArrow,s.sx)
        elif ui.landscape==2:
            ui.bind(EScancodeRightArrow,s.pag_su)
            ui.bind(EScancodeLeftArrow,s.pag_giu)
            ui.bind(EScancodeDownArrow,s.dx)
            ui.bind(EScancodeUpArrow,s.sx)
        else:
            ui.bind(EScancodeUpArrow,s.pag_su)
            ui.bind(EScancodeDownArrow,s.pag_giu)
            ui.bind(EScancodeLeftArrow,s.sx)
            ui.bind(EScancodeRightArrow,s.dx)

    def screen_change(s,at_init=0):
        if ui.landscape:
            s.max_lines=8
            #del s.main
            #s.main=Image.new(ui.landscape_size)
        else:
            s.max_lines=10
            #del s.main
        s.main=Image.new(ui.display_size)
        if not at_init:
            #Mettiamo a posto la posizione del testo (riga prima e riga ultima)
            if s.len_info>s.max_lines: s.end_line=s.first_line+s.max_lines
            elif s.len_info<=s.max_lines:
                s.first_line=0
                s.end_line=s.len_info
            if s.end_line>s.len_info:
                s.first_line=s.len_info-s.max_lines
                s.end_line=s.first_line+s.max_lines
            s.bind()
            s.info_redraw()

    def body_init(s):
        ui.save_state()
        s.screen_change()
        ui.mode_callback=s.screen_change
        if s.ext in s.advanced_menu:
            ui.menu.menu(s.advanced_menu[s.ext])
            ui.left_key=[None,_(u"Avanzate")]
        else:
            ui.menu.menu([])
            ui.left_key=[None,u""]
        ui.right_key=[s.esci,_(u"Indietro")]
        s.info_redraw()

    def pag_giu(s):
        if s.len_info>s.max_lines:
            s.first_line+=1
            s.end_line+=1
            if s.end_line>s.len_info:
                s.end_line=s.len_info
                s.first_line-=1
            s.info_redraw()

    def pag_su(s):
        if s.len_info>s.max_lines:
            s.first_line-=1
            s.end_line-=1
            if s.first_line<0:
                s.end_line=s.max_lines
                s.first_line=0
            s.info_redraw()

    def sx(s):
        if not s.x==s.min_x:
            s.x+=s.scroll_offset
            s.info_redraw()

    def dx(s):
          s.x-=s.scroll_offset
          s.info_redraw()

    def info_redraw(s):
        s.main.blit(grafica.bg_img)
        i = 1
        for prop,value in s.info_totali[s.first_line:s.end_line]:
            text=None
            try:
                if not value:
#                    s.main.text((s.x,s.y+15*(i+1)),unicode(linee[i][0]),font=settings.mainfont,fill=settings.text_color)
                    text=prop
                else:
#                    s.main.text((s.x,s.y+15*(i+1)),unicode(linee[i][0]+u": "+linee[i][1]),font=settings.mainfont,fill=settings.text_color)
                    text="%s: %s"%(prop,value)
            except:
                try:
                    #s.main.text((s.x,s.y+15*(i+1)),unicode(str(linee[i][0])+u": "+str(linee[i][1])),font=settings.mainfont,fill=settings.text_color)
                    text="%s: %s"%(str(value),str(prop))
                except:
                    continue
            s.main.text((s.x,s.y+15*i),to_unicode(text),font=settings.mainfont,fill=settings.text_color)
            i+=1
        # for i in range(len(linee)):
            # prop,value=linee[i]
            # if not type(prop) == types.StringType:
                # prop=repr(prop)
            # if not type(value) in [types.UnicodeType,types.StringType]:
                # value=repr(value)
            # if type(prop) == types.StringType:
                # prop=to_unicode(prop)
            # if type(value) == types.StringType:
                # value=to_unicode(value)
            # try:
                # if not value=="":
                    # s.main.text((s.x,s.y+15*(i+1)),u"%s: %s"%(prop,value),font=settings.mainfont,fill=settings.text_color)
                # else:
                    # s.main.text((s.x,s.y+15*(i+1)),prop,font=settings.mainfont,fill=settings.text_color)
            # except Exception,e:
                # s.main.text((s.x,s.y+15*(i+1)),unicode(e),font=settings.mainfont,fill=settings.text_color)# Exception,e:
                #print str(e)
                # try:
                    # s.main.text((s.x,s.y+15*(i+1)),unicode(str(prop)+u": "+str(value)),font=settings.mainfont,fill=settings.text_color)
                # except:
                    # pass #Exception,e: print str(e)
        text_center(s.main,13,s.title_text,settings.path_color)
        text_center(s.main,28,s.filename,settings.text_color)#def text_center(img,y1,testo, fil=(0,0,0), font=u"Default"): #Centra testo
        # try:
            # img,mas=ext_util.search(s.ext)[1]
            # s.main.blit(img,mask=mas)
        # except: pass
        if ui.landscape:
            s.main.polygon((202,14,207,14,207,162,202,162),settings.scroll_bar_bg_color1,settings.scroll_bar_bg_color2) #Sfondo barra di scorrimento
            if s.len_info>s.max_lines: #Barra di scroll laterale
                q=15+int(148.0/s.len_info*s.first_line) #5+int(177.0/len(s.file)*s.page)+9
                qp=q+int(148.0/s.len_info*s.max_lines)-1
                s.main.polygon((203,q,206,q,206,qp,203,qp),settings.scroll_bar_main_color1,settings.scroll_bar_main_color2)
        else:
            s.main.polygon((170,14,175,14,175,193,170,193),settings.scroll_bar_bg_color1,settings.scroll_bar_bg_color2) #Sfondo barra di scorrimento
            if s.len_info>s.max_lines: #Barra di scroll laterale
                q=15+int(177.0/s.len_info*s.first_line)
                qp=1+q+int(177.0/s.len_info*s.max_lines)
                s.main.polygon((171,q,174,q,174,qp,171,qp),settings.scroll_bar_main_color1,settings.scroll_bar_main_color2)
        ui.draw(s.main)

class color_init:
    def __init__(s):
        s.xc, s.yc = 0, 0
        s.black_white = 0
        s.mode=0
        s.mode_list=[_(u"Testo"),_(u"Etichette"),_(u"Titolo")]
        ui.save_state()
        ui.menu.menu([])
        ui.mode_callback = s.bind
        ui.right_key = [s.quit_color,_(u"Indietro")]
        ui.left_key = [s.cm,s.mode_list[s.mode]]
        s.bind()
        s.color_running = 1
        s.color = None
        #haha chissà cosa ci faceva questo...strana cosa!
        #appuifw.app.exit_key_handler = s.quit_color
        #s.disegna_color()
        ff00 = xrange(0xff, -1, -0x33)
        s.pal = [(r,g,b) for r in ff00 for g in ff00 for b in ff00]  # web-safe 216 colors
        s.map_j = range(0,12,2)+range(11,0,-2)  # make better grouping
        while s.color_running:
           s.black_white ^= 0x1  # toggle
           #s.clear_box(s.black_white)
           #ui.canvas_refresh()
           s.disegna_color()
           ui.canvas_refresh()
           e32.ao_sleep(0.18)
        main.restore()
    def cm(s):
        s.mode=(s.mode+1)%3
        ui.left_key=[s.cm,s.mode_list[s.mode]]
    def bind(s):
        ui.unbindall()
        ui.bind(EScancodeSelect,s.ok_color)
        ui.bind(EScancode5,s.get_rgb)
        if ui.landscape==2:
            ui.bind(EScancodeRightArrow,s.up_color)
            ui.bind(EScancodeLeftArrow,s.down_color)
            ui.bind(EScancodeDownArrow,s.right_color)
            ui.bind(EScancodeUpArrow,s.left_color)
        elif ui.landscape==1:
            ui.bind(EScancodeLeftArrow,s.up_color)
            ui.bind(EScancodeRightArrow,s.down_color)
            ui.bind(EScancodeUpArrow,s.right_color)
            ui.bind(EScancodeDownArrow,s.left_color)
        else:
            ui.bind(EScancodeUpArrow,s.up_color)
            ui.bind(EScancodeDownArrow,s.down_color)
            ui.bind(EScancodeRightArrow,s.right_color)
            ui.bind(EScancodeLeftArrow,s.left_color)
    def quit_color(s):
        s.color_running = 0
    def left_color(s):
        if s.xc > 0:
            s.xc -= 1
    def right_color(s):
        if s.xc < 17:
            s.xc += 1
    def up_color(s):
        if s.yc > 0:
            s.yc -= 1
    def down_color(s):
        if s.yc < 11:
            s.yc += 1
    def ok_color(s,clr=None):
        if clr:
            s.color=clr
        else:
            s.color = s.pal[18*s.map_j[s.yc] + s.xc]
        if s.mode==0:
            settings.text_color=s.color
        elif s.mode==1:
            settings.label_color=s.color
        elif s.mode==2:
            settings.path_color=s.color
    def get_rgb(s):
        try:
            if s.color:
                r,g,b=(appuifw.query(_(u"Inserire R,G,B del colore preferito",'text',u'%i,%i,%i')%s.color)).split(',')
            else:
                r,g,b=(appuifw.query(_(u"Inserire R,G,B del colore preferito",'text',u'%i,%i,%i')%(0,0,0))).split(',')
            r=int(r)
            g=int(g)
            b=int(b)
            for i in [r,g,b]: 
                if i>255 or i<0:
                    raise
            s.ok_color((r,g,b))
        except:
            pass
    def disegna_color(s):
        ui.canvas_image.blit(grafica.bg_img)
        if ui.landscape:
            x=20
        else:
            x=6
        if s.black_white:
            ui.canvas_image.rectangle([(9*s.xc+x, 9*s.yc+17), (9*s.xc+10+x, 9*s.yc+27)], 0)
        for j in xrange(12):
          for id in xrange(18):
            k = 18*s.map_j[j] + id
            ui.canvas_image.rectangle([(9*id+x+1, 9*j+18), (9*id+9+x, 9*j+26)], None, s.pal[k])
        if s.color:
            if ui.landscape:
                ui.canvas_image.text((2,135),_(u"Colore scelto:"),fill=settings.text_color)
                ui.canvas_image.rectangle([(1,140), (17*9+9,160)], None, s.color)  #Anteprima colore
            else:
                ui.canvas_image.text((2,140),_(u"Colore scelto:"),fill=settings.text_color)
                ui.canvas_image.rectangle([(1,145), (17*9+9,165)], None, s.color)  #Anteprima colore
        else:
                ui.canvas_image.text((2,145),_(u"Selezionare un colore per il testo!"),fill=settings.text_color)
                ui.canvas_image.text((2,158),_(u"Premere 5 per inserimento manuale"),fill=settings.text_color)

class open_with:

    def __init__(s, ext = None):
        try:
            s.pred_ext = os.path.splitext(explorer.get_file())[1]
        except:
            s.pred_ext = ext
        if not s.pred_ext:
            s.pred_ext = ".ext"
        ui.save_state()
        s.old_listbox_param = ListBox.save()
        try:
            s.tot_applicazioni = msys.listapp()
        except:
            s.tot_applicazioni = []
            user.note(_(u"Impossibile avviare %s.\nReinstallare l'applicazione o il modulo.")%"msys")
        s.view_ext()

    def app_selection(s, app_list = []):
        if not app_list:
            return
        def add():
            ext = appuifw.query(_(u"Estensione da associare"), 'text', to_unicode(s.pred_ext))
            if ext:
                id = ListBox.current()
                app = ur(application_path[id])
                settings.open_with_files.append((ur(ext.lower()),app))
                user.note(_(u"Estensione %s associata all'applicazione %s.")%(ext,application_names[id]),_(u"Apri Con"))
        def info():
            id = ListBox.current()
            user.note(_(u"Nome: %s\nUID: %s\nPercorso: %s")%(application_names[id],uids[id],application_path[id]),_(u"Apri Con"),-1)
        uids = []
        application_names = []
        application_path = []
        choose_list = []
        app_list2 = []
        for name,uid,path in app_list:
            app_list2.append((name.capitalize(),path,uid))
        app_list2.sort()
        for name,path,uid in app_list2:
            uids.append(uid)
            application_names.append(name)
            application_path.append(path)
            choose_list.append((name,u"UID: %s"%uid))
        #for i in range(0,len(application_names)):
        #    choose_list.append((application_names[i],u"UID: "+uids[i]))
        ListBox.reset()
        #ListBox.elements=[]
        if choose_list:
            for name,uid in choose_list:
                ListBox.elements.append(LType(name, uid, _(u"Seleziona l'applicazione")))
        else:
            #ListBox.elements.append(LType(name=u"",title=u"Nessuna applicazione"))
            ListBox.no_data=u"Nessuna applicazione"
        ListBox.select_item(0) #Comprende il redraw
        ui.menu.menu([(_(u"Aggiungi"),[add],u"[OK]"),(_(u"Informazioni"),[info]),(_(u"Indietro"),[s.view_ext])])
        ui.left_key=[None,_(u"Opzioni")]
        ui.right_key=[s.view_ext,_(u"Indietro")]
        ListBox.sel_cb=add
        ListBox.left_cb=s.view_ext

    def esci(s):
        ListBox.load(s.old_listbox_param)
        main.restore()

    def view_ext(s):
        #temp=[]
        def man_add():
            ext=appuifw.query(_(u"Inserire l'estensione:"),'text',to_unicode(s.pred_ext))
            if ext==None: return
            path=appuifw.query(_(u"Percorso file .app:"),'text',u"E:\\System\\Apps\\")
            if path==None: return
            path=ur(os.path.normpath(path))
            if not os.path.exists(path):
                user.note(_(u"Percorso inesistente o non valido!"),_(u"Apri con..."))
            else:
                settings.open_with_files.append((ur(ext.lower()),path))
                s.view_ext()
        def delete():
            if settings.open_with_files:
                att=settings.open_with_files[ListBox.current()]
                if user.query(_(u"Eliminare estensione associata?"),_(u"Apri con...")):
                    settings.open_with_files.remove(att)
                    s.view_ext()
        def modifica():
            if settings.open_with_files:
                i=ListBox.current()
                att=settings.open_with_files[i]
                ext=appuifw.query(_(u"Inserire l'estensione:"),'text',to_unicode(att[0]))
                if not ext: return
                settings.open_with_files.remove(att)
                settings.open_with_files.append((ur(ext.lower()),att[1]))
                #settings.open_with_files[i][0]=ext.lower()
                s.view_ext()
        ListBox.reset()
        ui.bind(EScancodeBackspace, delete)
        #ListBox.elements=[]
        if settings.open_with_files:
            for ext,name in settings.open_with_files:
                #temp.append((unicode(i[0]),(unicode(i[1]))))
                try:
                    icona=crea_icone(name[:-3]+"aif")[0:2]
                except:# Exception,e:
                    #print str(e)
                    icona=ext_util.search(ext)[1]
#                ListBox.elements.append(LType(name=unicode(name),undername=unicode(ext),title=u"Apri con...",icon=ext_util.search(ext)[1]))
                ListBox.elements.append(LType(to_unicode(os.path.split(name)[1]), to_unicode(ext), _(u"Apri con..."), icona))
        else:
            ListBox.elements.append(LType(_(u"Elenco vuoto"), _(u"Premere opzioni!"), _(u"Apri con...")))
        #ListBox.elements=temp
        #ListBox.redraw_list()
        #if len(temp)==0: temp=[(u"Elenco vuoto",u"Premere opzioni!")]
        #appuifw.app.title=unicode(open_with_text)
        #appuifw.app.screen="normal"
        ui.menu.menu([(_(u"Aggiungi"),[lambda: s.app_selection(s.tot_applicazioni)]),(_(u"Aggiungi manualmente"),[man_add]),(_(u"Elimina"),[delete],u"[C]"),(_(u"Modifica"),[modifica],u"[OK]"),(_(u"Indietro"),[s.esci])])
        ui.left_key=[None,_(u"Opzioni")]
        ui.right_key=[s.esci,_(u"Indietro")]
        ListBox.left_cb=s.esci
        ListBox.right_cb=lambda: s.app_selection(s.tot_applicazioni)
        ListBox.sel_cb=modifica
        ListBox.select_item(0) #Comprende il redraw
        # list_box=appuifw.Listbox(temp)
        # appuifw.app.body=list_box
        # list_box.bind(8,delete)

class _DriveManager:

    def __init__(s):
        s.folder = None
        try:
            import miso
            s.miso = miso
        except:
            user.note(_(u"Impossibile avviare %s.\nReinstallare l'applicazione o il modulo.")%"miso")
        try:
            s.folder = to_unicode(explorer.dir)
#            if not os.path.isdir(s.folder):
#                s.folder = None
        except:
            pass
        s.last_ui = ui.get_state()
        s.view_ext()

    def esci(s):
        main.restore(None, s.last_ui, 1)

    def view_ext(s, errcode = None, item = None):

        def add(p = None, n = None):
            if p!=None:
                path = p
            else:
                path = appuifw.query(_(u"Inserire il percorso:"), 'text', s.folder)
                if path==None:
                    return
            if not n:
                n = ListBox.current()

            path = os.path.normpath(path)

            if (not p) and (not os.path.exists(path)):
                user.note(_(u"Percorso inesistente o non valido!"),_(u"Virtualizzazione unità"))
            else:
                r = sys_tools.create_drive_subst(path, n)
                s.view_ext(r, n)
        
        def delete_all():
        
            if user.query(_(u"Cancellare veramente tutte le associazioni?"), _(u"Virtualizzazione unità")):
                for i in xrange(0, 26):
                    sys_tools.create_drive_subst(u"", i)
                    s.view_ext(1, i)

        ListBox.reset()

        drives = e32.drive_list()

        for i in xrange(0, 26):#len(drives)+1):
            p = s.miso.get_subst_path(i)
            if p:
                if (errcode==0) and (i == item):
                    desc = _(u"Errore configurazione!")
                else:
                    desc = p
                #t = LType(u"Unità %s:\\"%unichr(i+65), p, _(u"Virtualizzazione unità"))
            else:
                if (errcode==0) and (i == item):
                    desc = _(u"Errore configurazione!")
                else:
                    desc = _(u"Non configurata")
            t = LType(u"Unità %s:\\"%unichr(i+65), desc, _(u"Virtualizzazione unità"))
            ListBox.elements.append(t)

        ui.menu.menu([(_(u"Aggiungi - Modifica"), [add], u"[OK]"),
                      (_(u"Elimina"),[lambda: add(u"")], u"[C]"),
                      (_(u"Elimina tutto"),[delete_all]),
                      (_(u"Indietro"),[s.esci])])
        ui.bind(EScancodeBackspace, lambda: add(u""))
        ui.left_key = [None, _(u"Opzioni")]
        ui.right_key = [s.esci, _(u"Indietro")]
        ListBox.sel_cb = add
        ListBox.select_item(item)

class gestore_temi:
#Theme manager
    def __init__(s,end_callback=None,no_load=0):
        s.standalone=no_load
        if no_load: return
        s.skin_props=[]
        s.temi_ricevuti=[]
        s.themes_list=[]
        s.old_listbox_param=ListBox.save()
        ui.save_state()
        if end_callback:
            s.end_callback=end_callback
        else:
            s.end_callback=main.restore
        # f=open("D:/theme_report.txt","w")
        # f.write(repr(s.skin_props))
        # f.close()
        s.get_skins()
        s.list_init()
        s.body_init()
    def GetListOfSkin(s,dire,ext=["theme_prop.ini","ui.zip","icons.zip"]):
        #skin_names=[]
        skin_path=[]
        total=0
        files=os.listdir(dire)
        for f in files:
            path="%s\\%s"%(dire,f)#dire+"\\"+f
            if os.path.isdir(path):
                c=os.listdir(path)
                c=map(lambda x: x.lower(),c)
                if ext[0] in c and ext[1] in c and ext[2] in c:
                    skin_path.append(path)
                    total+=1
        return total,skin_path
    def get_skins(s):
        s.skin_props=[]
        s.total_skin,skin_dirs=s.GetListOfSkin(directory.allskin_dir)
        for skin in skin_dirs:
            try:
                s.skin_props.append((s.theme_prop_reader("%s\\theme_prop.ini"%skin),skin)) #Memorizziamo le proprietà del tema
            except Exception,e:
                print str(e)
                s.total_skin-=1
    def theme_prop_reader(s,file):
        f=codecs.open(file,"r","latin1")
        t=f.read()
        f.close()
        temp=[]
        for i in t.splitlines():
            if i.startswith(";"):
                temp.append(i.split(";")[1].split(":"))
               # pass
            #else:
                #a=i.split(";")[1]
                #temp.append((a.split(":")[0], i.split(";")[1].split(":")[1]))
        return dict(temp)
    def list_init(s):
        s.themes_list=[]
        uii, ico = settings.skin[0],settings.skin[1]
        for i in s.skin_props:
                skinname=os.path.split(i[1])[1]
                try:
                    name=i[0][u"Nome"]
                    mode=u""
                    if uii == ico == skinname:
                        mode=u"(Attivo)"
                    elif skinname == uii:
                        mode=u"(Attivo: sfondi)"
                    elif skinname == ico:
                        mode=u"(Attivo: icone)"

                    s.themes_list.append(LType(u"%s %s"%(name,mode), i[0][u"Autore"], i[0][u"Descrizione"]))
                except:
                    s.themes_list.append(LType(_(u"Tema difettoso"), _(u"Controllare tema"), _(u"Tema difettoso")))#s.themes_list.append(LType(name=i[0][u"Nome"],undername=i[0][u"Autore"],title=u"Tema invalido"))
    def refresh(s):
        s.get_skins()
        s.list_init()
        ListBox.elements=s.themes_list[:]
        ListBox.select_item(0)
    def info(s):
        index=ListBox.current()
        skin_name=s.skin_props[index][0][u"Nome"]
        skin_autor=s.skin_props[index][0][u"Autore"]
        skin_info=s.skin_props[index][0][u"Descrizione"]
        testo=_(u"Nome: %s\r\nAutore: %s\r\nDescrizione: %s\r\n")%(skin_name,skin_autor,skin_info)
        try:
            f = open("%s\\info.txt"%(s.skin_props[index][1]),"r")
            text = f.read()
            f.close()
            text=decode_text(text)
            testo+=_(u"Altre informazioni:\r\n%s")%text
        except: pass# Exception, e: print str(e)
        text_viewer(text=testo,end_callback=s.body_init,title=_(u"Dettagli tema"))
    def exit(s):
        # if s.caricando==1:
            # appuifw.note(u"Un tema si sta già caricando...attendere il ritorno al programma!")
            # return
        ListBox.load(s.old_listbox_param)
        try: s.end_callback()
        except: return
        explorer.view_refresh()
    def body_init(s,n=0,old_body=None):
        if old_body: ui.set_state(old_body)
        ListBox.reset()
        ListBox.elements=s.themes_list[:]
        ui.right_key=[s.exit,_(u"Indietro")]
        ui.left_key=[None,_(u"Opzioni")]
        ui.menu.menu([(_(u"Applica tema!"),[s.selection_callback],u"[OK]"),
                    (_(u"Anteprima"),[s.preview]),
                    (_(u"Informazioni"),[s.info],u"[5]"),
                    (_(u"Gestione"),[(_(u"Installa"),s.install),
                                  (_(u"Disinstalla"),s.uninstall),
                                  (_(u"Salva o invia"),s.create_installer)
                                 ]),
                    (_(u"Extra"),[(_(u"Colori da tema"),s.get_colors),
                              (_(u"Icone da tema"),lambda: s.parts(ic=1)),
                              (_(u"Sfondi da tema"),lambda: s.parts(ui=1))
                              ]),
                    (_(u"Indietro"),[s.exit])
                    ])
        ui.bind(EScancode5, s.info)
        ListBox.left_cb=s.exit
        ListBox.sel_cb=s.selection_callback
        ListBox.select_item(n) #Comprende il redraw
    def create_installer(s):
        if not user.query(_(u"Creare l'installazione per il tema selezionato?\nSarà poi possibile inviarlo ad un dispositivo."),_(u"Gestore temi")):
            return
        user.direct_note(_(u"Creazione installazione in corso..."))
        index=ListBox.current()
        path=to_unicode(s.skin_props[index][1])
        skin_name=s.skin_props[index][0][u"Nome"]
        skin_autor=s.skin_props[index][0][u"Autore"]
        import zipfile
        to=u"%s:\\%s_by_%s.zip"%(directory.disk,skin_name,skin_autor)
        zout = zipfile.ZipFile(to,"w",zipfile.ZIP_DEFLATED)
        for fname in os.listdir(path):
            zout.write(os.path.join(ur(path),ur(fname)),fname)
        zout.close()
        user.note(_(u"Installazione tema correttamente creata in %s:\\!")%directory.disk,_(u"Gestore temi"))
        if user.query(_(u"Inviare tramite bluetooth?"),_(u"Gestore temi")):
            gestione_file.invia([ur(to)])
    def install(s):
        s.temi_ricevuti=[]
        user.direct_note(_(u"Scansione temi da installare in corso...\nIl processo potrebbe richiedere qualche minuto."),_(u"Attendere"))
        for path in ["C:\\System\\Mail","E:\\System\\Mail","C:","E:"]:
            try: s.walktree(path)
            except: pass
        if not s.temi_ricevuti:
            user.note(_(u"Nessun tema trovato nei file ricevuti o nelle directory radice delle unità.\nIl tema deve essere un archivio .zip contentente:\n-theme_prop.ini\n-UI.zip\n-ICONS.zip"),
                      _(u"Scansione completata"),-1)
        else:
            user.note(_(u"Trovati %i temi da installare")%len(s.temi_ricevuti),
                      _(u"Scansione completata"))
            l=[]
            for i in s.temi_ricevuti:
                l.append(ru(os.path.split(i)[1][:-4]))
            i=appuifw.popup_menu(l,_(u"Tema da installare:"))
            if i!=None:
                try:
                    user.direct_note(_(u"Installazione tema in corso..."),_(u"Attendere"))
                    destination=directory.allskin_dir+"\\"+(os.path.split(s.temi_ricevuti[i])[1][:-4])
                    
                    directory.create(destination)
                    
                    unzip().extract(s.temi_ricevuti[i],destination)
                    s.total_skin,skin_dirs=s.GetListOfSkin(directory.allskin_dir)
                    for skin in skin_dirs:
                        try: s.skin_props.append((s.theme_prop_reader(skin+"\\theme_prop.ini"),skin)) #Memorizziamo le proprietà del tema
                        except Exception,e:
                            print str(e)
                            s.total_skin-=1
                    #s.list_init()
                    #ListBox.select_item(0)
                    try:
                        if not s.standalone: s.refresh()
                    except: pass
                    user.note(_(u"Tema installato correttamente!"),l[i])
                except:
                    user.note(_(u"Errore nell'istallazione del tema!\nLa memoria potrebbe essere piena o il tema è danneggiato o in un formato zip non supportato."),_(u"Errore: %s"%(l[i])))
    def walktree(s,dir):
        for f in os.listdir(dir):
            try :
                pathname = '%s\\%s' % (dir, f)
                if os.path.isdir(pathname) and (not dir in ["C:","E:"]):
                    s.walktree(pathname)
                else:
                    if (os.path.splitext(pathname)[1]).lower()==".zip":
                        if zipfile.is_zipfile(pathname):
                            try:
                                z=zipfile.ZipFile(pathname)
                                l=map(lambda x: x.lower(),z.namelist())
                                z.close()
                                del z
                            except: continue
                            if ("theme_prop.ini" in l) and ("ui.zip" in l) and ("icons.zip" in l):
                                s.temi_ricevuti.append(pathname)
            except : pass
    def uninstall(s):
        index=ListBox.current()
        skinname=os.path.split(s.skin_props[index][1])[1]
        if (skinname in settings.skin) or len(s.skin_props)==1:
            user.note(_(u"Impossibile eliminare!\nTema in uso, parzialmente in uso o unico."),_(u"Eliminazione Tema"))
            return
        else:
            if user.query(_(u"Si è sicuri di cancellare il tema %s definitivamente?")%(s.skin_props[index][0][u"Nome"]),_(u"Conferma eliminazione"),left=_(u"Disinstalla!")):
                e32.ao_sleep(0.1)
                user.direct_note(_(u"Disinstallazione tema in corso..."),_(u"Disinstallazione"))
                gestione_file.removedir(s.skin_props[index][1])
                s.refresh()
    def preview(s):
        index=ListBox.current()
        path=s.skin_props[index][1]
        prev=ui.get_state()
        user.direct_note(_(u"Caricamento anteprima..."))
        # z=ziptools.unzip().extract(path+"\\ui.zip","D:\\winfile_preview")
        # z=ziptools.unzip().extract(path+"\\icons.zip","D:\\winfile_preview")
        try:
            if ui.landscape:
                ui.draw(Image.open(path+"\\preview_LS.png"))
            else:
                ui.draw(Image.open(path+"\\preview.png"))
        except:
            user.note(_(u"Nessun anteprima disponibile.\nAssicurarsi che nella cartella del tema ci sia il file preview.png"))
            return
        ui.reset_ui()
        #ui.canvas_image.clear()
        # if ui.landscape:
            # ui.canvas_image.blit(Image.open("D:\\winfile_preview\\sfondo_LS.jpg"))
            # ui.canvas_image.blit(Image.open("D:\\winfile_preview\\selezione_LS.jpg"),mask=Image.open("D:\\winfile_preview\\selezione_mask_LS.bmp"),target=(0,13))
        # else:
            # ui.canvas_image.blit(Image.open("D:\\winfile_preview\\Sfondo.jpg"))
            # ui.canvas_image.blit(Image.open("D:\\winfile_preview\\selezione_LS.jpg"),mask=Image.open("D:\\winfile_preview\\selezione_mask.bmp"),target=(0,13))
        #ui.canvas_refresh()
        lc=e32.Ao_lock()
        e32.ao_sleep(0.5)
        ui.key_callback=lambda k: lc.signal()
        lc.wait()
        ui.set_state(prev)
        ListBox.select_item(index)
        #ui.canvas_refresh()
        del prev
    def selection_callback(s,skin=None): #Applica tema
        # if s.caricando==1: 
            # appuifw.note(u"Un tema si sta già caricando...attendere il ritorno al programma!")
            # return
        if not skin:
            index=ListBox.current()
            settings.skin=[os.path.split(s.skin_props[index][1])[1],os.path.split(s.skin_props[index][1])[1]]
        else:
            settings.skin=skin #! Array [0,1]
        #appuifw.note(u"Caricamento skin in corso...")
        user.direct_note(_(u"Caricamento tema in corso.\nAttendere..."),_(u"Temi"))
        #s.caricando=1
        try:
            #Before loading another theme, it'll clean everything!
            gestione_file.removedir(directory.skin_dir, 0)
        except:
            pass
        try:
            grafica.load(1) #Image extraction and loading
            grafica.screen_change() #Screen adaptations
            ext_util.reload() #Icon cache reloading
        except Exception,error:
            user.note(_(u"Errore nel caricamento della grafica!\nAssicurarsi che abbia tutti i file necessari.\nDettagli errore: %s")%unicode(error),_(u"Errore tema"),-1)
        try:
            s.get_settings(s.skin_props[index][0])
        except Exception,error:
            user.note(_(u"Errore nel caricamento dei colori!\nColore mancante nel file ini: %s")%unicode(error),_(u"Errore"),-1)
        ListBox.select_item(index)
    def get_colors(s):
        index=ListBox.current()
        try:
            s.get_settings(s.skin_props[index][0])
        except:
            appuifw.note(u'Error loading theme colors!')
        ListBox.select_item(index)
    def parts(s,ui=0,ic=0):
        index=ListBox.current()
        s=os.path.split(s.skin_props[index][1])[1]
        if ui: settings.skin[0]=s
        if ic: settings.skin[1]=s
        try:
            grafica.load(1)
            ext_util.reload()
        except: appuifw.note(u'Error loading theme graphics!')
        ListBox.select_item(index)
    def read_settings(s,fn):
        
        # f=codecs.open(fn,"r","latin1")
        # linee=f.readlines()
        # f.close()
        # temp=[]
        # for i in linee:
            # if not i.startswith(";"): pass
            # else: temp.append((i.split(";")[1].split(":")[0].replace("\r\n","").replace("\n",""),
                              # i.split(";")[1].split(":")[1].replace("\r\n","").replace("\n","")))
        # temp=dict(temp)
        try:
            s.get_settings(s.theme_prop_reader(fn))
        except:
            pass
        #del temp,linee,i
    def get_settings(s,temp):
        settings.text_color=eval(temp[u"text_color"])
        settings.label_color=eval(temp[u"label_color"])
        settings.path_color=eval(temp[u"path_color"])
        settings.playerbar_color1=eval(temp[u"grafical_bar_color1"])
        settings.playerbar_color2=eval(temp[u"grafical_bar_color2"])
        settings.scroll_bar_bg_color1=eval(temp[u"scroll_bar_bg_color1"])
        settings.scroll_bar_bg_color2=eval(temp[u"scroll_bar_bg_color2"])
        settings.scroll_bar_main_color1=eval(temp[u"scroll_bar_main_color1"])
        settings.scroll_bar_main_color2=eval(temp[u"scroll_bar_main_color2"])
        settings.progress_bar_bg_color1=eval(temp[u"progress_bar_bg_color1"])
        settings.progress_bar_bg_color2=eval(temp[u"progress_bar_bg_color2"])
        settings.progress_bar_color1=eval(temp[u"progress_bar_color1"])
        settings.progress_bar_color2=eval(temp[u"progress_bar_color2"])
        settings.window_border=eval(temp[u"window_border"])
        settings.lyrics_color=eval(temp[u"lyrics_color"])

class _settings:
    def __init__(s):
        s.etichetta_utente=u"WinFile"
        s.right_up_dir=0
        #s.posta="File ricevuti"
        s.mainfont=(None,None,None,)#(u"Nokia Sans S60",None,None) #font,size,flag
        s.label_font=(None, 14, 16,) #bold
#define FONT_BOLD 1
#define FONT_ITALIC 2
#define FONT_SUBSCRIPT 4
#define FONT_SUPERSCRIPT 8
#define FONT_ANTIALIAS 16
#define FONT_NO_ANTIALIAS 32
        s.null=None
        #s.path_font=None
        #s.label_font=None
        #s.fontlist=[u"Default"]
        #s.fontlist=s.fontlist+appuifw.available_fonts()
        s.search_string=u"*.*"
        s.preview_switch=1
        s.open_with_files=[] #Array contenente estenzione e app da eseguire....[(.mp3,E:\..\LcgJukebox.app)]
        s.save_path=1
        s.text_color=(0,0,0) #Testo
        s.label_color=(0,0,0) #Etichette softkey
        s.path_color=(0,0,0) #Titolo
        s.playerbar_color1,s.playerbar_color2=(90,160,229),(90,160,229) #barra player
        s.scroll_bar_bg_color1,s.scroll_bar_bg_color2=(255,255,255),(200,200,200) #Sfondo barra di scorrimento
        s.scroll_bar_main_color1,s.scroll_bar_main_color2=(80,80,80),(80,80,80)
        s.progress_bar_bg_color1,s.progress_bar_bg_color2=(192,192,192),(255,255,255)
        s.progress_bar_color1,s.progress_bar_color2=(0,0,0),(10,125,254)
        s.window_border=s.text_color #Bordo finestre e menu; se non è specificato nel tema, mettiamo il colore del testo
        s.lyrics_color=s.text_color
        s.get_size_on_canvas=1
        s.volume=2
        s.audio_repeat=0
        s.audio_shuffle=0
        s.text_viewer_search_string=u""
        s.text_viewer_view_mode=0
        s.text_viewer_history={}
        s.skin=["Cobalt","Cobalt"]
        s.lang_list=["Italiano"]
        s.lang=s.lang_list[0]
        # s.lang_list=[u"Italiano",u"English",u"Deutsch"]
        # s.code_list=["it","en","de"]
        s.delete_temp=0
        # If true, popup a query while trying to exit
        s.ask_before_exit = 1
        s.to_save=["s.skin","s.null","s.etichetta_utente","s.right_up_dir","s.get_size_on_canvas",
                  "s.search_string","s.preview_switch","s.save_path","s.open_with_files","s.text_viewer_view_mode",
                  "s.text_viewer_search_string",
                  "s.audio_repeat","s.audio_shuffle","s.volume","s.lang","s.delete_temp",
                  "s.sort_files_by","s.sort_dirs_by","s.sort_mode","s.show_hidden_tasks","s.ask_before_exit"]
        s.color_to_save=["s.text_color",
                    "s.label_color","s.path_color",
                    "s.playerbar_color1","s.playerbar_color2",
                    "s.scroll_bar_bg_color1","s.scroll_bar_bg_color2",
                    "s.scroll_bar_main_color1","s.scroll_bar_main_color2",
                    "s.progress_bar_bg_color1","s.progress_bar_bg_color2",
                    "s.progress_bar_color1","s.progress_bar_color2",
                    "s.lyrics_color","s.window_border"]
        s.SORT_BY_NAME=0
        s.SORT_BY_SIZE=1
        s.SORT_BY_DATE=2
        s.SORT_BY_TYPE=3
        s.SORT_BY_NONE=4
        s.SORT_DIRS_FIRST=0
        s.SORT_DIRS_LAST=1
        s.SORT_DIRS_ANY=2
        s.SORT_ASCENDING=0
        s.SORT_DESCENDING=1
        # Sort by name - dirs first - ascending by default setting
        s.sort_files_by=s.SORT_BY_NAME
        s.sort_dirs_by=s.SORT_DIRS_FIRST 
        s.sort_mode=s.SORT_ASCENDING
        #s.time_zone=0
        s.show_hidden_tasks = 1
        # 0 only in some situation like settings reset...
        s.save_settings_at_exit = 1

    def language_scan(s):
        s.lang_list=["Italiano"]
        for i in os.listdir(directory.lang_dir):
            if i[-3:] in ["lng","ini"]:
                s.lang_list.append(i)

    def set(s,n,v):
        if v=="switch":
            vo=eval("s.%s"%n)
            if vo:
                exec("s.%s=0"%n)
            else:
                exec("s.%s=1"%n)
        else:
            exec("s.%s=%s"%(n,v))

    def salvataggio(s,dati):
        #appuifw.note(u"Impostazioni cambiate","conf")
        s.salvato = 1

    def impostazioni(s):
        appuifw.app.screen="normal"
        #nu=["esci","dirsuperiore"]
        appuifw.app.title=_(u"Preferenze generali")
        azioni_list=[_(u"Uscita"),_(u"Dir. superiore")]
        anteprima_list=[_(u"Da tema, più veloce"),_(u"Anteprima, meno veloce")]
        on_off_general_list=[_(u"No"),_(u"Sì")]
        # try:
            # index_font=fontlist.index(settings.mainfont)
        # except:
            # index_font=0
        try:
            s.language_scan()
        except:
            print "No language files/dir found or error. Check language files."
        try:
            la = s.lang_list.index(s.lang)
        except:
            la = 0
        dati = [
            (_(u"Lingua"), 'combo', (map(to_unicode, s.lang_list),la)),
            (_(u"Tasto destro"),'combo', (azioni_list,int(s.right_up_dir))),
            #(_(u"Icona immagini e video"),  'combo', (anteprima_list,int(s.preview_switch))),
            (_(u"Chiedi conferma prima di uscire"),'combo',  (on_off_general_list, int(s.ask_before_exit))),
            (_(u"Visualizza dimensione file"),  'combo', (on_off_general_list,int(s.get_size_on_canvas))),
            (_(u"Etichetta tasto sinistro"),'text', s.etichetta_utente),
            (_(u"Salva sessione"),'combo',  (on_off_general_list, int(s.save_path))),
            (_(u"Canc. tema in ram alla chiusura"),'combo',  (on_off_general_list, int(s.delete_temp)))
           # (unicode(setting4_text),'text', unicode(posta)),
           # (u"Font",  'combo', (fontlist,index_font)),
           # 
            #(u"Lingua",'combo',(lang_list,lang_att))
           ]
        flags = appuifw.FFormEditModeOnly+appuifw.FFormDoubleSpaced
        fff = appuifw.Form(dati, flags)
        fff.save_hook = s.salvataggio
        s.salvato = 0
        fff.execute()
        if s.salvato:
        # 0 posizione della barra dall'alto
            s.lang = s.lang_list[fff[0][2][1]]
            s.right_up_dir = fff[1] [2][1]
            s.ask_before_exit = fff[2] [2][1] #Boleano
            s.get_size_on_canvas = fff[3] [2][1] #Boleano
            s.etichetta_utente  = fff[4][2]
            s.save_path  = fff[5][2][1]
            s.delete_temp = fff[6][2][1]
            s.load_lang()
            main.menu_init()
            main.set_softkeys()
            explorer.view_refresh()
        # mainfont = fontlist[fff[5] [2][1]]
        # save_path = fff[6] [2][1]
        # if save_path==0: save_path=1
        # else: save_path=0
        
        # lang1 = code_list[fff[7] [2][1]]
        # if lang1==lang: pass
        # else:
         # lang=lang1
         # resource_loader().load_language()
         # menu_init()
        appuifw.app.screen="full"

    def explorer_settings(s):
        on_off_general_list=[_(u"No"),_(u"Sì")]
        appuifw.app.screen="normal"
        appuifw.app.title=_(u"Gestione filesystem")
        dati = [
            (_(u"Ordina per"),'combo', ([_(u"Nome"),_(u"Dimensione"),_(u"Data"),_(u"Tipo"),_(u"Nessun ordinamento")],int(s.sort_files_by))),
            (_(u"Regole"), 'combo', ([_(u"Crescente"),_(u"Decrescente")],int(s.sort_mode))),
            (_(u"Ordine cartelle"), 'combo', ([_(u"Inizio"),_(u"Fine"),_(u"Nessun ordinamento")],int(s.sort_dirs_by))),
            #(_(u"Fuso orario locale"), 'number', s.time_zone),
            (_(u"Visualizza task nascosti"), 'combo', (on_off_general_list, int(s.show_hidden_tasks)))
            ]
        flags = appuifw.FFormEditModeOnly + appuifw.FFormDoubleSpaced
        fff = appuifw.Form(dati, flags)
        fff.save_hook = s.salvataggio
        s.salvato = 0
        fff.execute()
        if s.salvato:
            s.sort_files_by = fff[0] [2][1]
            s.sort_mode = fff[1] [2][1]
            s.sort_dirs_by = fff[2][2][1]
            #s.time_zone  = fff[3][2]
            s.show_hidden_tasks  = fff[3][2]
            #dataformatter.time_zone = s.time_zone
            explorer.view_refresh()
        appuifw.app.screen="full"

    def load_lang(s):
        try:
            if s.lang!=s.lang_list[0]:
                return _.load("%s\\%s"%(directory.lang_dir,s.lang))
            else:
                _.clean()
                print "Default language set"
        except:
            traceback.print_exc()
            return 0

    def save_to_disk(s):
        import marshal
        if not os.path.exists(directory.data_dir):
            os.makedirs(directory.data_dir)
        data=[]
        to_save=map(eval,s.to_save)
        data=marshal.dumps(to_save)
        try:
            c=open(directory.settings_file,"wb")
            c.write(data)
            c.close()
        except:
            #appuifw.note(u"Settings.dat write error!",'error')
            print "Settings.dat write error!"
        del data,to_save

    def load_settings(s):
        import marshal
        if not os.path.exists(directory.settings_file):
            return
        try:
            c=open(directory.settings_file,"rb")
            data=marshal.load(c)
            c.close()
        except:
            appuifw.note(u"Settings.dat read error!",'error')
        try:
            
            for i in xrange(len(s.to_save)):
                exec(s.to_save[i]+"="+repr(data[i]))
        except:
            #appuifw.note(u"Settings.dat load error!\nStrange values, maybe due to version up(down)grade.","error")
            print "Settings.dat load error!\nStrange values, maybe due to version up(down)grade."
    def save_colors(s):
        import marshal
        if not os.path.exists(directory.data_dir): os.makedirs(directory.data_dir)
        data=[]
        to_save=map(eval,s.color_to_save)
        data=marshal.dumps(to_save)
        try:
            c=open(directory.theme_file,"wb")
            c.write(data)
            c.close()
        except:
            #appuifw.note(u"Theme.dat write error!",'error')
            print "Theme.dat write error!"
        del data,to_save
    def load_colors(s):
        import marshal
        if not os.path.exists(directory.theme_file):
            #Se i colori non sono stati cambiati dall'utente o non esiste il file, carichiamoli dall'ini!
            g=gestore_temi(no_load=1)
            try:
                g.read_settings("%s\\%s\\theme_prop.ini"%(directory.allskin_dir,s.skin[0]))
            except:
               pass
            del g
            return
        try:
            c=open(directory.theme_file,"rb")
            data=marshal.load(c)
            c.close()
        except:
            #appuifw.note(u"Theme.dat read error!",'error')
            print "Theme.dat read error!"
        try:
            for i in xrange(len(s.color_to_save)):
                exec(s.color_to_save[i]+"="+repr(data[i]))
        except:
            #appuifw.note(u"Theme colors load error!","error")
            print "Theme colors load error!"
    def save_session(s):
        import marshal
        if not os.path.exists(directory.data_dir):
            os.makedirs(directory.data_dir)
        if not settings.save_path:
            try: os.remove(directory.session_file) #Se non è attiva l'impostazione, semplicemente cancelliamo il file se c'è
            except: pass
            return
        try:
            #Qui mettiamo un try perché non è sicuro che si possa avere un nome (magari la lista è vuota...)
            name=(ListBox.elements[ListBox.current()]).name
        except:
            name=u""
        data=marshal.dumps([explorer.dir,name])
        try:
            c=open(directory.session_file,"wb")
            c.write(data)
            c.close()
        except:
            #appuifw.note(u"Session.bin write error!",'error')
            print "Session.bin write error!"
    def load_session(s):
        if os.path.exists(directory.session_file) and settings.save_path:
            import marshal
            try:
                c=open(directory.session_file,"rb")
                data=marshal.load(c)
                c.close()
                return data
            except:
                #appuifw.note(u"Sesssion.bin read error!",'error')
                print "Sesssion.bin read error!"
        #if len(s.to_save)!=len(data): appuifw.note(u"Settings are damaged or old.")
    def reset(s):
        if not user.query(_(u"Cancellare tutti i file di impostazione?\nIl processo ripristinerà WinFile e le sue impostazioni originali."), _(u"Impostazioni"), _(u"Reimposta!")):
            return
        # don't save settings at exit
        s.save_settings_at_exit = 0
        # delete every skin temp file
        s.delete_temp = 1
        fn = [directory.settings_file,
            directory.theme_file,
            directory.session_file,
            directory.first_boot_file]
        for f in fn:
            try:
                os.remove(f)
            except:
                pass
        print "WinFile settings cleaned!"
        if user.query(_(u"Le impostazioni e i file relativi sono state cancellate!\nChiudere ora WinFile?\nNOTA: ogni ulteriore modifica alle impostazioni ora non andrà salvata!"), _(u"Impostazioni"), _(u"Chiudi")):
            main.quit()
        # wf=["theme.dat","settings.dat","session.bin"]
        # if reset_all: delete(datadir)
        # else delete(wf)

class _grafica:
    def __init__(s, size):
        s.screen_size = size
    def boot(s):
        try:
            s.load()
        except:
            try:
                #Qui potrebbe essere solo un problema della directory "temporanea"
                s.load(1)
            except:
                #Il tema è di sicuro danneggiato, verifichiamo se ce ne sono altri, altrimenti l'applicazione avvisa e si chiude
                try:
                    os.remove(directory.theme_file)
                    #print "theme.dat eliminato"
                except:
                    pass
                try:
                    for path in os.listdir(directory.allskin_dir):
                        try:
                            l=os.listdir(directory.allskin_dir+"\\"+path)
                            l=map(lambda x: x.lower(),l)
                        except: continue
                        if ("ui.zip" in l) and ("icons.zip" in l) and ("theme_prop.ini" in l):
                            settings.skin=[path,path]
                            break
                    s.load(1)
                except:
                    appuifw.note(u"Nessun tema!\nNo themes!\nKeine Themen!")
                    appuifw.note(u"Installarne uno!\nInstall one!\nBitte eine installieren!")
                    #appuifw.note(u"Low Memory on D:? Try to restart!")
                    g=gestore_temi(no_load=1)
                    g.install()
                    try:
                        for path in os.listdir(directory.allskin_dir):
                            try:
                                l=os.listdir(directory.allskin_dir+"\\"+path)
                                l=map(lambda x: x.lower(),l)
                            except: continue
                            if ("ui.zip" in l) and ("icons.zip" in l) and ("theme_prop.ini" in l):
                                settings.skin=[path,path]
                                break
                        s.load(1)
                    except:# Exception,e:
                        #print str(e)
                        #print settings.skin
                        settings.path_color=0xff0000
                        user.note(u"Impossibile avviare il programma.\nNessun tema è installato o disponibile per l'utilizzo.\nOppure una o più memorie (utente, D: o ram) sono piene.\nProvare a riavviare il telefono.",u"Fatal Error",-1)
                        sys.exit()
                    del g
                    #appuifw.app.set_exit()
    def load(s,force=0):
        if (not os.path.exists(directory.skin_dir)) or force:
            #print "Lettura file zip"
            unzip().extract("%s\\%s\\ICONS.zip"%(directory.allskin_dir,settings.skin[1]),directory.skin_dir)
            #print "Icone estratte"
            #user.direct_note(u"Icone estratte",u"Caricamento...")
            unzip().extract("%s\\%s\\UI.zip"%(directory.allskin_dir,settings.skin[0]),directory.skin_dir)
            #user.direct_note(u"UI estratto",u"Caricamento...")
            #print "UI estratto"
            #d=progress_dialog(u"Caricamento tema...",u"Avviamento WinFile",max=48)
            #d.draw()
        # for i in s.theme_files:
            # exec("""%s=Image.open("%s")"""%(var,path))
        # return
        # for var,path in [("s.spuntoimg","spunto.png"),
                        # ("s.appimg","Application.png"),
                        # ("s.file_img","File.png"),
                        # ("s.bg_img_normal","Sfondo.jpg"),
                        # ("s.bg_img_landscape","Sfondo_LS.jpg"),
                        # ("s.csel_img_normal","selezione.jpg"),
                        # ("s.csel_img_landscape","selezione_LS.jpg"),
                        # ("s.csel_img_mask_normal","selezione_mask.bmp"),
                        # ("s.csel_img_mask_landscape","selezione_mask_LS.bmp"),
                        # ("s.cartella_img","Cartella.png"),
                        # ("s.dll_img","dll.png"),
                        # ("s.ingranaggio_img","ingranaggio.png"),
                        # ("s.internet_img","internet.png"),
                        # ("s.mmc_img","mmcmemory.png"),
                        # ("s.tel_img","telmemory.png"),
                        # ("s.musica_img","musica.png"),
                        # ("s.mail_img","Mail.png"),
                        # ("s.ram_img","rammemory.png"),
                        # ("s.rom_img","rommemory.png"),
                        # ("s.video_img","video.png"),
                        # ("s.immagine_img","immagine.png"),
                        # ("s.settings_img","settings.png"),
                        # ("s.archive_img","Archivio.png"),
                        # ("s.vcf_img","Vcf.png"),
                        # ("s.sis_img","Sis_installer.png"),
                        # ("s.text_img","testo.png"),
                        # ("s.pycon_img","Python.png")]:
            # try:
                # exec("""%s=Image.open("D:\\winfile_theme\\%s")"""%(var,path))
                # e32.ao_yield()
            # except Exception,e: print str(e),path
        # sys.exit()
        
        #user.direct_note(u"Caricamento grafica in memoria...",u"Caricamento...")
        s.spuntoimg = Image.open(directory.skin_dir+"\\spunto.png")
        #d.forward();d.draw()
        s.appimg = Image.open(directory.skin_dir+"\\Application.png")
        #d.forward();d.draw()
        s.file_img = Image.open(directory.skin_dir+"\\File.png")
        #d.forward();d.draw()
        try:
            s.bg_img_normal = Image.new(s.screen_size)
            s.bg_img_normal.load(directory.skin_dir+"\\Sfondo.jpg")
        except:
            traceback.print_exc()
        #d.forward();d.draw()
        s.bg_img_landscape = Image.open(directory.skin_dir+"\\Sfondo_LS.jpg")
        #d.forward();d.draw()
        s.csel_img_normal = Image.open(directory.skin_dir+"\\selezione.jpg")
        #d.forward();d.draw()
        s.csel_img_landscape = Image.open(directory.skin_dir+"\\selezione_LS.jpg")
        #d.forward();d.draw()
        s.csel_img_mask_normal = Image.open(directory.skin_dir+"\\selezione_mask.bmp")
        #d.forward();d.draw()
        s.csel_img_mask_landscape = Image.open(directory.skin_dir+"\\selezione_LS_mask.bmp")
         #d.forward();d.draw()
        s.cartella_img = Image.open(directory.skin_dir+"\\Cartella.png")
         #d.forward();d.draw()
        # s.cartellaimg_img=Image.open(directory.skin_dir+"\\Cartella_immagini.png")
        # s.cartellaaudio_img=Image.open(directory.skin_dir+"\\Cartella_musica.png")
        # s.cartellavideo_img=Image.open(directory.skin_dir+"\\Cartella_video.png")
        # s.cartellainstall_img=Image.open(directory.skin_dir+"\\Cartella_install.png")
        s.dll_img = Image.open(directory.skin_dir+"\\dll.png")
         #d.forward();d.draw()
        #s.cartellafont_img=Image.open(directory.skin_dir+"\\font.png")
        s.ingranaggio_img = Image.open(directory.skin_dir+"\\ingranaggio.png") #;d.forward();d.draw()
        s.internet_img = Image.open(directory.skin_dir+"\\internet.png") #;d.forward();d.draw()
        s.mmc_img = Image.open(directory.skin_dir+"\\mmcmemory.png") #;d.forward();d.draw()
        s.tel_img = Image.open(directory.skin_dir+"\\telmemory.png") #;d.forward();d.draw()
        s.musica_img = Image.open(directory.skin_dir+"\\musica.png") #;d.forward();d.draw()
        s.mail_img = Image.open(directory.skin_dir+"\\Mail.png") #;d.forward();d.draw()
        s.ram_img = Image.open(directory.skin_dir+"\\rammemory.png") #;d.forward();d.draw()
        s.rom_img = Image.open(directory.skin_dir+"\\rommemory.png") #;d.forward();d.draw()
        s.video_img = Image.open(directory.skin_dir+"\\video.png") #;d.forward();d.draw()
        s.immagine_img = Image.open(directory.skin_dir+"\\immagine.png") #;d.forward();d.draw()
        s.settings_img = Image.open(directory.skin_dir+"\\settings.png") #;d.forward();d.draw()
        s.archive_img = Image.open(directory.skin_dir+"\\Archivio.png") #;d.forward();d.draw()
        s.vcf_img = Image.open(directory.skin_dir+"\\Vcf.png") #;d.forward();d.draw()
        s.sis_img=Image.open(directory.skin_dir+"\\Sis_installer.png") #;d.forward();d.draw()
        s.text_img = Image.open(directory.skin_dir+"\\testo.png") #;d.forward();d.draw()
        s.pycon_img = Image.open(directory.skin_dir+"\\Python.png") #;d.forward();d.draw()

        #Maschere init
        
        s.appimg_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.file_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.cartella_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.dll_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.ingranaggio_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.internet_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.mmc_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.tel_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.musica_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.mail_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.ram_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.rom_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.video_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.immagine_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.settings_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.archive_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.vcf_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.sis_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.text_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.spunto_mask = Image.new((14,14), 'L') #;d.forward();d.draw()
        s.pycon_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        #Caricamento maschera;d.forward()
        s.appimg_mask.load(directory.skin_dir+"\\Application_mask.bmp") #;d.forward();d.draw()
        s.file_img_mask.load(directory.skin_dir+"\\File_mask.bmp") #;d.forward();d.draw()
        s.cartella_mask.load(directory.skin_dir+"\\Cartella_mask.bmp") #;d.forward();d.draw()
        s.dll_img_mask.load(directory.skin_dir+"\\dll_mask.bmp") #;d.forward();d.draw()
        s.ingranaggio_img_mask.load(directory.skin_dir+"\\ingranaggio_mask.bmp") #;d.forward();d.draw()
        s.internet_img_mask.load(directory.skin_dir+"\\internet_mask.bmp") #;d.forward();d.draw()
        s.mmc_img_mask.load(directory.skin_dir+"\\mmcmemory_mask.bmp") #;d.forward();d.draw()
        s.tel_img_mask.load(directory.skin_dir+"\\telmemory_mask.bmp") #;d.forward();d.draw()
        s.musica_img_mask.load(directory.skin_dir+"\\musica_mask.bmp") #;d.forward();d.draw()
        s.mail_mask.load(directory.skin_dir+"\\mail_mask.bmp") #;d.forward();d.draw()
        s.ram_img_mask.load(directory.skin_dir+"\\rammemory_mask.bmp") #;d.forward();d.draw()
        s.rom_img_mask.load(directory.skin_dir+"\\rommemory_mask.bmp") #;d.forward();d.draw()
        s.video_img_mask.load(directory.skin_dir+"\\video_mask.bmp") #;d.forward();d.draw();d.draw()
        s.immagine_img_mask.load(directory.skin_dir+"\\immagine_mask.bmp") #;d.forward();d.draw()
        s.settings_img_mask.load(directory.skin_dir+"\\settings_mask.bmp") #;d.forward();d.draw()
        s.archive_mask.load(directory.skin_dir+"\\archivio_mask.bmp") #;d.forward();d.draw()
        s.vcf_mask.load(directory.skin_dir+"\\vcf_mask.bmp") #;d.forward();d.draw()
        s.sis_mask.load(directory.skin_dir+"\\Sis_installer_mask.bmp") #;d.forward();d.draw()
        s.text_mask.load(directory.skin_dir+"\\testo_mask.bmp") #;d.forward();d.draw()
        s.spunto_mask.load(directory.skin_dir+"\\spunto_mask.bmp") #;d.forward();d.draw()
        s.pycon_mask.load(directory.skin_dir+"\\Python_mask.bmp") #;d.forward();d.draw()
        #menu

        s.bg_img = s.bg_img_normal
        s.csel_img = s.csel_img_normal#.resize((176,16))
        s.csel_img_mask = Image.new(s.csel_img.size,'L')
        s.csel_img_mask.blit(s.csel_img_mask_normal)
        
        s.mn_sel = s.csel_img.resize((168,16))
        s.mn_sel_mask = s.csel_img_mask.resize((168,16))
        s.submn_sel = s.csel_img.resize((100,16))
        s.submn_sel_mask = s.csel_img_mask.resize((100,16))
        
       # d.close()
    def screen_change(s):

        if ui.landscape:
            s.bg_img=s.bg_img_landscape
            s.csel_img=s.csel_img_landscape
            s.csel_img_mask=Image.new(s.csel_img_mask_landscape.size,'L')
            s.csel_img_mask.blit(s.csel_img_mask_landscape)
            s.mn_i=s.csel_img.resize((200,16))
            s.mn_i_mask=s.csel_img_mask.resize((200,16))

        else:
            s.bg_img=s.bg_img_normal
            s.csel_img=s.csel_img_normal
            s.csel_img_mask=Image.new(s.csel_img_mask_normal.size,'L')
            s.csel_img_mask.blit(s.csel_img_mask_normal)
            s.mn_i=s.csel_img.resize((168,16))
            s.mn_i_mask=s.csel_img_mask.resize((168,16))

    # def theme_files(s,abs=1):
        # if abs: return [
        # directory.skin_dir+"\\spunto.png",
        # directory.skin_dir+"\\Application.png",
        # directory.skin_dir+"\\File.png",
        # directory.skin_dir+"\\Sfondo.jpg",
        # directory.skin_dir+"\\Sfondo_LS.jpg",
        # directory.skin_dir+"\\selezione.jpg",
        # directory.skin_dir+"\\selezione_LS.jpg",
        # directory.skin_dir+"\\selezione_mask.bmp",
        # directory.skin_dir+"\\selezione_LS_mask.bmp",
        # directory.skin_dir+"\\Cartella.png",
        # directory.skin_dir+"\\dll.png",
        # directory.skin_dir+"\\ingranaggio.png",
        # directory.skin_dir+"\\internet.png",
        # directory.skin_dir+"\\mmcmemory.png",
        # directory.skin_dir+"\\telmemory.png",
        # directory.skin_dir+"\\musica.png",
        # directory.skin_dir+"\\Mail.png",
        # directory.skin_dir+"\\rammemory.png",
        # directory.skin_dir+"\\rommemory.png",
        # directory.skin_dir+"\\video.png",
        # directory.skin_dir+"\\immagine.png",
        # directory.skin_dir+"\\settings.png",
        # directory.skin_dir+"\\Archivio.png",
        # directory.skin_dir+"\\Vcf.png",
        # directory.skin_dir+"\\Sis_installer.png",
        # directory.skin_dir+"\\testo.png",
        # directory.skin_dir+"\\Python.png",
        # directory.skin_dir+"\\Application_mask.bmp",
        # directory.skin_dir+"\\File_mask.bmp",
        # directory.skin_dir+"\\Cartella_mask.bmp",
        # directory.skin_dir+"\\dll_mask.bmp",
        # directory.skin_dir+"\\ingranaggio_mask.bmp",
        # directory.skin_dir+"\\internet_mask.bmp",
        # directory.skin_dir+"\\mmcmemory_mask.bmp",
        # directory.skin_dir+"\\telmemory_mask.bmp",
        # directory.skin_dir+"\\musica_mask.bmp",
        # directory.skin_dir+"\\mail_mask.bmp",
        # directory.skin_dir+"\\rammemory_mask.bmp",
        # directory.skin_dir+"\\rommemory_mask.bmp",
        # directory.skin_dir+"\\video_mask.bmp",
        # directory.skin_dir+"\\immagine_mask.bmp",
        # directory.skin_dir+"\\settings_mask.bmp",
        # directory.skin_dir+"\\archivio_mask.bmp",
        # directory.skin_dir+"\\vcf_mask.bmp",
        # directory.skin_dir+"\\Sis_installer_mask.bmp",
        # directory.skin_dir+"\\testo_mask.bmp",
        # directory.skin_dir+"\\spunto_mask.bmp",
        # directory.skin_dir+"\\Python_mask.bmp"
        # ]
        # else: return ["spunto.png","Application.png","File.png","Sfondo.jpg","Sfondo_LS.jpg","selezione.jpg",
        # "selezione_LS.jpg","selezione_mask.bmp","selezione_mask_LS.bmp","Cartella.png","dll.png","ingranaggio.png",
        # "internet.png","mmcmemory.png","telmemory.png","musica.png","Mail.png","rammemory.png",
        # "rommemory.png","video.png","immagine.png","settings.png","Archivio.png","Vcf.png","Sis_installer.png",
        # "testo.png","Python.png","Application_mask.bmp","File_mask.bmp","Cartella_mask.bmp","dll_mask.bmp",
        # "ingranaggio_mask.bmp","internet_mask.bmp","mmcmemory_mask.bmp","telmemory_mask.bmp","musica_mask.bmp",
        # "mail_mask.bmp","rammemory_mask.bmp","rommemory_mask.bmp","video_mask.bmp","immagine_mask.bmp",
        # "settings_mask.bmp","archivio_mask.bmp","vcf_mask.bmp","Sis_installer_mask.bmp","testo_mask.bmp",
        # "spunto_mask.bmp",
        # "Python_mask.bmp"]

class _extensions:
    def __init__(s):
        s.imgextensions = [u".jpg",u".png",u".bmp",u".mbm",u".gif",u".jpeg",u".wbmp",u".168x136",u".40x30",u".80x60",u".ota"]
        s.videoextensions = [u".3gp",u".mp4",u".avi",u".rm",u".mpg",u".mpeg",u".ram",u".flv"]
        s.audioextensions = [u".mp3",u".wav",u".au",u".amr",u".m4a",u".wma",u".ogg",u".aac",u".mid",u".rng",u".kar",u".snd",u".mxmf",u".awb",u".rmf"]
        s.playlistextensions = [u".pyl",u".m3u",u".wpl"] #PyPlayer's & m3u (Default player) playlists
        s.appextensions = [u".app",u".exe"]
        s.libraryextension = [u".lib",u".dll",u".mdl"]
        s.documentsextension = [u".txt",u".pdf",u".doc",u".ppt",u".xls",u".rtf",u".m",u".mm",u".log",u".lrc"]
        s.opendocumentextension = [u".odt",u".ott",u".odm",u".oth",u".ods",u".ots",u".odg",u".otg",u".odp",u".otp",u".odf",u".odb",u".ods"]
        s.settingextension = [u".dat",u".ini",u".sav",u".cfg",u".aex",u".reg"]
        s.archiveextension = [u".zip",u".rar",u".tar",u".gzip",u".7z",u".cab"]
        s.cardextension = [u".vcf",u".db"]
        s.flashextensions = [u".flv",u".swf"]
        s.installerextensions = [u".sis",u".jar",u".jad",u".blz"]
        s.pythonextensions = [u".py",u".pyc",u".pyd",u".pyo",u".pyc_dis"]
        s.internetextensions = [u".html",u".xhtml",u".xml",u".htm"]
        s.default_icon = [grafica.file_img,grafica.file_img_mask]
        s.known = s.imgextensions+s.videoextensions+s.audioextensions+s.playlistextensions+s.appextensions+s.libraryextension+s.documentsextension+s.opendocumentextension+s.settingextension+s.archiveextension+s.cardextension+s.flashextensions+s.installerextensions+s.pythonextensions+s.internetextensions
        s.groups = [(s.imgextensions,"image",[grafica.immagine_img,grafica.immagine_img_mask]),(s.videoextensions,"video",[grafica.video_img,grafica.video_img_mask]),(s.audioextensions,"audio",[grafica.musica_img,grafica.musica_img_mask]),(s.playlistextensions,"playlist",[grafica.musica_img,grafica.musica_img_mask]),(s.appextensions,"apps",[grafica.appimg,grafica.appimg_mask]),
                (s.libraryextension,"libs",[grafica.dll_img,grafica.dll_img_mask]),(s.documentsextension,"docs",[grafica.text_img,grafica.text_mask]),(s.settingextension,"config",[grafica.settings_img,grafica.settings_img_mask]),(s.archiveextension,"archive",[grafica.archive_img,grafica.archive_mask]),
                (s.cardextension,"vcard",[grafica.vcf_img,grafica.vcf_mask]),(s.flashextensions,"flash",[grafica.video_img,grafica.video_img_mask]),(s.installerextensions,"install",[grafica.sis_img,grafica.sis_mask]),(s.pythonextensions,"python",[grafica.pycon_img,grafica.pycon_mask]),(s.internetextensions,"internet",[grafica.internet_img,grafica.internet_img_mask]),(s.opendocumentextension,"open_office",[grafica.text_img,grafica.text_mask])]

        s.drive_icon = [s.default_icon,
                        s.default_icon,
                        [grafica.tel_img, grafica.tel_img_mask],
                        [grafica.mmc_img, grafica.mmc_img_mask],
                        [grafica.mmc_img, grafica.mmc_img_mask],
                        [grafica.ram_img, grafica.ram_img_mask],
                        [grafica.tel_img, grafica.tel_img_mask],
                        [grafica.rom_img, grafica.rom_img_mask],
                        [grafica.mmc_img, grafica.mmc_img_mask]]
            
        #ti=time.clock()
        #for extarray,desc,icon in s.groups:
        #    for ext in extarray:
        #        s.dict_source[ext]=(desc,icon)
        #print time.clock()-ti
    # def search2(s,ext):
        # ext=ext.lower()
        # if ext in s.known:
            # return s.dict_source[ext]
        # return "",s.default_icon
    def search(s,ext):
        ext = ext.lower()
        # if ext in s._cache_:
            # return s._cache_[ext]
        if ext in s.known:
            for extarray,desc,icon in s.groups:
                if ext in extarray:
                    # if len(arr_ay)>2: return arr_ay[1],arr_ay[2]
                    # else: return arr_ay[1],None
                    #s._cache_[ext]=arr_ay[1],arr_ay[2]
                    # if desc==u"image":
                        # desc+='//';desc+=d
                    return desc,icon
#        else:
        return "", s.default_icon
    def splitext(s,path): #Funzione per ricavare l'estensione in modo veloce (+ di os.path.splitext)
        #ext = ''
        f = path.rfind('.')
        if f != -1:
            #ext = path[f:]
            return path[f:]
        return ''
        #return ext
    def search_path(s,dir):
        return s.search(s.splitext(dir))#s.search(os.path.splitext(dir)[1])
    def reload(s):
        s.groups,s.default_icon = [],[]
        s.__init__()

class system_tools:
    def __init__(s):
        s.bg=0
        s.t=e32.Ao_timer()
        s.scr_name="ScreenShotWF_%.3i.%s"
        s.scr_dir="C:\\WinFile_ScreenShots"

    def _init_screenmachine(s):
        import keycapture
        s.keycapture = keycapture
        del keycapture

    def bt_manager(s):
        try:
            import btutils
            modes=[(_(u"disattivo"),_(u"Attivare")),(_(u"attivo"),_(u"Disattivare"))]
            bt_actions=[btutils.on,btutils.off]
            state=btutils.getmode()
            note=_(u"Bluetooth %s.\n%s?")%modes[state]
            if user.query(note,u"Bluetooth"):
                bt_actions[state]()
        except Exception,e:
            user.note(_(u"Periferica Bluetooth non disponibile o già in uso:%s")%unicode(e),_(u"Errore bluetooth"),-1)

    def create_drive_subst(s, path, drv):
        try:
            import miso
        except:
            user.note(_(u"Impossibile avviare %s.\nReinstallare l'applicazione o il modulo.")%"miso")
        if path!=u"":
            path = to_unicode(os.path.normpath(path))
            if (path[-1] != u"\\"):# and (path != u""):
                # The function need a particular path definition, otherwise it may fail
                path = u"%s\\" % path
        else:
            if miso.get_subst_path(drv)==u"":
                return 1
        try:
            if miso.get_subst_path(drv)!=u"":
                miso.create_drive_subst(drv, u"") #Clean it before assign
            miso.create_drive_subst(drv, path)
            #print "Drive link correctly created!"
            return 1
        except:
            return 0

    def compress_ram(s):
        p=sysinfo.free_ram()
        try:
            import miso
        except:
            user.note(_(u"Impossibile avviare %s.\nReinstallare l'applicazione o il modulo.")%"miso")
        miso.compress_all_heaps()
        d=sysinfo.free_ram()
        user.note(_(u"Prima: %s\nDopo: %s\nRecuperati: %s")%(dataformatter.sizetostr(p),dataformatter.sizetostr(d),dataformatter.sizetostr(d-p)),_(u"Rapporto pulizia ram"),-1)

    def restart(s):
        try:
            import miso
        except:
            user.note(_(u"Impossibile avviare %s.\nReinstallare l'applicazione o il modulo.")%"miso")
        scelta=user.query(_(u"Riavviare il telefono?\nI dati non salvati potrebbero essere persi."),_(u"Riavvio telefono"))
        if scelta:
            e32.ao_sleep(0.1)
            main.quit(1)
            miso.restart_phone()

    def backlight(s):
        modes=[(_(u"normale"),_(u"Attivare la funzione per tenerla sempre accesa")),(_(u"sempre accesa"),_(u"Disattivare la funzione e reimpostare l'illuminazione normale"))]
        note=_(u"Luce schermo %s.\n%s?")%modes[s.bg]
        if user.query(note,_(u"Retroilluminazione")):
            if s.bg:
                s.bg=0
            else:
                s.bg=1
                s.keep_bg_on()

    def keep_bg_on(s):
        e32.reset_inactivity() #This doesn't allow to turn off light and to activate screensaver
        if s.bg:
            s.t.after(2,s.keep_bg_on)

    def get_scr_number(s, dir):
        try:
            return len( filter(lambda x: x.startswith("ScreenShotWF_"), os.listdir(dir)))
        except:
            return 0

    def save_screenshot(s, dir):
        no = s.get_scr_number()
        file = os.path.join(dir, s.scr_name%(no,'png'))
        while os.path.exists(file):
            #Checks for file overwritting
            no += 1
            file = os.path.join(dir, s.scr_name%(no,'png'))
        screenshot().save(file, quality=100, bpp=24) #Quality for JPG, bpp for PNG
        print "Screen Shot Saved!", file

    def screenshot(s):
        modes=[(_(u"disattivata"),_(u"Attivare la funzione?\n Alla pressione dei tasti matita + 0 verrà salvata la foto di ciò che si vede!")),(_(u"attivata"),_(u"Disattivarla?"))]
        note=_(u"Funzione screenshot %s.\n%s")%modes[s.bg]
        if user.query(note,_(u"Foto schermo")):
            pass

    def components_list(s, fn = None):
        if not user.query(_(u"Creare nella cartella corrente il file app_log.txt contenente una lista ordinata delle applicazioni installate dall'utente?"),_(u"App.ni installate")):
            return

        adv=user.query(_(u"Aggiungere anche altre informazioni (UID,percorso) oltre al nome dell'applicazione?"),_(u"App.ni installate"),right=u"No",left=u"Sì")
        apps=msys.listapp()
        rn="\r\n"
        header=_("-------------------------------\r\nApplicazioni installate in %s\r\n-------------------------------\r\n")
        header2=_("--> %s (%i) <--\r\n")
        javaC,javaE=[],[]
        sisC,sisE=[],[]
        for name,uid,path in apps:
            if path[-5:]=='].app'and path.rfind('[')!=-1:
                if path[0]=='C': javaC.append((uid,name,path))
                elif path[0]=='E': javaE.append((uid,name,path))
            else:
                if path[0]=='C': sisC.append((uid,name,path))
                elif path[0]=='E': sisE.append((uid,name,path))
        del apps
        if fn:
            f=open(fn,"w")
        else:
            f=open(os.path.join(explorer.dir,"app_log.txt"),"w")
        if sisC or javaC:
            f.write(header%"C:")
            f.write(rn)
            if sisC:
                f.write(header2%("SIS",len(sisC)))
                for uid,name,path in sisC:
                    f.write(ur(name))
                    f.write(rn)
                    if adv:
                        f.write(uid)
                        f.write(rn)
                        f.write(ur(path))
                        f.write(rn)
                    # else:
                        # f.write(rn)
                    f.write(rn)
                #f.write(rn)
            if javaC:
                f.write(header2%("JAVA",len(javaC)))
                for uid,name,path in javaC:
                    f.write(ur(name))
                    f.write(rn)
                    if adv:
                        f.write(uid)
                        f.write(rn)
                        f.write(ur(path))
                        f.write(rn)
                    # else:
                        # f.write(rn)
                    f.write(rn)
                #f.write(rn)
        if sisE or javaE:
            f.write(header%"E:")
            f.write(rn)
            if sisE:
                f.write(header2%("SIS",len(sisE)))
                for uid,name,path in sisE:
                    f.write(ur(name))
                    f.write(rn)
                    if adv:
                        f.write(uid)
                        f.write(rn)
                        f.write(ur(path))
                        f.write(rn)
                    # else:
                        # f.write(rn)
                    f.write(rn)
                #f.write(rn)
            if javaE:
                f.write(header2%("JAVA",len(javaE)))
                for uid,name,path in javaE:
                    f.write(ur(name))
                    f.write(rn)
                    if adv:
                        f.write(uid)
                        f.write(rn)
                        f.write(ur(path))
                        f.write(rn)
                    # else:
                        # f.write(rn)
                    f.write(rn)
                #f.write(rn)
        f.close()
        if not fn:
            explorer.refresh(u"app_log.txt")

class DataFormatter:
    # def __init__(s):
        # s.time_zone=0
    def sizetostr(self, size):
        if not size:
            return u"0 B"
        if size>=1073741824:
            txt=u"%.03f GB" % (size/1073741824.0)
        elif size>=1048576:
            txt=u"%.03f MB" % (size/1048576.0)
        elif size>=1024:
            txt=u"%.03f KB" % (size/1024.0)
        else:
            txt=u"%i B" % size
        return txt
    def getdate(self, tm):
        return u"%02i/%02i/%02i"%(tm[2],tm[1],tm[0])
    def gethour(self, tm):
        return u"%02i:%02i:%02i"%(tm[3],tm[4],tm[5])
    # def gethour_wt(self, tm):
        ##gethour with timezones
        # return u"%02i:%02i:%02i"%(tm[3],tm[4],tm[5])

class _main_:
#Some tools to manage application itself and some basic functions

    def __init__(s):
        s.app_title = appuifw.app.title
        s.platform = e32.s60_version_info
        s.time_zone = 0
        if s.platform>=(3,0):
            s.S60v2 = 0
            s.S60v3 = 1
        else:
            s.S60v2 = 1
            s.S60v3 = 0
        s.time_zone = s.get_time_zone()
        #TODO: set application hidden/sys on user setting
        #e32.ao_sleep(0
    def get_time_zone(s):
        try:
            path= "D:\\WF_TZ_TMP_FN"
            f = open(path,"w")
            dt = time.time() - os.path.getmtime(path)
            
            print "Time zone: %i secs"%dt
            f.close()
            os.remove(path)
            return dt
        except:
            return 0

    def restore(s, to_elem = None, ui_state = None, refresh = 0):
        if ui_state:
            ui.set_state(ui_state)
        else:
            try:
                ui.reload_state()
            except:
                pass#print "Recupero stato UI in main.restore fallito!"
        if ui.mode_callback!=None:
            ui.mode_callback()
        if refresh:
            explorer.refresh(to_elem)
        elif to_elem:
            ListBox.select_item(to_elem)
        explorer.set_inputs_type()

    def hide_app(s):
        s.set_app_flags(0, 1)
        s.switch_to_bg()
        print "WinFile hidden by user decision"
    def ask_to_quit(s):
        if settings.ask_before_exit and (not user.query(_(u"Vuoi veramente uscire da WinFile?"), _(u"Arrivederci!"), _(u"Esci!"), _(u"Ho sbagliato..."))):
            return#s.quit()
        s.quit()
    def quit(s, restart = 0):
        #e32.ao_sleep(0.1)
        #print ui.landscape
        try:
            #Send the "program's close" message to plugin, if any
            plugins.clean_module()
        except:
            pass
        #Avoid to do other operations...from now winfile should be unresponsive!
        ui.unbindall()
        ui.shutdown_effect()
        if settings.save_settings_at_exit:
            #print "shutdown_effect"
            settings.save_to_disk()
            #print "save_to_disk"
            settings.save_session()
            #print "session_save"
            settings.save_colors()
            #print "color_save"
        sys.exitfunc = lambda: None
        #print "sys.exitfunc cleanup"
        if settings.delete_temp:
            #print "Pulizia tema in D:\\"
            gestione_file.removedir(directory.skin_dir, 0)
            #print "Pulizia eseguita!"
        if restart:
            return
        if __shell__:
            lock.signal()
        else:
            #Force quit in some situations
            try:
                msys.kill_app(s.app_title)
            except:
                pass
            appuifw.app.set_exit()
    # def term(s):
        # print "Warning: WinFile force quit..."
        
    def menu_init(s):
        s.file_menu=[(_(u"File"),[(_(u"Apri-esegui"),lambda: start(file=explorer.get_file()),u"[OK]"),
                                  (_(u"Apri da sistema"),lambda: start(2,explorer.get_file())),
                                  (_(u"Apri intern."),lambda: start(1,explorer.get_file())),
                                  (_(u"Vis. testuale"),lambda: text_viewer(explorer.get_file(),end_callback=main.restore)),
                                  (_(u"Nuova cartella"),gestione_file.nuovo),
                                  (_(u"Nuovo file"),lambda: gestione_file.nuovo('file')),
                                  (_(u"Elimina"),gestione_file.cancella,u"[C]"),
                                  (_(u"Rinomina"),gestione_file.rinomina,u"[8]"),
                                  (_(u"Info e extra"),lambda: info_box(explorer.get_file(),main.restore),u"[5]"),
                                  (_(u"Attributi"),lambda: gestione_file.attributes(explorer.get_file()),u"[6]")
                                  ])]
        s.empty_dir=[(_(u"Nuova cartella"),[gestione_file.nuovo]),
                     (_(u"Nuovo file"),[lambda: gestione_file.nuovo('file')]),
                     (_(u"Incolla"),[gestione_file.incolla],u"[7]")]
        s.fileinbox_menu=[(_(u"File"),[(_(u"Apri-esegui"),lambda: start(file=explorer.get_file()),u"[OK]"),
                                  (_(u"Apri da sistema"),lambda: start(2,explorer.get_file())),
                                  (_(u"Apri intern."),lambda: start(1,explorer.get_file())),
                                  (_(u"Vis. testuale"),lambda: text_viewer(explorer.get_file(),end_callback=main.restore)),
                                  (_(u"Elimina"),gestione_file.cancella,u"[C]"),
                                  (_(u"Info e extra"),lambda: info_box(explorer.get_file(),main.restore),u"[5]")
                                  ])]
        s.edit_menu=[(_(u"Modifica"),[(_(u"Copia"),lambda: gestione_file.copia(explorer.get_file(1)),u"[1]"),
                                  (_(u"Taglia"),lambda: gestione_file.taglia(explorer.get_file(1)),u"[4]"),
                                  (_(u"Incolla"),gestione_file.incolla,u"[7]")])]
        s.editinbox_menu=[(_(u"Modifica"),[
                                (_(u"Copia"),lambda: gestione_file.copia_inbox(explorer.get_file(1)),u"[1]"),
                                (_(u"Taglia"),lambda: gestione_file.taglia(explorer.get_file(1)),u"[4]")])
                         ]
        s.select_menu=[(_(u"Seleziona"),[(_(u"Uno"),ListBox.select_element,u"[0]"),
                                  (_(u"Tutti"),ListBox.select_all),
                                  (_(u"Nessuno"),ListBox.select_none),
                                  (_(u"Inverti"),ListBox.select_invert)])]
        s.send_menu=[(_(u"Invia via bluetooth"),[gestione_file.invia],u"[Verde]")]
        s.tools_menu=[(_(u"Utilità"),[(_(u"Cerca"),explorer.cerca,u"[2]"),
                                  (_(u"Crittografa"),lambda: cript_system(explorer.get_file(1))),
                                  (_(u"Bluetooth"), sys_tools.bt_manager),
                                  (_(u"Ottimizza RAM"), sys_tools.compress_ram),
                                  (_(u"Riavvia sistema"), sys_tools.restart),
                                  (_(u"Info sistema"),lambda: info_box("<SYS.INFO>",main.restore)),
                                  (_(u"Illuminazione"), sys_tools.backlight),
                                  (_(u"App. Java"),explorer.find_java),
                                  (_(u"App. installate"), sys_tools.components_list),
                                  (_(u"Debug log"),s.debug_log),
                                  ])]
        s.tools2_menu=[(_(u"Utilità"),[(_(u"Cerca"),explorer.cerca),
                                  (_(u"Bluetooth"), sys_tools.bt_manager),
                                  (_(u"Ottimizza RAM"), sys_tools.compress_ram),
                                  (_(u"Riavvia sistema"), sys_tools.restart),
                                  (_(u"Info sistema"), lambda: info_box("<SYS.INFO>",main.restore)),
                                  (_(u"App. Java"),explorer.find_java),
                                  (_(u"Illuminazione"), sys_tools.backlight),
                                  (_(u"Debug log"),s.debug_log),
                                  (_(u"exec cmd..."),lambda: eval(appuifw.query(u"Insert command: ","text"))),
                                  (_(u"Toggle pad"),ui.toggle_pad)
                                  ])]
        s.settings_menu=[(_(u"Impostazioni"),[(_(u"Preferenze"),settings.impostazioni),
                                  (_(u"Opzioni file"),settings.explorer_settings),
                                  (_(u"Colori tema"),color_init),
                                  (_(u"Apri con"),open_with),
                                  (_(u"Temi & Aspetto"),gestore_temi),
                                  (_(u"Unità virtuali"), _DriveManager),
                                  (_(u"Schermo"),ui.change_screen_mode,_(u"[Matita]")),
                                  (_(u"Reimposta"),settings.reset)
                                  ])]
        s.exit_menu=[(_(u"Esci"),[s.ask_to_quit])]
        s.base_menu=[(_(u"About"),[s.about]),
                     (_(u"About v2"),[_About])
                    ]+s.exit_menu
        s.processes_menu=[(_(u"Termina"),[explorer.term_proc],u"[C]"),(_(u"Aggiorna"),[explorer.refresh_task_proc_list],u"[5]")]
        s.tasks_menu=[(_(u"Operazioni"),[(_(u"Passa a..."),lambda: appswitch.switch_to_fg(ru(explorer.get_file())),u"[OK]"),
                                      (_(u"Chiudi"),explorer.close_kill_task,u"[C]"),
                                      (_(u"Termina"),lambda: explorer.close_kill_task(0))
                                       ]),
                     (_(u"Aggiorna"),[lambda: explorer.refresh_task_proc_list(1)],u"[5]")]

    def set_softkeys(s):
        if settings.right_up_dir:
            ui.right_key = [explorer.back, _(u"Indietro")]
        else:
            ui.right_key = [s.ask_to_quit, _(u"Esci")]
        ui.left_key = [None, settings.etichetta_utente]

    def about(s):
        text_viewer("%s\\About.txt"%directory.appdir,
                    end_callback = s.restore,
                    read_only = 1,
                    title = _(u"Informazioni su WinFile"))
        
    def debug_log(s):
        text_viewer(text = to_unicode(debug.log),
                    end_callback = s.restore,
                    line_sep = u'\n',
                    title = u"** WinFile Debug Console **")

    def switch_to_bg(s):
        msys.send_bg()#s.app_title)

    def switch_to_fg(s):
        msys.send_fg()#s.app_title)
    
    def set_app_flags(s, sys_app, hidden_app):
        try:
            msys.set_system(sys_app)
            msys.set_hidden(hidden_app)
        except:
            traceback.print_exc()

    def did_u_know_tha(s):
        hf = "%s\\hints_%s.txt"%(directory.lang_dir)
        if os.path.exists(hf%settings.lang):
            print "Hints file found: "%settings.lang
        else:
            print "Hints file not found for your language!"
        user.note(u"Ciao", _(u"Lo sapevi che..."), -1)

    def first_boot(s):
        if os.path.exists(directory.first_boot_file):
            print "You are a veteran!"
        else:
            print "Hey! It seems that you're new with WinFile ;)"
            print "Lets go!!!"
            f = open(directory.first_boot_file,"wb")
            f.close()

    def show_error(s, txt = u"nessuna informazione"):

        user.note(u"Errore: %s\nGuardare il debug log per maggiori informazioni."%txt, u"Errore irreversibile")

class _About:

    def __init__(s):
        s.old_ui = ui.get_state()
        ui.reset_ui()
        ui.right_key = [s.esci,_(u'Indietro')]
        ui.left_key = [None,u'']
        import random
        s.rand = random
        s.t = e32.Ao_timer()
        s.drawing = 1
        s.strings = [u"WinFile", u"Version boh"]
        s.txt = load_text_file("%s\\About.txt"%directory.appdir)[0]
        s.tobj = Text_Object(s.txt, skinUI.main_drawable_rect, ALIGNMENT_CENTER, lambda: None)#, s.draw)
        s.tobj.bind()
        s.draw()

    def esci(s):
        s.drawing = 0
        main.restore(None, s.old_ui)

    def load(s):
        #TODO: improve utf-16 detection
        f = open(s.file, 'r')
        text = f.read()
        f.close()
        if text.startswith('\xff\xfe') or text.startswith('\xfe\xff'):# or text.find("\x20\x29")!=-1 or text.find("\x0d\x00\x0a\x00")!=-1: #Se è unicode (utf16)
            enc = 'utf16' #Codifica x l'unicode
            text = text.decode(enc)
        elif text.startswith('\xef\xbb\xbf'): #Se è utf8
            enc = 'utf8'
            text = text.decode(enc)
        else:
            for enc in __supported_encodings__:
                try:
                    text = text.decode(enc).replace(u"\x00","")
                    break
                except UnicodeError:
                    pass
            else:
                raise UnicodeError
        return text.replace(u'\r\n', u'\u2029').replace(u'\n', u'\u2029') , enc , len(text) , u'\u2029'

    def draw(s):
        i = ui.canvas_image
        rand_color = (s.rand.randint(0,255), s.rand.randint(0,255), s.rand.randint(0,255))
        i.clear(rand_color)
        s.tobj.text_redraw(i)
        if s.drawing:
            ui.canvas_refresh()
            s.t.after(0.1,s.draw)
        else:
            main.restore(None, s.old_ui)

class Translator(object):
    def __init__(self):
        self.translations = {}

    def load_compiled(self, filename):
        import marshal
        f = open(filename)
        try:
            data = marshal.load(f)
        except:
            data = None
            print "Compiled language file error: unknown data. Not a lang file or lang file for other python platforms."
            print "Ask the author for an update or for the plain string translation file (ini)"
        f.close()
        self.clean()
        if not type(data)==types.DictType:
            raise RuntimeError, "Compiled language file corrupted. Bad data type."
        else:
            self.translations = data
            print "Compiled language file sucessfully loaded."

    def load_plain(self, filename):
        print "Warning: using plain string loader. To have faster loading times, use a compiled language file (lng)."
        st=[types.UnicodeType, types.StringType]
        f = open(filename)
        lns = f.read()
        f.close()
        self.clean()
        for ln in lns.splitlines():
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            x = None
            try:
                x = eval('''{%s}''' % ln)
            except Exception,e:
                print ValueError('%s: syntax error (%s)' % (repr(ln),str(e))), "Trying to continue..."
            if x:
                dst = x.values()[0]
                if dst:
                    key = x.keys()[0]
                    if key in self.translations:
                        print 'Warning: string already translated %s'%key, "Skipping..."
                    else:
                        if type(dst) in st:
                            self.translations[key] = dst
                        else:
                            print 'String malformed or not a string %s'%dst, "Trying to continue..."
                else:
                    print "Warning: empty translation field.%s"%repr(ln)

    def load(self, filename):
        self.clean()
        try:
            if filename[-3:]=="lng":
                self.load_compiled(filename)
            else:
                self.load_plain(filename)
            return 1
        except:
            traceback.print_exc()

    def clean(self):
        self.translations = {}

    def __call__(self, string):
        try:
            return self.translations[string]
        except:
            return string



# class Konsole:
    # def __init__(s):

        # s.body = appuifw.Text()
        # s.body.color = 0
        # s.body.font = 'normal'
        # s.hidden = 1

    # def show(s):

        # s.prev_body = appuifw.app.body
        # appuifw.app.body = s.body
        # s.hidden = 0

    # def hide(s):

        # appuifw.app.body = s.prev_body
        # s.hidden = 1

    # def __call__(s, t):

        # s.body.add(to_unicode(t))

_ = Translator()
main = _main_()
print "Running on S60 %i.%i"%main.platform
settings = _settings()
settings.load_settings()
ui = _UI()
ui.body_init()
skinUI = _SkinUI()
user = user_messages()
grafica = _grafica(ui.screen_size)
grafica.boot()
skinUI.after_graphics_boot()
#konsole.show()
#konsole(u"Loading graphic resources...")

#konsole(u"Loading settings...")
settings.load_colors()
gestione_file = FileManager()
ext_util = _extensions()
dataformatter = DataFormatter()
#dataformatter.time_zone=settings.time_zone
sys_tools = system_tools()

settings.load_lang()

#import plugin_eng
#p_loader = plugin_eng._Plugin_loader(directory.plugins_dir)
#p_loader.init()

#print "Startup time:",time.time() - t,"sec"
#del t
ListBox = GrafList()
plugins = explorer_plugins()
explorer = Explorer()
main.set_softkeys()
main.menu_init()
explorer.first_boot()
#This will be called when you press red key (like on NSeries phones) or you exit app from task manager (but not killing it)
sys.exitfunc = main.quit

print "WinFile StartUp Complete!"
#konsole(u"WinFile StartUp Complete!")
#konsole.hide()

#Check if WinFile has never run on this platform
main.first_boot()

if __shell__:
    #Set the application lock instance
    lock = e32.Ao_lock()
    #Lock the application without quit to shell until the app is exited
    lock.wait()
    #Restore default output
    debug.quit()
