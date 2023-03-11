import io
import tkinter as tk
from time import time, sleep
from requests import request
from PIL import Image, ImageTk
from threading import Thread

HOST = "https://pno3cwb1.student.cs.kuleuven.be"
CASES = {
        "damBreak": "/opt/openfoam8/tutorials/multiphase/interFoam/laminar/damBreak/damBreak",
        "smallPoolFire2D": "/opt/openfoam8/tutorials/combustion/fireFoam/LES/smallPoolFire2D"
    }


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.inputframes = {}
        self.options = {}
        self.frames = []
        self.n = 1
        self.title("P&O3 CW-B")
        self.geometry("800x500")
        self.frame = tk.Frame(self, width=800, height=500)
        self.frame.pack_propagate(False)
        self.frame.pack()
        self.resizable(False, False)
        self.frame.columnconfigure(0, minsize=500, weight=5)
        self.frame.columnconfigure(1, minsize=300, weight=3)
        self.frame.rowconfigure(0, minsize=400, weight=40)
        self.frame.rowconfigure(1, minsize=100, weight=10)

        self.inputframe = tk.Frame(self.frame, width=300, height=400)
        self.inputframe.grid(column=1, row=0)

        dy, xmin, xmax = 40, 70, 200
        tk.Label(self.inputframe, text="Case").place(anchor=tk.CENTER, x=xmin, y=1*dy)
        self.case = tk.StringVar()
        self.case.set("damBreak")
        self.menu = tk.OptionMenu(self.inputframe, self.case, *CASES)
        self.menu.place(anchor=tk.CENTER, x=xmax, y=1*dy)
        self.case.trace("w", self.changeOptions)

        for case in CASES:
            self.inputframes[case] = tk.Frame(self.inputframe, width=300, height=240)
        self.changeOptions()

        tk.Label(self.inputframes["damBreak"], text="Hoogte dijk  (m)").place(anchor=tk.CENTER, x=xmin, y=2*dy - 65)
        self.hoogte_muur = tk.Scale(self.inputframes["damBreak"], from_=0.1, to=3.5, orient=tk.HORIZONTAL, resolution=0.01)
        self.hoogte_muur.set(0.64)
        self.hoogte_muur.place(anchor=tk.CENTER, x=xmax, y=2*dy - 65)
        tk.Button(self.inputframes["damBreak"], bg="red", width=2, height=1, command=lambda: self.hoogte_muur.set(0.64)).place(anchor=tk.CENTER, x=280, y=2*dy - 60)

        tk.Label(self.inputframes["damBreak"], text="Breedte dijk  (m)").place(anchor=tk.CENTER, x=xmin, y=3*dy - 65)
        self.breedte_muur = tk.Scale(self.inputframes["damBreak"], from_=0.1, to=1.9, orient=tk.HORIZONTAL, resolution=0.01)
        self.breedte_muur.set(0.32)
        self.breedte_muur.place(anchor=tk.CENTER, x=xmax, y=3*dy - 65)
        tk.Button(self.inputframes["damBreak"], bg="red", width=2, height=1, command=lambda: self.breedte_muur.set(0.32)).place(anchor=tk.CENTER, x=280, y=3*dy - 60)

        tk.Label(self.inputframes["damBreak"], text="Verschuiving dijk  (m)").place(anchor=tk.CENTER, x=xmin, y=4*dy - 65)
        self.verschuiving_muur = tk.Scale(self.inputframes["damBreak"], from_=-1, to=1, orient=tk.HORIZONTAL, resolution=0.01)
        self.verschuiving_muur.set(0)
        self.verschuiving_muur.place(anchor=tk.CENTER, x=xmax, y=4*dy - 65)
        tk.Button(self.inputframes["damBreak"], bg="red", width=2, height=1, command=lambda: self.verschuiving_muur.set(0)).place(anchor=tk.CENTER, x=280, y=4*dy - 60)

        tk.Label(self.inputframes["damBreak"], text="Hoogte water  (m)").place(anchor=tk.CENTER, x=xmin, y=5*dy - 65)
        self.hoogte_water = tk.Scale(self.inputframes["damBreak"], from_=0.1, to=4, orient=tk.HORIZONTAL, resolution=0.01)
        self.hoogte_water.set(2)
        self.hoogte_water.place(anchor=tk.CENTER, x=xmax, y=5*dy - 65)
        tk.Button(self.inputframes["damBreak"], bg="red", width=2, height=1, command=lambda: self.hoogte_water.set(2)).place(anchor=tk.CENTER, x=280, y=5*dy - 60)

        tk.Label(self.inputframes["damBreak"], text="Breedte water  (m)").place(anchor=tk.CENTER, x=xmin, y=6*dy - 65)
        self.breedte_water = tk.Scale(self.inputframes["damBreak"], from_=0.1, to=4, orient=tk.HORIZONTAL, resolution=0.01)
        self.breedte_water.set(0.5)
        self.breedte_water.place(anchor=tk.CENTER, x=xmax, y=6*dy - 65)
        tk.Button(self.inputframes["damBreak"], bg="red", width=2, height=1, command=lambda: self.breedte_water.set(0.5)).place(anchor=tk.CENTER, x=280, y=6*dy - 60)

        tk.Label(self.inputframes["damBreak"], text="Lengte video  (s)").place(anchor=tk.CENTER, x=xmin, y=7*dy - 65)
        self.lengte_db = tk.Scale(self.inputframes["damBreak"], from_=1, to=5, orient=tk.HORIZONTAL, resolution=1)
        self.lengte_db.set(2)
        self.lengte_db.place(anchor=tk.CENTER, x=xmax, y=7*dy - 65)
        tk.Button(self.inputframes["damBreak"], bg="red", width=2, height=1, command=lambda: self.lengte_db.set(2)).place(anchor=tk.CENTER, x=280, y=7*dy - 60)

        tk.Label(self.inputframes["smallPoolFire2D"], text="Lengte video  (s)").place(anchor=tk.CENTER, x=xmin, y=2*dy - 65)
        self.lengte_spf = tk.Scale(self.inputframes["smallPoolFire2D"], from_=1, to=5, orient=tk.HORIZONTAL, resolution=1)
        self.lengte_spf.set(2)
        self.lengte_spf.place(anchor=tk.CENTER, x=xmax, y=2*dy - 65)
        tk.Button(self.inputframes["smallPoolFire2D"], bg="red", width=2, height=1, command=lambda: self.lengte_spf.set(2)).place(anchor=tk.CENTER, x=280, y=2*dy - 60)

        tk.Label(self.inputframes["smallPoolFire2D"], text="Parameter").place(anchor=tk.CENTER, x=xmin, y=3*dy - 65)
        self.param = tk.StringVar()
        self.param.set("T")
        self.menu = tk.OptionMenu(self.inputframes["smallPoolFire2D"], self.param, "T", "CH4", "CO2", "H2O", "N2", "O2")
        self.menu.place(anchor=tk.CENTER, x=xmax, y=3*dy - 65)
        tk.Button(self.inputframes["smallPoolFire2D"], bg="red", width=2, height=1, command=lambda: self.param.set("T")).place(anchor=tk.CENTER, x=280, y=3 * dy - 60)

        self.button = tk.Button(self.inputframe, text="RUN", command=self.send_command, width=30, height=2)
        self.button.place(anchor=tk.CENTER, x=150, y=350)

        self.text = tk.StringVar()
        self.outtekst = tk.Label(self.frame, height=7, wraplength=300, textvariable=self.text,
                                 width=42, justify=tk.LEFT, anchor=tk.NW, relief="groove")
        self.outtekst.grid(column=1, row=1)

        self.image = tk.Label(self.frame, width=500, height=500, relief="groove")
        self.showStartImage()
        self.image.grid(column=0, row=0, rowspan=2)

    def changeOptions(self, *_):
        for case in self.inputframes:
            inputframe = self.inputframes[case]
            if case == self.case.get():
                inputframe.place(x=0, y=60)
            else:
                inputframe.place_forget()

    def showStartImage(self):
        Thread(target=self.renderer, daemon=True).start()

    def send_command(self):
        def verbind():
            try:
                cmd = CASES[self.case.get()]
                if self.case.get() == "damBreak":
                    cmd = "\n".join([cmd, str(self.hoogte_water.get()), str(self.breedte_water.get()), str(self.breedte_muur.get()), str(self.hoogte_muur.get()), str(self.verschuiving_muur.get()), str(self.lengte_db.get())])
                elif self.case.get() == "smallPoolFire2D":
                    cmd = "\n".join([cmd, str(self.lengte_spf.get()), str(self.param.get())])
                self.button.config(state=tk.DISABLED)
                self.clear_output()
                self.add_output("Opdracht versturen naar server...")
                begin = int(time() * 1000)
                req = request("POST", HOST, data=cmd, stream=True)
                self.add_output(f"Berekeningen ontvangen ({int(time() * 1000) - begin} ms)")
                self.add_output("Afbeelding renderen...")
                r = req.content
                self.frames = []
                gif = Image.open(io.BytesIO(r))
                for n in range(gif.n_frames):
                    gif.seek(n)
                    self.showImage(gif)

                self.add_output("Afbeelding gerenderd")
            except:
                self.add_output("Er is een fout opgetreden")
            self.button.config(state=tk.NORMAL)
        Thread(target=verbind, daemon=True).start()

    def clear_output(self):
        self.text.set("")
        self.outtekst.update()

    def add_output(self, text):
        self.text.set(self.text.get() + text + "\n")
        self.outtekst.update()

    def showImage(self, i):
        width, height = i.size
        r = height/width
        if height == width:
            height = width = 500
        elif height > width:
            height = 500
            width = height/r
        else:
            width = 500
            height = r*width
        i = i.resize((int(width), int(height)))
        im = ImageTk.PhotoImage(i)
        self.frames.append(im)

    def renderer(self):
        frame = 0
        while True:
            if frame >= len(self.frames):
                frame = 0
                sleep(0.1)
                continue
            im = self.frames[frame]
            self.image.configure(image=im)
            self.image.image = im
            self.image.update()
            self.update()
            sleep(0.05)
            frame += 1


myapp = App()
myapp.mainloop()
