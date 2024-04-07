from ctypes import windll, byref, sizeof, c_int
from pystray import Icon, Menu, MenuItem
import customtkinter as ctk
from enum import Enum
from PIL import Image
import threading
import random
import json
import sys
import os

class Color(str, Enum):
    BACK =   '#B26456'
    FRAME2 = '#F7C566'
    BUTT1 =  '#EA9840'
    BUTT2 =  '#DC6B19'
    BUTT3 =  '#EEB27B'
    TEXT =   '#FFF8DC'

def bar_color(app):
    HWND = windll.user32.GetParent(app.winfo_id())
    DWMWA_CAPTION_COLOR = 35
    COLOR_1 = 0x005664B2
    windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_CAPTION_COLOR,
                                        byref(c_int(COLOR_1)), sizeof(c_int))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class LoadConfig():

    default_config = {"cat_position": 947}

    def __init__(self) -> None:
        self.config = self.open_config_file()

    def open_config_file(self) -> str:
        with open(resource_path('config.json'), 'r') as file:
            try:
                config = json.load(file)
            except FileNotFoundError:
                config = self.default_config
        return config

    def get_config(self):
        return self.config

class SettingWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(fg_color=Color.BACK)
        self.after(201, lambda: self.iconbitmap(resource_path('icons\\setting_icon.ico')))
        self.mas = master
        self.cat_pos = LoadConfig().get_config()
        self.geometry('300x120+200+200')
        self.title('Settings')
        self.buttons()
        bar_color(self)

    def buttons(self):
        up_button = ctk.CTkButton(self, text='UP', command=self.go_up,
                                    fg_color=Color.BUTT1, hover_color=Color.BUTT3,
                                    text_color=Color.TEXT)
        up_button.pack(side='top', padx=10, pady=10, anchor='center', expand=True)

        down_button = ctk.CTkButton(self, text='DOWN', command=self.go_down,
                                    fg_color=Color.BUTT1, hover_color=Color.BUTT3,
                                    text_color=Color.TEXT)
        down_button.pack(side='top', padx=10, pady=10, anchor='center', expand=True)

    def go_up(self):
        self.mas.geometry(f'+{self.mas.winfo_x()}+{self.cat_pos["cat_position"]-1}')
        self.cat_pos["cat_position"] -= 1
        self.save_settings()

    def go_down(self):
        self.mas.geometry(f'+{self.mas.winfo_x()}+{self.cat_pos["cat_position"]+1}')
        self.cat_pos["cat_position"] += 1
        self.save_settings()

    def save_settings(self):
        with open(resource_path('config.json'), 'w') as file:
            json.dump(self.cat_pos, file)

class IconTray():
    def __init__(self, master) -> None:
        self.master = master
        self.show_state = False
        self.hide_state = True
        self.top_level = None
        self.create_tray_icon()

    def create_tray_icon(self) -> None:
        cat_icon = Image.open(resource_path('icons\\icon.ico'))
        icon = Icon('Screen kitty', icon=cat_icon, title='Screen kitty',
                    menu=Menu(
                        MenuItem('Hide', self.hide_kitty, checked=lambda item: self.show_state),
                        MenuItem('Show', self.show_kitty, checked=lambda item: self.hide_state),
                        Menu.SEPARATOR,
                        MenuItem('Settings', self.settings),
                        Menu.SEPARATOR,
                        MenuItem('Exit', self.exit_app)))
        icon.run()

    def hide_kitty(self, icon, item) -> None:
        if self.show_state:
            return
        self.show_state = not self.show_state
        self.hide_state = not self.hide_state
        self.master.withdraw()

    def show_kitty(self, icon, item) -> None:
        if self.hide_state:
            return
        self.show_state = not self.show_state
        self.hide_state = not self.hide_state
        self.master.deiconify()

    def settings(self):
        if len(self.master.winfo_children()) > 1:
            return
        self.top_level = SettingWindow(self.master)

    def exit_app(self) -> None:
        os._exit(0)

class LoadAllSprites():
    def __init__(self) -> None:
        self.all_sprites = []
        self.load_images()

    def load_images(self) -> None:
        for image in os.listdir(resource_path('assets')):
            img_ = Image.open(resource_path(f'assets\\{image}'))
            img = ctk.CTkImage(dark_image=img_, size=img_.size)
            self.all_sprites.append(img)

    def get_images(self) -> None:
        return self.all_sprites

class MainFrame(ctk.CTkLabel):
    def __init__(self, master, sprites) -> None:
        self.sprites = sprites
        self.master = master
        self.current_frame = 0
        self.direction = 'left'
        self.counter = (random.randrange(20, 50))
        self.speedup = 1
        super().__init__(master, text='', bg_color='white', image=self.sprites[self.current_frame])
        self.pack()
        self.master.bind('<Enter>', lambda e: self.move_hovered_cat(e))
        self.animate()

    def chose_mode(self) -> None:
        if self.counter <= 0:
            idle = random.choice([1,0])
            if idle:
                self.current_frame = 8
                self.direction = 'idle'
                self.counter = (random.randrange(20, 200))
            else:
                self.direction = random.choice(['left', 'right'])
                self.counter = (random.randrange(20, 200))
                if self.direction == 'left':
                    self.current_frame = 0
                else:
                    self.current_frame = 4

    def detect_edges(self) -> None:
        if self.master.winfo_x() <= 2:
            self.direction = 'right'
            self.current_frame = 4
            self.counter = (random.randrange(20, 200))
        elif self.master.winfo_x() >= self.master.winfo_width()-120:
            self.direction = 'left'
            self.current_frame = 0
            self.counter = (random.randrange(20, 200))

    def change_directions(self) -> None:
        if self.current_frame == 4 and self.direction == 'left':
            self.current_frame = 0
        elif self.current_frame == 8 and self.direction == 'right':
            self.current_frame = 4
        elif self.current_frame == 12 and self.direction == 'idle':
            self.current_frame = 8

    def animate(self) -> None:
        self.chose_mode()
        self.detect_edges()
        self.change_directions()
        self.configure(image=self.sprites[self.current_frame])
        self.current_frame += 1
        self.counter -= 1
        if self.speedup > 1 and not self.current_frame%4:
            self.speedup -= 1
        if self.direction == 'idle':
            self.speedup = 1
        self.move_id = self.master.after(50, self.move_cat)
        self.animate_id = self.master.after((200//self.speedup), self.animate)

    def move_cat(self) -> None:
        if self.direction == 'left':
            self.master.geometry(f'+{self.master.winfo_x()-(3*self.speedup)}+{self.master.winfo_y()}')
        if self.direction == 'right':
            self.master.geometry(f'+{self.master.winfo_x()+(3*self.speedup)}+{self.master.winfo_y()}')

    def move_hovered_cat(self, e) -> None:
        if e.x < self.master.winfo_width()//2:
            self.direction = 'right'
            self.current_frame = 4
        else:
            self.direction = 'left'
            self.current_frame = 0
        self.master.after_cancel(self.move_id)
        self.master.after_cancel(self.animate_id)
        self.speedup = 3
        self.animate()

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.geometry(f'+550+{LoadConfig().get_config()["cat_position"]}')
        self.wm_attributes('-topmost', True)
        self.wm_attributes('-transparentcolor', 'white')
        self.lift()
        self.grab_set()
        self.overrideredirect(True)
        all_sprites = LoadAllSprites().get_images()
        MainFrame(self, all_sprites)

if __name__ == "__main__":
    app = App()
    icon_thread = threading.Thread(target=lambda: IconTray(app))
    icon_thread.start()
    app.mainloop()
