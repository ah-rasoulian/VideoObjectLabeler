from tkinter import *
from tkinter import filedialog
import threading
from PIL import Image, ImageTk
import cv2
import numpy as np


class GUI(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.frames_list = list()
        self.thread = None
        self.main_frame_image = None
        self.current_frame_index = 0
        self.points = {}
        self.contours = {}

        # drawing options
        self.show_points = False
        self.show_contours = True

        # determine the basic arguments of main window
        self.title('Object Labeler')

        ################################################################################################################
        # add menu bar
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)
        # add a file sub menu
        self.file_menu = Menu(self.menu_bar, tearoff=False)
        self.file_menu.add_command(label='New file', command=self.spawn_file_reader_thread)
        self.file_menu.add_command(label='Exit', command=self.destroy)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        # add a help sub menu
        self.help_menu = Menu(self.menu_bar, tearoff=False)
        self.help_menu.add_command(label='About...')
        self.menu_bar.add_cascade(label='Help', menu=self.help_menu)
        ################################################################################################################
        # add toolbar
        self.toolbar = Frame(self, bd=1)
        self.toolbar.grid(row=0, sticky='w')

        self.add_icon = ImageTk.PhotoImage(Image.open('Icons/add.png'))
        self.add_button = Button(self.toolbar, image=self.add_icon, relief=FLAT, state=DISABLED)
        self.add_button.pack(side=LEFT, padx=2, pady=2)
        self.add_button.bind('<Enter>', lambda event: self.on_hover('add'))
        self.add_button.bind('<Leave>', lambda event: self.on_leave())
        self.add_button.bind('<Button-1>', lambda event: self.activate_adding_points())

        self.done_icon = ImageTk.PhotoImage(Image.open('Icons/done.jpg'))
        self.done_button = Button(self.toolbar, image=self.done_icon, relief=FLAT, state=DISABLED)
        self.done_button.pack(side=LEFT, padx=2, pady=2)
        self.done_button.bind('<Enter>', lambda event: self.on_hover('done'))
        self.done_button.bind('<Leave>', lambda event: self.on_leave())
        self.done_button.bind('<Button-1>', lambda event: self.create_contour())

        self.save_icon = ImageTk.PhotoImage(Image.open('Icons/save.jpg'))
        self.save_button = Button(self.toolbar, image=self.save_icon, relief=FLAT, state=DISABLED)
        self.save_button.pack(side=LEFT, padx=2, pady=2)
        self.save_button.bind('<Enter>', lambda event: self.on_hover('save'))
        self.save_button.bind('<Leave>', lambda event: self.on_leave())
        ################################################################################################################
        # add main frame
        self.main_frame = Label(self, width=100, height=20)
        self.main_frame.grid(row=1)
        self.main_frame.bind('<Motion>', self.show_coordinates)
        self.main_frame.bind('<Button-1>', self.add_point)

        ################################################################################################################
        # add buttons pane
        self.buttons_frame = Frame(self)

        self.previous_icon = ImageTk.PhotoImage(Image.open('Icons/previous.jpg'))
        self.previous_button = Button(self.buttons_frame, image=self.previous_icon, relief=FLAT)
        self.previous_button.pack(side=LEFT, padx=2, pady=2)
        self.previous_button.bind('<Enter>', lambda event: self.on_hover('previous'))
        self.previous_button.bind('<Leave>', lambda event: self.on_leave())
        self.previous_button.bind('<Button-1>', lambda event: self.change_picture('previous'))

        self.frame_index_scale = Scale(self.buttons_frame, orient=HORIZONTAL, from_=0, to=10)
        self.frame_index_scale.set(self.current_frame_index)
        self.frame_index_scale.pack(side=LEFT, padx=2, pady=2)
        self.frame_index_scale.bind('<Motion>', lambda event: self.update_index_frame())
        self.frame_index_scale.bind('<Button-1>', lambda event: self.change_picture('scale'))
        self.frame_index_scale.bind('<ButtonRelease-1>', lambda event: self.change_picture('scale'))

        self.next_icon = ImageTk.PhotoImage(Image.open('Icons/next.png'))
        self.next_button = Button(self.buttons_frame, image=self.next_icon, relief=FLAT)
        self.next_button.pack(side=LEFT, padx=2, pady=2)
        self.next_button.bind('<Enter>', lambda event: self.on_hover('next'))
        self.next_button.bind('<Leave>', lambda event: self.on_leave())
        self.next_button.bind('<Button-1>', lambda event: self.change_picture('next'))
        ################################################################################################################
        # add status bar
        self.status_bar = Frame(self)
        self.status_bar.grid(row=3, sticky='w')

        self.status = Label(self.status_bar)
        self.status.pack(side=LEFT)
        ################################################################################################################

    def show_coordinates(self, event):
        self.status.configure(text='x={}, y={}'.format(event.x, event.y))

    def add_point(self, event):
        if self.show_points:
            if self.done_button['state'] == DISABLED:
                self.done_button['state'] = NORMAL
            if not self.points.__contains__(self.current_frame_index):
                self.points[self.current_frame_index] = list()
            self.points.get(self.current_frame_index).append([event.x, event.y])
            self.display_image(self.frames_list[self.current_frame_index])

    def activate_adding_points(self):
        self.show_points = True
        self.previous_button['state'] = DISABLED
        self.next_button['state'] = DISABLED
        self.frame_index_scale['state'] = DISABLED

    def create_contour(self):
        self.done_button['state'] = DISABLED
        self.previous_button['state'] = NORMAL
        self.next_button['state'] = NORMAL
        self.frame_index_scale['state'] = NORMAL

        new_contour = np.array(self.points[self.current_frame_index]).reshape((-1, 1, 2)).astype(np.int32)
        self.points.pop(self.current_frame_index)
        self.show_points = False
        if not self.contours.__contains__(self.current_frame_index):
            self.contours[self.current_frame_index] = list()
        self.contours.get(self.current_frame_index).append(new_contour)
        self.display_image(self.frames_list[self.current_frame_index])

    def on_hover(self, text):
        self.status.configure(text=text)

    def update_index_frame(self):
        self.frame_index_scale.configure(to=len(self.frames_list) - 1)

    def on_leave(self):
        self.status.configure(text='')

    def change_picture(self, direction):
        if direction == 'next':
            if self.current_frame_index == len(self.frames_list) - 1 or self.next_button['state'] == DISABLED:
                return
            else:
                self.current_frame_index += 1
        elif direction == 'previous':
            if self.current_frame_index == 0 or self.previous_button['state'] == DISABLED:
                return
            else:
                self.current_frame_index -= 1
        else:
            self.current_frame_index = self.frame_index_scale.get()

        if self.current_frame_index == 0:
            self.previous_button['state'] = DISABLED
        elif self.previous_button['state'] == DISABLED and not self.show_points:
            self.previous_button['state'] = NORMAL

        if self.current_frame_index == len(self.frames_list) - 1:
            self.next_button['state'] = DISABLED
        elif self.next_button['state'] == DISABLED and not self.show_points:
            self.next_button['state'] = NORMAL

        self.frame_index_scale.set(self.current_frame_index)
        self.display_image(self.frames_list[self.current_frame_index])

    def display_image(self, image):
        image = self.frames_list[self.current_frame_index].copy()

        if self.show_points and self.points.__contains__(self.current_frame_index):
            points = self.points.get(self.current_frame_index)
            for point in points:
                image = cv2.circle(image, tuple(point), 2, (0, 0, 255), -1)

        if self.show_contours:
            image = cv2.drawContours(image, self.contours.get(self.current_frame_index), -1, (0, 255, 0), 1)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.main_frame.configure(height=image.shape[0], width=image.shape[1])
        self.main_frame_image = ImageTk.PhotoImage(Image.fromarray(image))
        self.main_frame.configure(image=self.main_frame_image)

    def spawn_file_reader_thread(self):
        self.thread = ThreadedFileReader(self.frames_list)
        self.thread.start()
        self.periodic_call()

    def periodic_call(self):
        self.display_first_frame()
        if self.main_frame_image is None:
            self.after(100, self.periodic_call)

    def display_first_frame(self):
        if len(self.frames_list) > 0:
            self.buttons_frame.grid(row=2)
            self.previous_button['state'] = DISABLED
            self.add_button['state'] = NORMAL
            self.save_button['state'] = NORMAL
            self.display_image(self.frames_list[self.current_frame_index])


class ThreadedFileReader(threading.Thread):
    def __init__(self, frames):
        threading.Thread.__init__(self)
        self.frames = frames

    def run(self):
        file_name = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                               filetypes=[("video files", "*.mp4;*.avi")])
        cap = cv2.VideoCapture(file_name)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_rate = 1
        for frame_no in range(0, total_frames, sample_rate):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            _, image = cap.read()
            self.frames.append(image)
        print(file_name, total_frames)


if __name__ == "__main__":
    app = GUI()
    app.mainloop()
