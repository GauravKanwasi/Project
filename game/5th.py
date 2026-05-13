import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
import os
from PIL import Image, ImageTk, ImageDraw, ImageGrab
import io


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drawing App")
        self.root.geometry("1100x750")
        self.root.minsize(800, 600)
        self.root.configure(bg="#1e1e2e")

        self.current_color = "#f8f8f2"
        self.bg_color = "#1e1e2e"
        self.line_width = 4
        self.prev_x = None
        self.prev_y = None
        self.drawing_mode = "pen"
        self.temp_item = None
        self.fill_var = tk.BooleanVar(value=False)
        self.brush_shape = tk.StringVar(value="round")

        self.canvas_width = 1400
        self.canvas_height = 900
        self.pil_image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.pil_draw = ImageDraw.Draw(self.pil_image)

        self.history = []
        self.redo_stack = []

        self._build_ui()
        self._setup_bindings()
        self.set_mode("pen")
        self._save_state()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e2e")
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 9))
        style.configure("TButton", background="#313244", foreground="#cdd6f4",
                        font=("Segoe UI", 9), borderwidth=0, focuscolor="none")
        style.map("TButton",
                  background=[("active", "#45475a"), ("pressed", "#585b70")],
                  foreground=[("active", "#cdd6f4")])
        style.configure("TCheckbutton", background="#1e1e2e", foreground="#cdd6f4",
                        font=("Segoe UI", 9))
        style.map("TCheckbutton", background=[("active", "#1e1e2e")])
        style.configure("TCombobox", fieldbackground="#313244", background="#313244",
                        foreground="#cdd6f4", font=("Segoe UI", 9))
        style.configure("TScale", background="#1e1e2e", troughcolor="#313244")

        outer = ttk.Frame(self.root)
        outer.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        tb = tk.Frame(outer, bg="#181825", padx=6, pady=6)
        tb.pack(side=tk.TOP, fill=tk.X)

        tools = [
            ("✏ Pen", "pen"),
            ("╲ Line", "line"),
            ("▭ Rect", "rectangle"),
            ("○ Oval", "oval"),
            ("◻ Eraser", "eraser"),
            ("T Text", "text"),
        ]
        self.tool_btns = {}
        for label, mode in tools:
            b = tk.Button(
                tb, text=label, bg="#313244", fg="#cdd6f4",
                activebackground="#89b4fa", activeforeground="#1e1e2e",
                font=("Segoe UI", 9), relief=tk.FLAT, padx=8, pady=4, bd=0,
                command=lambda m=mode: self.set_mode(m)
            )
            b.pack(side=tk.LEFT, padx=2)
            self.tool_btns[mode] = b

        sep = tk.Frame(tb, width=1, bg="#45475a")
        sep.pack(side=tk.LEFT, padx=8, fill=tk.Y)

        tk.Label(tb, text="Size:", bg="#181825", fg="#a6adc8",
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.size_slider = tk.Scale(
            tb, from_=1, to=80, orient=tk.HORIZONTAL, length=100,
            command=self._change_width, showvalue=True,
            bg="#181825", fg="#cdd6f4", troughcolor="#313244",
            highlightthickness=0, bd=0, sliderrelief=tk.FLAT,
            font=("Segoe UI", 8)
        )
        self.size_slider.set(self.line_width)
        self.size_slider.pack(side=tk.LEFT, padx=4)

        sep2 = tk.Frame(tb, width=1, bg="#45475a")
        sep2.pack(side=tk.LEFT, padx=8, fill=tk.Y)

        tk.Label(tb, text="Brush:", bg="#181825", fg="#a6adc8",
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.brush_var = tk.StringVar(value="round")
        for val in ("round", "square"):
            rb = tk.Radiobutton(
                tb, text=val, variable=self.brush_var, value=val,
                bg="#181825", fg="#cdd6f4", selectcolor="#313244",
                activebackground="#181825", activeforeground="#89b4fa",
                font=("Segoe UI", 9), indicatoron=1
            )
            rb.pack(side=tk.LEFT, padx=2)

        sep3 = tk.Frame(tb, width=1, bg="#45475a")
        sep3.pack(side=tk.LEFT, padx=8, fill=tk.Y)

        self.color_preview = tk.Canvas(tb, width=30, height=24, bg=self.current_color,
                                       highlightthickness=1, highlightbackground="#585b70",
                                       cursor="hand2")
        self.color_preview.pack(side=tk.LEFT, padx=4)
        self.color_preview.bind("<Button-1>", lambda e: self.choose_color())

        clr_btn = tk.Button(
            tb, text="Color", bg="#313244", fg="#cdd6f4",
            activebackground="#89b4fa", activeforeground="#1e1e2e",
            font=("Segoe UI", 9), relief=tk.FLAT, padx=8, pady=4, bd=0,
            command=self.choose_color
        )
        clr_btn.pack(side=tk.LEFT, padx=2)

        palette = ["#f38ba8", "#fab387", "#f9e2af", "#a6e3a1",
                   "#89dceb", "#89b4fa", "#cba6f7", "#f8f8f2", "#313244", "#11111b"]
        for c in palette:
            b = tk.Button(
                tb, bg=c, width=2, height=1, relief=tk.FLAT, bd=0,
                cursor="hand2", command=lambda x=c: self.set_color(x)
            )
            b.pack(side=tk.LEFT, padx=1)

        sep4 = tk.Frame(tb, width=1, bg="#45475a")
        sep4.pack(side=tk.LEFT, padx=8, fill=tk.Y)

        self.fill_cb = tk.Checkbutton(
            tb, text="Fill", variable=self.fill_var,
            bg="#181825", fg="#cdd6f4", selectcolor="#313244",
            activebackground="#181825", activeforeground="#89b4fa",
            font=("Segoe UI", 9)
        )
        self.fill_cb.pack(side=tk.LEFT, padx=4)

        sep5 = tk.Frame(tb, width=1, bg="#45475a")
        sep5.pack(side=tk.LEFT, padx=8, fill=tk.Y)

        for label, cmd in [("Undo", self.undo), ("Redo", self.redo), ("Clear", self.clear_canvas)]:
            tk.Button(
                tb, text=label, bg="#313244", fg="#cdd6f4",
                activebackground="#45475a", activeforeground="#cdd6f4",
                font=("Segoe UI", 9), relief=tk.FLAT, padx=8, pady=4, bd=0,
                command=cmd
            ).pack(side=tk.LEFT, padx=2)

        for label, cmd in [("Save", self.save_drawing), ("Load", self.load_drawing)]:
            tk.Button(
                tb, text=label, bg="#89b4fa", fg="#1e1e2e",
                activebackground="#b4befe", activeforeground="#1e1e2e",
                font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=4, bd=0,
                command=cmd
            ).pack(side=tk.RIGHT, padx=2)

        cf = tk.Frame(outer, bg="#1e1e2e")
        cf.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        self.v_scroll = ttk.Scrollbar(cf, orient=tk.VERTICAL)
        self.h_scroll = ttk.Scrollbar(cf, orient=tk.HORIZONTAL)
        self.canvas = tk.Canvas(
            cf, bg="white", cursor="crosshair",
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set,
            highlightthickness=0
        )
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        cf.grid_rowconfigure(0, weight=1)
        cf.grid_columnconfigure(0, weight=1)
        self.canvas.config(scrollregion=(0, 0, self.canvas_width, self.canvas_height))

        self.status_var = tk.StringVar(value="Mode: Pen  |  Size: 4  |  Ready")
        sb = tk.Label(
            self.root, textvariable=self.status_var,
            bg="#11111b", fg="#a6adc8", anchor=tk.W,
            font=("Segoe UI", 8), padx=8, pady=3
        )
        sb.pack(side=tk.BOTTOM, fill=tk.X)

        ctx = tk.Menu(self.canvas, tearoff=0, bg="#313244", fg="#cdd6f4",
                      activebackground="#45475a", activeforeground="#cdd6f4")
        ctx.add_command(label="Undo  Ctrl+Z", command=self.undo)
        ctx.add_command(label="Redo  Ctrl+Y", command=self.redo)
        ctx.add_separator()
        ctx.add_command(label="Clear Canvas", command=self.clear_canvas)
        ctx.add_separator()
        ctx.add_command(label="Pick Color", command=self.choose_color)
        self.ctx_menu = ctx

    def _setup_bindings(self):
        self.canvas.bind("<Button-1>", self._mouse_down)
        self.canvas.bind("<B1-Motion>", self._mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._mouse_up)
        self.canvas.bind("<Button-3>", lambda e: self.ctx_menu.post(e.x_root, e.y_root))
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-s>", lambda e: self.save_drawing())
        self.root.bind("<Control-o>", lambda e: self.load_drawing())
        self.root.bind("<Escape>", lambda e: self._cancel())

    def _cx(self, x):
        return self.canvas.canvasx(x)

    def _cy(self, y):
        return self.canvas.canvasy(y)

    def _mouse_down(self, event):
        self.start_x = self._cx(event.x)
        self.start_y = self._cy(event.y)
        self.prev_x = self.start_x
        self.prev_y = self.start_y
        self.temp_item = None

        mode = self.drawing_mode
        if mode == "line":
            self.temp_item = self.canvas.create_line(
                self.start_x, self.start_y, self.start_x, self.start_y,
                fill=self.current_color, width=self.line_width,
                capstyle=tk.ROUND
            )
        elif mode == "rectangle":
            fill = self.current_color if self.fill_var.get() else ""
            self.temp_item = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline=self.current_color, fill=fill, width=self.line_width
            )
        elif mode == "oval":
            fill = self.current_color if self.fill_var.get() else ""
            self.temp_item = self.canvas.create_oval(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline=self.current_color, fill=fill, width=self.line_width
            )
        elif mode == "pen":
            self._draw_dot(self.start_x, self.start_y, self.current_color)
        elif mode == "eraser":
            self._draw_dot(self.start_x, self.start_y, "white")
        elif mode == "text":
            self._text_dialog(self.start_x, self.start_y)

    def _draw_dot(self, x, y, color):
        r = self.line_width / 2
        if self.brush_var.get() == "round":
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline=color)
        else:
            self.canvas.create_rectangle(x-r, y-r, x+r, y+r, fill=color, outline=color)
        self._pil_dot(x, y, color)

    def _pil_dot(self, x, y, color):
        r = self.line_width / 2
        if self.brush_var.get() == "round":
            self.pil_draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
        else:
            self.pil_draw.rectangle([x-r, y-r, x+r, y+r], fill=color)

    def _mouse_drag(self, event):
        x = self._cx(event.x)
        y = self._cy(event.y)
        mode = self.drawing_mode

        if mode in ("pen", "eraser"):
            color = self.current_color if mode == "pen" else "white"
            cap = tk.ROUND if self.brush_var.get() == "round" else tk.PROJECTING
            if self.prev_x is not None:
                self.canvas.create_line(
                    self.prev_x, self.prev_y, x, y,
                    fill=color, width=self.line_width,
                    capstyle=cap, smooth=True, joinstyle=tk.ROUND
                )
                self.pil_draw.line(
                    [self.prev_x, self.prev_y, x, y],
                    fill=color,
                    width=self.line_width
                )
            self.prev_x, self.prev_y = x, y

        elif mode == "line" and self.temp_item:
            self.canvas.coords(self.temp_item, self.start_x, self.start_y, x, y)

        elif mode == "rectangle" and self.temp_item:
            self.canvas.coords(self.temp_item, self.start_x, self.start_y, x, y)

        elif mode == "oval" and self.temp_item:
            self.canvas.coords(self.temp_item, self.start_x, self.start_y, x, y)

    def _mouse_up(self, event):
        x = self._cx(event.x)
        y = self._cy(event.y)
        mode = self.drawing_mode

        if mode == "line" and self.temp_item:
            coords = self.canvas.coords(self.temp_item)
            self.pil_draw.line(coords, fill=self.current_color, width=self.line_width)

        elif mode == "rectangle" and self.temp_item:
            coords = self.canvas.coords(self.temp_item)
            fill = self.current_color if self.fill_var.get() else None
            self.pil_draw.rectangle(coords, outline=self.current_color, fill=fill,
                                    width=self.line_width)

        elif mode == "oval" and self.temp_item:
            coords = self.canvas.coords(self.temp_item)
            fill = self.current_color if self.fill_var.get() else None
            self.pil_draw.ellipse(coords, outline=self.current_color, fill=fill,
                                  width=self.line_width)

        self.temp_item = None
        self.prev_x = None
        self.prev_y = None
        self._save_state()

    def _text_dialog(self, cx, cy):
        dlg = tk.Toplevel(self.root)
        dlg.title("Add Text")
        dlg.configure(bg="#1e1e2e")
        dlg.geometry("320x180")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text="Text:", bg="#1e1e2e", fg="#cdd6f4",
                 font=("Segoe UI", 10)).pack(pady=(14, 2))
        entry = tk.Entry(dlg, font=("Segoe UI", 11), bg="#313244", fg="#f8f8f2",
                         insertbackground="#f8f8f2", relief=tk.FLAT, bd=4)
        entry.pack(pady=2, padx=20, fill=tk.X)
        entry.focus_set()

        size_frame = tk.Frame(dlg, bg="#1e1e2e")
        size_frame.pack(pady=6)
        tk.Label(size_frame, text="Size:", bg="#1e1e2e", fg="#cdd6f4",
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=4)
        size_var = tk.IntVar(value=16)
        sizes = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 64]
        cb = ttk.Combobox(size_frame, values=sizes, textvariable=size_var, width=5,
                          font=("Segoe UI", 9))
        cb.pack(side=tk.LEFT)

        def confirm(e=None):
            txt = entry.get().strip()
            if txt:
                fs = size_var.get()
                self.canvas.create_text(
                    cx, cy, text=txt, fill=self.current_color,
                    font=("Segoe UI", fs), anchor=tk.NW
                )
                self.pil_draw.text((cx, cy), txt, fill=self.current_color)
                self._save_state()
            dlg.destroy()

        entry.bind("<Return>", confirm)
        tk.Button(
            dlg, text="Add Text", command=confirm,
            bg="#89b4fa", fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT, padx=12, pady=6, bd=0,
            activebackground="#b4befe", activeforeground="#1e1e2e"
        ).pack(pady=8)

        dlg.update_idletasks()
        dlg.geometry(f"+{self.root.winfo_x() + self.root.winfo_width()//2 - 160}"
                     f"+{self.root.winfo_y() + self.root.winfo_height()//2 - 90}")

    def set_mode(self, mode):
        self.drawing_mode = mode
        colors = {"pen": "#89b4fa", "line": "#a6e3a1", "rectangle": "#f9e2af",
                  "oval": "#cba6f7", "eraser": "#f38ba8", "text": "#fab387"}
        for m, b in self.tool_btns.items():
            if m == mode:
                b.config(bg=colors.get(m, "#89b4fa"), fg="#1e1e2e")
            else:
                b.config(bg="#313244", fg="#cdd6f4")
        self.fill_cb.config(state=tk.NORMAL if mode in ("rectangle", "oval") else tk.DISABLED)
        self.status_var.set(f"Mode: {mode.capitalize()}  |  Size: {self.line_width}  |  Color: {self.current_color}")

    def _change_width(self, val):
        self.line_width = max(1, int(float(val)))
        self.status_var.set(f"Mode: {self.drawing_mode.capitalize()}  |  Size: {self.line_width}  |  Color: {self.current_color}")

    def choose_color(self):
        result = colorchooser.askcolor(color=self.current_color, parent=self.root)
        if result[1]:
            self.set_color(result[1])

    def set_color(self, color):
        self.current_color = color
        self.color_preview.config(bg=color)
        self.status_var.set(f"Mode: {self.drawing_mode.capitalize()}  |  Size: {self.line_width}  |  Color: {color}")

    def clear_canvas(self):
        if messagebox.askyesno("Clear", "Clear the canvas?", parent=self.root):
            self.canvas.delete("all")
            self.pil_image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            self._save_state()
            self.status_var.set("Canvas cleared")

    def save_drawing(self):
        ftypes = [("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("BMP Image", "*.bmp")]
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=ftypes,
                                            parent=self.root)
        if path:
            try:
                self.pil_image.save(path)
                self.status_var.set(f"Saved: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e), parent=self.root)

    def load_drawing(self):
        ftypes = [("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All Files", "*.*")]
        path = filedialog.askopenfilename(filetypes=ftypes, parent=self.root)
        if path:
            try:
                img = Image.open(path).convert("RGB")
                self.pil_image = img.resize((self.canvas_width, self.canvas_height),
                                            Image.LANCZOS)
                self.pil_draw = ImageDraw.Draw(self.pil_image)
                self._refresh_canvas_from_pil()
                self._save_state()
                self.status_var.set(f"Loaded: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Load Error", str(e), parent=self.root)

    def _refresh_canvas_from_pil(self):
        self.canvas.delete("all")
        self._tk_img = ImageTk.PhotoImage(self.pil_image)
        self.canvas.create_image(0, 0, image=self._tk_img, anchor=tk.NW)

    def _save_state(self):
        snapshot = self.pil_image.copy()
        self.history.append(snapshot)
        if len(self.history) > 60:
            self.history.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.pil_image = self.history[-1].copy()
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            self._refresh_canvas_from_pil()
            self.status_var.set("Undo")

    def redo(self):
        if self.redo_stack:
            snap = self.redo_stack.pop()
            self.history.append(snap)
            self.pil_image = snap.copy()
            self.pil_draw = ImageDraw.Draw(self.pil_image)
            self._refresh_canvas_from_pil()
            self.status_var.set("Redo")

    def _cancel(self):
        if self.temp_item:
            self.canvas.delete(self.temp_item)
            self.temp_item = None


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
