from tkinter import *
from tkinter import filedialog
import threading
import queue
import time
from PIL import Image, ImageTk


class GUI(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.queue = queue.Queue()
        self.thread = None

        # determine the basic arguments of main window
        self.title('Object Labeler')

        ################################################################################################################
        # add menu bar
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)
        # add a file sub menu
        self.file_menu = Menu(self.menu_bar, tearoff=False)
        self.file_menu.add_command(label='New file', command=self.open_new_file)
        self.file_menu.add_command(label='Exit', command=self.destroy)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        # add a help sub menu
        self.help_menu = Menu(self.menu_bar, tearoff=False)
        self.help_menu.add_command(label='About...')
        self.menu_bar.add_cascade(label='Help', menu=self.help_menu)
        ################################################################################################################
        # add toolbar
        self.toolbar = Frame(self, bd=1, relief=RAISED)
        self.toolbar.pack(side=TOP, fill=X)

        self.add_icon = ImageTk.PhotoImage(Image.open('Icons/add.png'))
        self.add_button = Button(self.toolbar, image=self.add_icon, relief=FLAT)
        self.add_button.pack(side=LEFT, padx=2, pady=2)
        self.add_button.bind('<Enter>', lambda event: self.on_hover(event, 'add'))
        self.add_button.bind('<Leave>', self.on_leave)

        self.done_icon = ImageTk.PhotoImage(Image.open('Icons/done.jpg'))
        self.done_button = Button(self.toolbar, image=self.done_icon, relief=FLAT)
        self.done_button.pack(side=LEFT, padx=2, pady=2)
        self.done_button.bind('<Enter>', lambda event: self.on_hover(event, 'done'))
        self.done_button.bind('<Leave>', self.on_leave)

        self.save_icon = ImageTk.PhotoImage(Image.open('Icons/save.jpg'))
        self.save_button = Button(self.toolbar, image=self.save_icon, relief=FLAT)
        self.save_button.pack(side=LEFT, padx=2, pady=2)
        self.save_button.bind('<Enter>', lambda event: self.on_hover(event, 'save'))
        self.save_button.bind('<Leave>', self.on_leave)
        ################################################################################################################
        # add main frame
        self.main_frame = Frame(self, width=400, height=300)
        self.main_frame.pack(fill=X)

        ################################################################################################################
        # add status bar
        self.status_bar = Frame(self)
        self.status_bar.pack(side=BOTTOM, fill=X)

        self.status = Label(self.status_bar)
        self.status.pack(side=LEFT)

    def on_hover(self, event, text):
        self.status.configure(text=text)

    def on_leave(self, event):
        self.status.configure(text='')

    def open_new_file(self):
        file_name = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                               filetypes=[("video files", "*.mp4;*.avi")])
        print(file_name)

    def spawnThread(self):
        self.button.config(state="disabled")
        self.thread = ThreadedClient(self.queue)
        self.thread.start()
        self.periodicCall()

    def periodicCall(self):
        self.checkQueue()
        if self.thread.is_alive():
            self.after(100, self.periodicCall)
        else:
            self.button.config(state="active")

    def checkQueue(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                self.listbox.insert('end', msg)
                self.progressbar.step(25)
            except queue.Empty:
                pass


class ThreadedClient(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        for x in range(1, 5):
            time.sleep(2)
            msg = "Function %s finished..." % x
            self.queue.put(msg)


if __name__ == "__main__":
    app = GUI()
    app.mainloop()
