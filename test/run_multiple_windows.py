import tkinter as tk


class TestWindow(tk.Toplevel):
    def __init__(self) -> None:
        super().__init__()
        self.geometry('150x150')
        newlabel = tk.Label(self, text="Settings Window")
        newlabel.pack()
        self.protocol("WM_DELETE_WINDOW", self.close_window)

    def close_window(self):
        print("kill")
        self.destroy()


def create_TestWindow():
    nn = TestWindow()


root = tk.Tk()
root.geometry('200x200')

myframe = tk.Frame(root)
myframe.pack()

mybutton = tk.Button(myframe, text="Settings", command=create_TestWindow)
mybutton.pack(pady=10)

root.mainloop()
