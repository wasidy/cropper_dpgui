# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 11:13:44 2023

@author: Vasiliy Stepanov
"""

import dearpygui.dearpygui as dpg
import numpy as np
from PIL import Image, ImageDraw, ExifTags, ImageFont
import os
import time

dpg.create_context()
dpg.create_viewport(title = "Main Window", width = 1663, height = 1200)
#dpg.create_viewport(title = "Second Window", width = 512, height = 512)
dpg.setup_dearpygui()



class Config:
    windowsize = (1100,1100)
    windowbackground = "grey"
    safemargins = 8
    lock_to_img = True
    #ini_dir = "F:/"
    savedir = ""
    patch_size = 512

config = Config()

class FileSelector():
    def __init__(self, startdir = "F:/"):
        self.startdir = startdir
        self.activedir = startdir
        self.activefile = ""
        self.extensions = (".png",".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG")
        self.flist=[]

    def GetFileList(self):
        #print (self.activedir)
        fpath, files = self.checkpath(self.activedir)
        self.flist=[]
        if fpath:
            self.flist = [file for file in files if os.path.splitext(file)[1] in self.extensions]

        return self.flist

    def NextFile(self):
        if self.activefile != "":
            fcount = self.flist.index(self.activefile)
            if fcount<(len(self.flist)-1):
                self.activefile = self.flist[fcount+1]
        return

    def PrevFile(self):
        if self.activefile != "":
            fcount = self.flist.index(self.activefile)
            if fcount>0:
                self.activefile = self.flist[fcount-1]
        return


    def SetActiveFile(self, fname):
        self.activefile = fname

    def GetActiveFile(self):
        return (self.activedir + self.activefile)

    def SetActiveFolder(self, foldername):
        if foldername[-1] != "/" or foldername[-1] != "\\":
            foldername = foldername + "/"
        foldername = foldername.replace("\\","/")
        self.activedir = foldername

    def GetActiveFolder(self):
        return self.activedir

    def GetActiveFileName(self):
        return (self.activefile)

    def checkpath(self, path):

        try:
            tfiles = os.listdir(path)
        except OSError as err:
            path = ""
            tfiles = ""
        return path, tfiles


class MyImage():
    def __init__(self):
        self.filename = str
        self.patch_save_size = 256


    def LoadImage(self, filename):


        if filename:
            self.image = Image.open(filename)
            self.loaded = True
            """
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            exif = self.image._getexif()
            if exif:
                if exif[orientation] == 3:
                    self.image=self.image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    self.image=self.image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    self.image=self.image.rotate(90, expand=True)
                    """
        else:
            self.image = Image.new("RGBA", (800,800), color = "black")
            self.loaded = False



        width, height = self.image.size
        self.imw = width
        self.imh = height

        self.image.putalpha(255)
        #dpg_image = np.frombuffer(self.image.tobytes(), dtype=np.uint8) / 255.0
        #return dpg_image, width, height

    def GetImage(self, new = True):
        if new == True:
            bgw = config.windowsize[0]#-config.safemargins
            bgh = config.windowsize[1]#-config.safemargins
        else:
            bgw = dpg.get_item_width("MainImage", width)#-config.safemargins
            bgh = dpg.get_item_width("MainImage", height)#-config.safemargins

        self.background = Image.new("RGBA", (bgw, bgh), color = config.windowbackground)
        if self.imw>bgw or self.imh>bgh:
            self.ratio = min(bgw/self.imw, bgh/self.imh)
            #self.ratio = self.ratio
        else:
            self.ratio = 1
        newsize = (round(self.imw*self.ratio), round(self.imh*self.ratio))
        temp_image = self.image.resize(newsize)

        #print ("Background size:",bgw,bgh)
        #print ("New size:", newsize)

        self.minx = int((bgw-newsize[0])/2)
        self.miny = int((bgh-newsize[1])/2)
        self.maxx = int((bgw-newsize[0])/2+newsize[0])
        self.maxy = int((bgh-newsize[1])/2+newsize[1])
        #print (self.minx, self.miny, self.maxx, self.maxy)

        offset_x = (bgw-newsize[0]) // 2
        offset_y = (bgh-newsize[1]) // 2

        offset = (offset_x, offset_y)
        self.background.paste(temp_image, offset)
        dpg_image = np.frombuffer(self.background.tobytes(), dtype=np.uint8) / 255.0
        return dpg_image, bgw, bgh

    #def Zoom(self, )

    def ViewPatch(self, coords, patchsize):
        if self.loaded:
            nobg_x = coords[0]-self.minx
            nobg_y = coords[1]-self.miny

            real_x1 = int(nobg_x / self.ratio)
            real_y1 = int(nobg_y / self.ratio)

            real_patch = int(patchsize / self.ratio)

            real_x2 = real_x1 + real_patch
            real_y2 = real_y1 + real_patch


            patch_image = self.image.crop((real_x1, real_y1, real_x2, real_y2)).resize((512,512))
            #print(real_x1, real_y1, real_x2, real_y2)
        else:

            patch_image = Image.new("RGBA",(512,512), color = config.windowbackground)


        dpg_image = np.frombuffer(patch_image.tobytes(), dtype=np.uint8) / 255.0

        #print (np.asarray(patch_image))
        return dpg_image

    def GetPatch(self, coords, patchsize, targetdir, filename, savesize):
        if self.loaded:
            if os.path.isdir(targetdir):
                nobg_x = coords[0]-self.minx
                nobg_y = coords[1]-self.miny

                real_x1 = int(nobg_x / self.ratio)
                real_y1 = int(nobg_y / self.ratio)

                real_patch = int(patchsize / self.ratio)

                real_x2 = real_x1 + real_patch
                real_y2 = real_y1 + real_patch

                aspect = (real_y2-real_y1)/(real_x2-real_x1)
                #print (real_x1, real_y1, real_x2, real_y2, aspect)
                patch_image = self.image.crop((real_x1, real_y1, real_x2, real_y2))

                fname = targetdir + os.path.splitext(filename)[0] +"_" + str(time.time()).replace(".","") + ".png"
                patch_image = patch_image.resize((savesize,savesize))

                patch_image.save(fname)
                print (f"{fname} saved!")

    #def ConvertToDPG(self, image
    def Zoom(self, step):
        pass

class sBox():
    def __init__(self, size = 256, wheelstep = 10):

        self.size = size
        self.step = wheelstep
        self.mousewheelstep = wheelstep

    def ChangeSize(self, value):
        self.size = self.size + value * self.mousewheelstep
    def GetSize(self):
        return self.size
    def SetCoords(self, coords):
        self.coords = coords
    def GetCoords(self):
        return self.coords


sbox = sBox(size = 256)

mypic = MyImage()

img_list = FileSelector(startdir = "F:/")

def save_callback():
    print("Save Clicked")


def SizeSelectionBox(sender, appdata):
    if dpg.is_item_hovered("drawlist"):
        if (sbox.size + appdata * sbox.mousewheelstep) / mypic.ratio >= config.patch_size:

            dpg.delete_item("SelectionBox")
            sbox.ChangeSize(appdata)
            mpos = dpg.get_mouse_pos()
            pos = dpg.get_item_pos("MainImage")
            pos2 = dpg.get_drawing_mouse_pos()
            #xpos = mpos[0] - pos[0] - sbox.GetSize() /2
            #ypos = mpos[1] - pos[1] - sbox.GetSize() /2
            xpos = pos2[0] - sbox.GetSize() /2
            ypos = pos2[1] - sbox.GetSize() /2

            #params = dpg.get_item_info("SelectionBox")
            #print (params)
            #state, coords = params
            dpg.delete_item("SelectionBox")
            dpg.draw_rectangle(pmin = (xpos, ypos), show = True, pmax =(xpos +  sbox.GetSize(), ypos +  sbox.GetSize()), thickness = 1, parent = "MainImage", tag = "SelectionBox")
        #print (pos)


def resize_img(sender, appdata):
    pass
    #print (sender)
    #print (appdata)
    #width, height = dpg.get_item_rect_size(appdata)
    #print (height, width)
    #dpg.set_item_width("MainImage", width)
    #dpg.set_item_height("MainImage", height)

    #dpg.add_image("pic", pos = (0,0), tag = "loadedimage", uv_min=(0.0, 0,0), uv_max=(1,1), label = "". parent = "MainImage")
    #dpg.delete_item("loadedimage", children_only=True)
    #dpg.draw_image("image_id", pmin = (0,0), pmax =(width, height), uv_min=(0, 0), uv_max=(1, 1), tag = "loadedimage", parent = "MainImage")

def MoveSelectionBox(sender, appdata):

    #appdata - mouse coords
    pos = dpg.get_item_pos("MainImage")
    pos2 = dpg.get_drawing_mouse_pos()
    #print (pos2)
    #xpos = appdata[0] - sbox.GetSize() /2 - pos[0]
    #ypos = appdata[1] - sbox.GetSize() /2 - pos[1]

    xpos = pos2[0] - sbox.GetSize() /2
    ypos = pos2[1] - sbox.GetSize() /2
    #xposmax = pos2[0] + sbox.GetSize() /2
    #yposmax = pos2[1] + sbox.GetSize() /2

    if xpos<mypic.minx:
        xpos=mypic.minx
    if xpos>(mypic.maxx-sbox.GetSize()):
        xpos=mypic.maxx - sbox.GetSize()
        #print(xpos)
    if ypos<mypic.miny:
        ypos=mypic.miny
    if ypos>(mypic.maxy-sbox.GetSize()):
        ypos=mypic.maxy - sbox.GetSize()

    dpg.delete_item("SelectionBox")
    sbox.SetCoords((xpos,ypos))
    dpg.draw_rectangle(pmin = (xpos, ypos), show = True, pmax =(xpos +  sbox.GetSize(), ypos +  sbox.GetSize()), thickness = 1, parent = "MainImage", tag = "SelectionBox")

    # Redraw preview
    #dpg.delete_item("prev_pic")
    p_texture = mypic.ViewPatch(sbox.GetCoords(), sbox.GetSize())
#    print(p_texture)
    dpg.set_value("prev_pic", p_texture)

#    with dpg.texture_registry():
#        dpg.add_static_texture(512, 512, p_texture, tag="prev_pic")

    #dpg.configure_item("preview_image", texture_tag = "prev_pic")




def hover_img(sender,appdata):
    print(appdata)

def mouse_click_lb(sender, appdata):
    coords = sbox.GetCoords()
    a = dpg.is_item_hovered("drawlist")
    if a:
        mypic.GetPatch(coords, sbox.GetSize(), targetdir = config.savedir, filename = img_list.GetActiveFileName(), savesize = config.patch_size)

with dpg.window(tag = "Primary", no_scrollbar = True, no_resize = True):

    mypic.LoadImage("")
    data, width, height = mypic.GetImage()

    with dpg.texture_registry():
        dpg.add_static_texture(width, height, data, tag="pic")

    with dpg.window(label = img_list.GetActiveFileName(), width = config.windowsize[0]+15, height = config.windowsize[1]+40,
                    tag = "MainImage",  no_scrollbar = True, no_resize = True, no_move = True,
                    no_collapse = True, no_close = True, menubar = False, pos = (10,10)):

        with dpg.drawlist(pos = (0,0), width = config.windowsize[0], height = config.windowsize[1], tag = "drawlist", show = True) as canvas:
            dpg.draw_image("pic", pmin = (0,0), pmax =(config.windowsize[0], config.windowsize[1]), uv_min=(0.0, 0,0), uv_max=(1, 1), tag = "loadedimage")



def ReLoadImg():
    mypic.LoadImage(img_list.GetActiveFile())

    data, width, height = mypic.GetImage()
    dpg.configure_item("MainImage", label = img_list.GetActiveFile())
    dpg.delete_item("loadedimage")
    dpg.delete_item("drawlist")
    dpg.delete_item("pic")

    with dpg.texture_registry():
        dpg.add_static_texture(width, height, data, tag="pic")

    with dpg.drawlist(pos = (0,0), width = config.windowsize[0], height = config.windowsize[1], tag = "drawlist", show = True, parent = "MainImage") as canvas:
        dpg.draw_image("pic", pmin = (0,0), pmax =(config.windowsize[0], config.windowsize[1]), uv_min=(0.0, 0,0), uv_max=(1, 1), tag = "loadedimage", parent = "drawlist")
    #print (img_list.GetActiveFile())
    #dpg.configure_item("loadedimage", texture_tag = "pic")

    #with.dpg.add_child_window()

with dpg.item_handler_registry(tag = "imagehandler") as handler:
    dpg.add_item_resize_handler(callback=resize_img)


dpg.bind_item_handler_registry("MainImage", "imagehandler")


def load_new_image(sender, data):
    img_list.SetActiveFile(data)
    ReLoadImg()

def FolderSelection_callback(sender, app_data):
    img_list.SetActiveFolder(app_data.get("file_path_name"))

    #dpg.delete_item("filelist")
    #dpg.add_listbox(items = img_list.GetFileList(), callback = load_new_image, num_items = 48, tag = "filelist", parent = "FileWindow")
    dpg.configure_item("filelist", items = img_list.GetFileList())
    dpg.configure_item("folder_selection", default_path = img_list.GetActiveFolder())
    dpg.configure_item("dirbutton", label = img_list.GetActiveFolder())
    #print (img_list.GetActiveFolder())

def SaveFolder_callback(sender, app_data):

    foldername = app_data.get("file_path_name")
    if foldername[-1] != "/" or foldername[-1] != "\\":
        foldername = foldername + "/"
    foldername = foldername.replace("\\","/")
    config.savedir = foldername
    dpg.configure_item("savefolder_selection", default_path = config.savedir)
    dpg.configure_item("targetdir", label = config.savedir)


def cancel_callback(sender, app_data):
    pass

def keydown(sender, app_data):
    #print (app_data)
    key = app_data
    # 39 - right
    # 37 - left
    # 32 - space
    # 49 - 1 and etc
    if key == 39:
        #print (dpg.get_item_configuration("filelist"))
        if img_list.GetActiveFileName() !="":
            img_list.NextFile()
            load_new_image(0, img_list.GetActiveFileName())
        #dpg.configure_item("filelist", default_value = 10)
    if key == 37:
        #print (dpg.get_item_configuration("filelist"))
        if img_list.GetActiveFileName() !="":
            img_list.PrevFile()
            load_new_image(0, img_list.GetActiveFileName())


def patch_size_button(sender, appdata, userdata):
    #print (userdata)

    buttons = ["sizebutton64", "sizebutton128", "sizebutton256", "sizebutton512", "sizebutton768"]
    labels = ["64","128","256","512","768"]
    for i in range(5):
        dpg.configure_item(buttons[i], label = labels[i])
    tbn = "sizebutton" + str(userdata)
    dpg.configure_item(tbn, label = "< " + str(userdata) + " >")
    mypic.path_save_size = userdata
    config.patch_size = userdata
    return

with dpg.window(label="FileWindow", width = 512, height = 510, tag="FileWindow", pos = (1130,10), no_title_bar = True):
    #dpg.add_text("Hhdh")
    dpg.add_button(label=img_list.activedir, callback=lambda: dpg.show_item("folder_selection"), width = 495, tag = "dirbutton")
    dpg.add_listbox(items = img_list.GetFileList(), callback = load_new_image, num_items = 27, tag = "filelist", width = 495)
    dpg.add_file_dialog(directory_selector=True, show=False,
                        callback=FolderSelection_callback, tag="folder_selection",
                        cancel_callback=cancel_callback,
                        width = 500, height = 800,
                        default_path = img_list.GetActiveFolder(),
                        modal = True,
                        )

with dpg.window(label="ParametersWindow", width = 512, height = 60,
                tag="Params", pos = (1130, 532),
                no_title_bar = True, no_resize = True, no_move = True,
                no_collapse = True, no_close = True):
    dpg.add_button(label="Select target dir", callback=lambda: dpg.show_item("savefolder_selection"), width = 495, tag = "targetdir")
    dpg.add_file_dialog(directory_selector=True, show=False,
                        callback=SaveFolder_callback, tag="savefolder_selection",
                        cancel_callback=cancel_callback,
                        width = 500, height = 800,
                        default_path = config.savedir,
                        modal = True,
                        )
    with dpg.table(header_row=False):
        dpg.add_table_column()
        dpg.add_table_column()
        dpg.add_table_column()
        dpg.add_table_column()
        dpg.add_table_column()
        with dpg.table_row():
            dpg.add_button(label = "64", width = 88, height = 50, tag = "sizebutton64", callback = patch_size_button, user_data = 64)
            dpg.add_button(label = "128", width = 88, height = 50, tag = "sizebutton128", callback = patch_size_button, user_data = 128)
            dpg.add_button(label = "< 256 >", width = 88, height = 50, tag = "sizebutton256", callback = patch_size_button, user_data = 256)
            dpg.add_button(label = "512", width = 88, height = 50, tag = "sizebutton512", callback = patch_size_button, user_data = 512)
            dpg.add_button(label = "768", width = 88, height = 50, tag = "sizebutton768", callback = patch_size_button, user_data = 768)


with dpg.window(label="Preview", pos = (1130, 638), width = 512, height = 512, tag = "Preview", no_resize = True,
                no_title_bar = True, no_move = True, no_collapse = True, no_close = True, no_scrollbar = True):
    p_texture = mypic.ViewPatch((0,0), config.patch_size)
    with dpg.texture_registry():
        dpg.add_dynamic_texture(512, 512, p_texture, tag="prev_pic")
    dpg.add_image("prev_pic")
    #with dpg.drawlist(pos = (0,0), width = 512, height = 512, tag = "prev_drawlist", show = True, parent = "Preview") as canvas:
    #    dpg.draw_image("prev_pic", pmin = (0,0), pmax =(512,512), uv_min=(0.0, 0,0), uv_max=(1, 1), tag = "preview_image", parent = "prev_drawlist")


with dpg.handler_registry():
    dpg.add_mouse_move_handler(callback=MoveSelectionBox)
    dpg.add_mouse_wheel_handler(callback=SizeSelectionBox)
    dpg.add_mouse_release_handler(button=dpg.mvMouseButton_Left, callback=mouse_click_lb)
    dpg.add_key_press_handler(key=- 1, callback = keydown)


dpg.show_viewport()
dpg.set_primary_window("Primary", True)
dpg.start_dearpygui()
dpg.destroy_context()