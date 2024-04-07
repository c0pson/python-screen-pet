from pystray import Icon, Menu, MenuItem
import customtkinter as ctk
from PIL import Image
import threading
import random
import os

class IconTray():
    def __init__(self, master) -> None:
        self.master = master
        self.state = False
        self.state_1 = True
        self.create_tray_icon()

    def create_tray_icon(self):
        cat_icon = Image.open('icon.ico')
        icon = Icon('Screen kitty', icon=cat_icon, title='Screen kitty',
                    menu=Menu(
                        MenuItem('Hide', self.hide_kitty, checked=lambda item: self.state),
                        MenuItem('Show', self.show_kitty, checked=lambda item: self.state_1),
                        MenuItem('Exit', self.exit_app)))
        icon.run()

    def hide_kitty(self, icon, item):
        self.state = not self.state
        self.state_1 = not self.state_1
        self.master.withdraw()

    def show_kitty(self, icon, item):
        self.state = not self.state
        self.state_1 = not self.state_1
        self.master.deiconify()

    def exit_app(self):
        os._exit(0)

class LoadAllSprites():
    def __init__(self) -> None:
        self.all_sprites = []
        self.load_images()

    def load_images(self):
        for image in os.listdir('assets'):
            img_ = Image.open(f'assets\\{image}')
            img = ctk.CTkImage(dark_image=img_, size=img_.size)
            self.all_sprites.append(img)

    def get_images(self):
        return self.all_sprites

class MainFrame(ctk.CTkLabel):
    def __init__(self, master, sprites):
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

    def chose_mode(self):
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

    def detect_edges(self):
        if self.master.winfo_x() <= 2:
            self.direction = 'right'
            self.current_frame = 4
            self.counter = (random.randrange(20, 200))
        elif self.master.winfo_x() >= 1800:
            self.direction = 'left'
            self.current_frame = 0
            self.counter = (random.randrange(20, 200))

    def change_directions(self):
        if self.current_frame == 4 and self.direction == 'left':
            self.current_frame = 0
        elif self.current_frame == 8 and self.direction == 'right':
            self.current_frame = 4
        elif self.current_frame == 12 and self.direction == 'idle':
            self.current_frame = 8

    def animate(self):
        self.chose_mode()
        self.detect_edges()
        self.change_directions()
        self.configure(image=self.sprites[self.current_frame])
        self.current_frame += 1
        self.counter -= 1
        if self.speedup > 1 and not self.current_frame%4:
            self.speedup -= 1
        self.move_id = self.master.after(50, self.move_cat)
        self.animate_id = self.master.after((200//self.speedup), self.animate)

    def move_cat(self):
        if self.direction == 'left':
            self.master.geometry(f'+{self.master.winfo_x()-(3*self.speedup)}+{self.master.winfo_y()}')
        if self.direction == 'right':
            self.master.geometry(f'+{self.master.winfo_x()+(3*self.speedup)}+{self.master.winfo_y()}')

    def move_hovered_cat(self, e):
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
    def __init__(self):
        super().__init__()
        self.geometry("+550+947")
        self.wm_attributes("-topmost", True)
        self.wm_attributes("-transparentcolor", "white")
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
