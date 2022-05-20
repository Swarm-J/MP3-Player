import tkinter
from tkinter import filedialog, ttk
import pygame
import os
import random
import time
from mutagen.mp3 import MP3


class Scrollbox(tkinter.Listbox):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.scrollbar = tkinter.Scrollbar(parent, orient=tkinter.VERTICAL, command=self.yview)

    def grid(self, row, column, rowspan=1, columnspan=1, sticky='nse', **kwargs):
        super().grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, **kwargs)
        self.scrollbar.grid(row=row, column=column, rowspan=rowspan, sticky='nse', pady=(20, 0))
        self['yscrollcommand'] = self.scrollbar.set


class Musicplayer(Scrollbox):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.stop = False
        self.mute = False
        self.pause = False
        self.repeat = False
        self.shuffle = False

        # Bindings
        self.bind('<Double-Button-1>', self.play_click)  # Play song on double click
        self.bind('<ButtonRelease-3>', self.popup_menu)  # Open up menu to play / remove song

    def popup_menu(self, event):
        m = tkinter.Menu(self, tearoff=False)
        m.add_command(label='Play', command=self.play_song)
        m.add_separator()
        m.add_command(label='Remove', command=self.remove_songs)

        if self.curselection():     # If a song is selected
            m.tk_popup(event.x_root, event.y_root)

    def add_song(self):
        global head_tail_path

        files = tkinter.filedialog.askopenfilenames(initialdir=os.path.expanduser('~/Music'),
                                                    title='Choose a File',
                                                    filetypes=[('mp3 Files', '*.mp3'), ('ogg Files', '*.ogg')])
        if files:
            for song in files:
                head_tail_path = os.path.split(song)
                # Remove directory info from song
                self.insert(tkinter.END, head_tail_path[1])
            self.select_set(0)

    def play_song(self):
        time_bar.config(text='')
        song_slider.config(value=0)
        self.stop = False

        if self.pause:
            pygame.mixer.music.unpause()
            self.pause = False

        else:
            song_selected = self.get(tkinter.ACTIVE)
            song_path = os.path.join(head_tail_path[0], song_selected)
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()

            self.play_time()    # call function to get song length

    def play_click(self, event):
        time_bar.config(text='')
        song_slider.config(value=0)

        self.stop = False

        song = self.get(tkinter.ANCHOR)
        full_path_song = os.path.join(head_tail_path[0], song)
        pygame.mixer.music.load(full_path_song)
        pygame.mixer.music.play()
        self.play_time()    # call function to get song length

    def stop_song(self):
        # Reset song slider and time bar
        time_bar.config(text='')
        song_slider.config(value=0)

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.selection_clear(tkinter.ACTIVE)

        # Set stop variable to True
        self.stop = True

    def pause_song(self):
        # pause
        if self.pause:
            pygame.mixer.music.unpause()
            self.pause = False
        # unpause
        else:
            pygame.mixer.music.pause()
            self.pause = True

    def random_song(self):
        # Reset song slider and time bar
        time_bar.config(text='')
        song_slider.config(value=0)

        rdm_number = random.randint(0, self.size() - 1)     # -1 because the size amount is not a valid index
        song = self.get([rdm_number])
        full_path_song = os.path.join(head_tail_path[0], song)
        pygame.mixer.music.load(full_path_song)
        pygame.mixer.music.play()

        self.selection_clear(0, tkinter.END)
        self.activate(rdm_number)
        self.selection_set(first=rdm_number, last=None)

    def next_song(self):
        # Reset song slider and time bar
        time_bar.config(text='')
        song_slider.config(value=0)

        # Get the current song number (returns tuple)
        current_song = self.curselection()
        next_s = current_song[0] + 1

        if self.shuffle:
            self.random_song()

        else:
            if next_s >= self.size():
                next_s = next_s - self.size()

            # Grab song title from playlist
            song = self.get(next_s)

            full_path_song = os.path.join(head_tail_path[0], song)

            pygame.mixer.music.load(full_path_song)
            pygame.mixer.music.play()

            self.selection_clear(0, tkinter.END)    # clear current selected song
            self.activate(next_s)   # underline the next song
            self.selection_set(first=next_s, last=None)  # None makes it so that only the line with index gets selected first)

    def previous_song(self):
        # Reset song slider and time bar
        time_bar.config(text='')
        song_slider.config(value=0)

        current_song = self.curselection()
        previous_s = current_song[0] - 1

        if self.shuffle:
            self.random_song()

        else:
            if previous_s < 0:
                previous_s = previous_s + self.size()

            song = self.get(previous_s)

            full_path_song = os.path.join(head_tail_path[0], song)

            pygame.mixer.music.load(full_path_song)
            pygame.mixer.music.play()

            self.selection_clear(0, tkinter.END)
            self.activate(previous_s)
            self.selection_set(first=previous_s, last=None)

    def remove_songs(self):
        selected_songs = self.curselection()
        for song in reversed(selected_songs):   # iterate backwards to keep correct index positions while deleting
            self.delete(song)
        self.selection_clear(0, tkinter.END)

    def repeat_song(self):
        self.stop = False

        if self.repeat:
            self.repeat = False
            repeat_button.config(image=repeat_b)

        else:
            self.repeat = True
            repeat_button.config(image=stop_repeat_b)

    def mute_sound(self):

        if self.mute:
            pygame.mixer.music.set_volume(1.0)
            volume_slider.set(100)
            mute_button.config(image=volume_b)
            self.mute = False
        else:
            pygame.mixer.music.set_volume(0.0)
            volume_slider.set(0)
            mute_button.config(image=mute_b)
            self.mute = True

    def shuffle_songs(self):
        if self.shuffle:
            self.shuffle = False
            shuffle_button.config(image=shuffle_b)

        else:
            self.shuffle = True
            shuffle_button.config(image=stop_shuffle_b)

    def play_time(self):
        if self.stop:
            return

        current_time = pygame.mixer.music.get_pos() / 1000

        # temp label to get data
        # slider_label.config(text=f'Slider: {int(song_slider.get())} and Song Pos: {int(current_time)}')

        # Use mutagen to determine song length
        current_song = self.get(tkinter.ACTIVE)
        full_song_path = os.path.join(head_tail_path[0], current_song)
        muta_song = MP3(full_song_path)

        global song_length
        self.song_length = muta_song.info.length     # in total seconds
        format_song_length = time.strftime('%M:%S', time.gmtime(self.song_length))

        current_time += 1

        if int(song_slider.get()) == int(self.song_length):
            time_bar.config(text=f" Elapsed time {format_song_length} / Total Duration {format_song_length} ")
            song_slider.set(value=0)    # Reset value when song is on repeat and reached end of song
            if self.shuffle:
                self.random_song()

            elif self.repeat:
                current_song = self.get(tkinter.ACTIVE)
                full_path_song = os.path.join(head_tail_path[0], current_song)
                pygame.mixer.music.load(full_path_song)
                pygame.mixer.music.play()

            else:
                self.next_song()

        elif self.pause:
            pass

        elif int(song_slider.get()) == int(current_time):
            # slider hasn't been moved
            slider_position = int(self.song_length)    # update slider
            song_slider.config(to=slider_position, value=int(current_time))   # update value to song length + start value set to 0

        else:
            # slider has been moved
            slider_position = int(self.song_length)    # update slider
            song_slider.config(to=slider_position, value=int(song_slider.get()))     # config slider to length of song

            # format time, gm time takes seconds as parameter
            formatted_time = time.strftime('%M:%S', time.gmtime(int(song_slider.get())))

            # set time elapsed in time bar
            time_bar.config(text=f" Elapsed time {formatted_time} / Total Duration {format_song_length} ")

            # Keep slider moving
            next_time = int(song_slider.get()) + 1

            song_slider.config(value=next_time)

        # Keeps updating the widget every second with `after` method
        time_bar.after(1000, self.play_time)

    def slide_song(self, event):

        song_selected = self.get(tkinter.ACTIVE)
        song_path = os.path.join(head_tail_path[0], song_selected)
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(start=int(song_slider.get()))

    @staticmethod
    def hold_slide(event):
        if song_slider:
            pygame.mixer.music.set_volume(0.0)

    @staticmethod
    def release_slide(event):
        pygame.mixer.music.set_volume(1.0)

    @staticmethod
    def slide_volume(x):
        pygame.mixer.music.set_volume(volume_slider.get())

        if pygame.mixer.music.get_volume() == 0.0:
            mute_button.config(image=mute_b)
        else:
            try:
                mute_button.config(image=volume_b)
            except NameError:
                pass

if __name__ == '__main__':

    root = tkinter.Tk()
    root.title('Swarmp3')
    root.geometry('1024x768')

    # Initialize Pygame Mixer / Needed to play song
    pygame.mixer.init()

    # Configuring columns
    root.columnconfigure(0, weight=7)
    root.columnconfigure(1, weight=3)

    # Configuring rows
    root.rowconfigure(0, weight=9)
    root.rowconfigure(1, weight=1)

    # Instantiate Musicplayer
    music_p = Musicplayer(root, bg='black', fg='yellow', selectbackground='grey', selectmode=tkinter.EXTENDED)
    music_p.grid(row=0, column=0, sticky='nsew', padx=20, pady=(20, 0))

    # Mp3 Player buttons
    play_b = tkinter.PhotoImage(file='Buttons/play.png')
    pause_b = tkinter.PhotoImage(file='Buttons/pause.png')
    stop_b = tkinter.PhotoImage(file='Buttons/stop.png')
    forward_b = tkinter.PhotoImage(file='Buttons/forward.png')
    backward_b = tkinter.PhotoImage(file='Buttons/backward.png')
    mute_b = tkinter.PhotoImage(file='Buttons/mute.png')
    volume_b = tkinter.PhotoImage(file='Buttons/volume.png')
    random_b = tkinter.PhotoImage(file='Buttons/random.png')
    repeat_b = tkinter.PhotoImage(file='Buttons/repeat.png')
    stop_repeat_b = tkinter.PhotoImage(file='Buttons/stop_repeat.png')
    shuffle_b = tkinter.PhotoImage(file='Buttons/shuffle.png')
    stop_shuffle_b = tkinter.PhotoImage(file='Buttons/stop_shuffle.png')

    # Player control frame
    controls_frame = tkinter.Frame(root)
    controls_frame.grid(row=1, column=0, sticky='s', pady=10)

    # Mp3 Player control buttons
    play_button = tkinter.Button(controls_frame, image=play_b, borderwidth=0, command=music_p.play_song).grid(row=0, column=2)
    pause_button = tkinter.Button(controls_frame, image=pause_b, borderwidth=0, command=music_p.pause_song).grid(row=0, column=4)
    stop_button = tkinter.Button(controls_frame, image=stop_b, borderwidth=0, command=music_p.stop_song).grid(row=0, column=0)
    forward_button = tkinter.Button(controls_frame, image=forward_b, borderwidth=0, command=music_p.next_song).grid(row=0, column=3)
    backward_button = tkinter.Button(controls_frame, image=backward_b, borderwidth=0, command=music_p.previous_song).grid(row=0, column=1)
    random_button = tkinter.Button(controls_frame, image=random_b, borderwidth=0, command=music_p.random_song).grid(row=1, column=4)
    repeat_button = tkinter.Button(controls_frame, image=repeat_b, borderwidth=0, command=music_p.repeat_song)
    repeat_button.grid(row=1, column=0)
    shuffle_button = tkinter.Button(controls_frame, image=shuffle_b, borderwidth=0, command=music_p.shuffle_songs)
    shuffle_button.grid(row=1, column=2)

    # Create menu
    menu = tkinter.Menu(root)
    root.config(menu=menu)

    # files menu
    file_menu = tkinter.Menu(menu, tearoff=False)
    menu.add_cascade(label='File', menu=file_menu)
    file_menu.add_command(label='Add Song(s)', command=music_p.add_song)

    # Volume Control Frame
    volume_frame = tkinter.Frame(root, background='green').grid(row=0, column=1, rowspan=2)

    # Volume slider
    vol_slider = tkinter.IntVar()
    volume_slider = ttk.Scale(volume_frame, from_=1, to=0, length=200, command=music_p.slide_volume, orient=tkinter.VERTICAL, variable=vol_slider)
    volume_slider.set(100)
    volume_slider.grid(row=1, column=1, sticky='ns')
    # volume_label = ttk.Label(volume_frame, textvariable=vol_slider).grid(row=1, column=1, sticky='w')
    mute_button = tkinter.Button(volume_frame, image=volume_b, borderwidth=0, command=music_p.mute_sound)
    mute_button.grid(row=2, column=1, sticky='n', pady=20)

    # Time Status
    time_bar = tkinter.Label(root, text='', borderwidth=1, relief='groove', anchor='e')
    time_bar.grid(column=0, sticky='sw', padx=5, pady=5, ipady=2)

    # Time slider played song
    song_slider = tkinter.ttk.Scale(root, from_=0, to=100, length=900, orient=tkinter.HORIZONTAL, value=0, command=music_p.slide_song)
    song_slider.grid(row=1, column=0, sticky='n')

    song_slider.bind('<Button-1>', music_p.hold_slide)     # Mute sound when sliding song
    song_slider.bind('<ButtonRelease-1>', music_p.release_slide)  # Put the volume back to 100%

    # #Create Temporary Slider Label
    # slider_label = tkinter.Label(root, text="0")
    # slider_label.grid(row=1, column=0, sticky='n', pady=20)

    root.mainloop()

