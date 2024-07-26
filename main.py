from tkinter import Tk
from src.gui.menu import InitWindow


def bring_window_on_top(win):
    win.attributes('-topmost', True)
    win.update()
    win.attributes('-topmost', False)


def init_starting_window():
    window = Tk()
    init_window = InitWindow(window)
    window.geometry("310x100")
    bring_window_on_top(window)
    window.title("Human Contact Annotator")
    window.mainloop()


def main():
    init_starting_window()


if __name__ == '__main__':
    main()
