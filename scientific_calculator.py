import tkinter as tk
from tkinter import ttk, simpledialog
import math

class CustomRenameDialog(tk.Toplevel):
    """A custom dark-mode dialog for renaming tabs."""
    def __init__(self, parent, title, initialvalue=""):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result = None

        # Style
        self.configure(bg='#2d2d2d')
        
        # Widgets
        self.label = tk.Label(self, text="Enter new name for the tab:", bg='#2d2d2d', fg='white', font=('Arial', 10))
        self.label.pack(padx=20, pady=(20, 10))

        self.entry = tk.Entry(self, bg='#1a1a1a', fg='white', insertbackground='white', relief='flat', font=('Arial', 10), width=30)
        self.entry.insert(0, initialvalue)
        self.entry.pack(padx=20, pady=10)
        self.entry.focus_set()

        button_frame = tk.Frame(self, bg='#2d2d2d')
        button_frame.pack(pady=(10, 20))

        self.ok_button = tk.Button(button_frame, text="OK", command=self.on_ok, bg='#4CAF50', fg='white', relief='flat', width=10)
        self.ok_button.pack(side='left', padx=10)

        self.cancel_button = tk.Button(button_frame, text="Cancel", command=self.on_cancel, bg='#5d5d5d', fg='white', relief='flat', width=10)
        self.cancel_button.pack(side='left', padx=10)

        self.bind("<Return>", lambda event: self.on_ok())
        self.bind("<Escape>", lambda event: self.on_cancel())

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.grab_set()
        self.wait_window(self)

    def on_ok(self):
        self.result = self.entry.get()
        self.destroy()

    def on_cancel(self):
        self.destroy()

class CalculatorTab(ttk.Frame):
    """
    Represents a single calculator instance within a tab.
    All the UI elements and logic for a single calculator are contained here.
    """
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app # Reference to the main application
        
        self.configure(style='Dark.TFrame')

        # Each tab needs its own result variable
        self.result_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the display row
        display_frame = tk.Frame(self, bg=self.app.dark_bg)
        display_frame.grid(row=0, column=0, columnspan=5, padx=10, pady=(20, 15), sticky='nsew')

        # Result display
        self.entry = tk.Entry(
            display_frame,
            textvariable=self.result_var,
            font=('Arial', 20, 'bold'),
            bd=4,
            insertwidth=2,
            width=14,
            borderwidth=0,
            bg=self.app.entry_bg,
            fg=self.app.entry_fg,
            justify='right',
            relief='flat'
        )
        self.entry.pack(side='left', fill='both', expand=True)
        self.entry.bind("<Return>", lambda event: self.calculate_result())
        self.entry.bind("<Button-3>", lambda event: self.paste_from_clipboard())

        # Copy button
        copy_btn = tk.Button(
            display_frame,
            text='Copy',
            padx=12,
            pady=5,
            font=('Arial', 10, 'bold'),
            bg=self.app.copy_button_bg,
            fg=self.app.button_fg,
            activebackground=self.app.active_bg,
            activeforeground=self.app.button_fg,
            relief='flat',
            borderwidth=0,
            command=self.copy_to_clipboard
        )
        copy_btn.pack(side='right', fill='y', padx=(5,0))

        # Button layout
        buttons = [
            ('C', 1, 0), ('(', 1, 1), (')', 1, 2), ('/', 1, 3), ('DEL', 1, 4),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('*', 2, 3), ('^', 2, 4),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3), ('sqrt', 3, 4),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3), ('%', 4, 4),
            ('0', 5, 0), ('.', 5, 1), ('±', 5, 2), ('=', 5, 3), ('π', 5, 4),
            ('sin', 6, 0), ('cos', 6, 1), ('tan', 6, 2), ('log', 6, 3), ('ln', 6, 4),
        ]

        # Button creation
        for text, row, col in buttons:
            if text == '=':
                bg = self.app.equals_button_bg
            elif text == 'C':
                bg = self.app.clear_button_bg
            elif text in ['sin', 'cos', 'tan', 'log', 'ln', 'sqrt', 'π', 'DEL', '^', '%']:
                bg = self.app.special_button_bg
            else:
                bg = self.app.button_bg

            button = tk.Button(
                self,
                text=text,
                padx=10,
                pady=10,
                font=('Arial', 12, 'bold'),
                bg=bg,
                fg=self.app.button_fg,
                activebackground=self.app.active_bg,
                activeforeground=self.app.button_fg,
                relief='flat',
                borderwidth=0,
                command=lambda t=text: self.on_button_click(t)
            )
            button.grid(row=row, column=col, padx=3, pady=3, sticky=tk.NSEW)

        # Grid configuration for this tab (frame)
        for i in range(7):
            self.grid_rowconfigure(i, weight=1)
        for i in range(5):
            self.grid_columnconfigure(i, weight=1)
            
    def show_notification(self, message, duration=1500):
        # Access the main app's notification method
        self.app.show_notification(message, duration)

    def copy_to_clipboard(self):
        result = self.result_var.get()
        if result:
            self.master.clipboard_clear()
            self.master.clipboard_append(result)
            self.show_notification("Copied to clipboard")
        else:
            self.show_notification("Nothing to copy", 2000)

    def paste_from_clipboard(self):
        try:
            clipboard_content = self.master.clipboard_get()
            if clipboard_content:
                self.result_var.set(self.result_var.get() + clipboard_content)
                self.show_notification("Pasted from clipboard")
            else:
                self.show_notification("Clipboard is empty", 2000)
        except tk.TclError:
            self.show_notification("No content in clipboard", 2000)
        return "break"

    def on_button_click(self, char):
        current_text = self.result_var.get()
        
        if char == 'C':
            self.result_var.set('')
        elif char == 'DEL':
            self.result_var.set(current_text[:-1])
        elif char == '±':
            if current_text and current_text.startswith('-'):
                self.result_var.set(current_text[1:])
            else:
                self.result_var.set('-' + current_text)
        elif char == 'π':
            self.result_var.set(current_text + str(math.pi))
        elif char == '=':
            self.calculate_result()
        elif char == 'sqrt':
            try:
                self.result_var.set(math.sqrt(float(current_text)))
            except (ValueError, TypeError):
                self.result_var.set('Error')
        elif char in ['sin', 'cos', 'tan', 'log', 'ln']:
            try:
                value = float(current_text)
                if char == 'sin': result = math.sin(math.radians(value))
                elif char == 'cos': result = math.cos(math.radians(value))
                elif char == 'tan': result = math.tan(math.radians(value))
                elif char == 'log': result = math.log10(value)
                elif char == 'ln': result = math.log(value)
                self.result_var.set(result)
            except (ValueError, TypeError):
                self.result_var.set('Error')
        else:
            self.result_var.set(current_text + char)

    def calculate_result(self):
        try:
            expression = self.result_var.get().replace('^', '**').replace('%', '/100')
            result = eval(expression, {"__builtins__": None}, {"math": math, "pi": math.pi})
            final_result = int(result) if isinstance(result, float) and result.is_integer() else result
            self.app.add_to_history(expression, final_result)
            self.result_var.set(final_result)
        except Exception:
            self.result_var.set('Error')


class TabbedCalculatorApp:
    """
    The main application window that holds the tabbed interface (Notebook).
    """
    def __init__(self, master):
        self.master = master
        master.overrideredirect(True)
        master.geometry("450x600+200+200")
        
        self.dark_bg = '#2d2d2d'
        self.button_bg = '#3d3d3d'
        self.button_fg = '#ffffff'
        self.active_bg = '#505050'
        self.entry_bg = '#1a1a1a'
        self.entry_fg = '#ffffff'
        self.special_button_bg = '#404040'
        self.equals_button_bg = '#4CAF50'
        self.clear_button_bg = '#ff4444'
        self.copy_button_bg = '#5d5d5d'

        self.master.configure(bg=self.dark_bg)

        # State variables
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._is_fullscreen = False
        self._resize_grip_size = 8
        self._is_resizing = False
        self._sidebar_job = None
        self._toast_job = None
        self._toast_label = None
        self.calculation_history = []
        self.history_window = None
        self._sidebar_close_job = None
        # MODIFICATION START: Change sidebar to be a Toplevel window
        self.sidebar_window = None 
        # MODIFICATION END

        # Main container
        self.container = tk.Frame(master, bg=self.dark_bg)
        self.container.pack(fill='both', expand=True)

        # Custom title bar
        self.title_bar = tk.Frame(self.container, bg='#1e1e1e', height=30)
        
        # --- Title Bar Widgets ---
        close_button = self.create_title_bar_button('✕', master.destroy, hover_color='#ff4444')
        close_button.pack(side='right', padx=5, pady=2)
        
        fullscreen_canvas = tk.Canvas(self.title_bar, width=20, height=20, bg='#1e1e1e', bd=0, highlightthickness=0)
        fullscreen_canvas.create_rectangle(5, 5, 15, 15, outline='white', width=1)
        fullscreen_canvas.pack(side='right', padx=5, pady=5)
        fullscreen_canvas.bind("<Button-1>", self.toggle_fullscreen)

        minimize_canvas = tk.Canvas(self.title_bar, width=20, height=20, bg='#1e1e1e', bd=0, highlightthickness=0)
        minimize_canvas.create_line(5, 10, 15, 10, fill='white', width=1)
        minimize_canvas.pack(side='right', padx=5, pady=5)
        minimize_canvas.bind("<Button-1>", self.minimize_window)

        title_label = tk.Label(self.title_bar, text="Zenth ", bg='#1e1e1e', fg='white')
        title_label.pack(side='left', padx=10)

        # Bind dragging events
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        title_label.bind("<ButtonPress-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.do_move)
        
        # Bind hover events for the control buttons
        fullscreen_canvas.bind("<Enter>", lambda e: e.widget.config(bg='#505050'))
        fullscreen_canvas.bind("<Leave>", lambda e: e.widget.config(bg='#1e1e1e'))
        minimize_canvas.bind("<Enter>", lambda e: e.widget.config(bg='#505050'))
        minimize_canvas.bind("<Leave>", lambda e: e.widget.config(bg='#1e1e1e'))

        # Main content frame
        self.main_frame = tk.Frame(self.container, bg=self.dark_bg)
        self.main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.configure_styles()
        
        # This container will use a grid layout to prevent the layout issues.
        top_container = tk.Frame(self.main_frame, bg=self.dark_bg)
        top_container.pack(fill='both', expand=True)
        top_container.grid_rowconfigure(0, weight=1)
        top_container.grid_columnconfigure(1, weight=1)

        # Create the menu button (hamburger icon)
        menu_button = tk.Canvas(top_container, width=30, height=30, bg=self.dark_bg, bd=0, highlightthickness=0, cursor="hand2")
        menu_button.create_line(8, 10, 22, 10, fill='white', width=2)
        menu_button.create_line(8, 15, 22, 15, fill='white', width=2)
        menu_button.create_line(8, 20, 22, 20, fill='white', width=2)
        menu_button.grid(row=0, column=0, sticky='nw', pady=0, padx=(0, 5))
        menu_button.bind("<Button-1>", self.toggle_sidebar)
        menu_button.bind("<Enter>", lambda e: e.widget.config(bg='#505050'))
        menu_button.bind("<Leave>", lambda e: e.widget.config(bg=self.dark_bg))

        # Create the tab controller (Notebook)
        self.notebook = ttk.Notebook(top_container, style='Dark.TNotebook')
        self.notebook.grid(row=0, column=1, sticky='nsew')
        
        # Frame for control buttons (Add/Close Tab)
        self.control_frame = tk.Frame(self.main_frame, bg=self.dark_bg)
        
        # Add Tab Button
        add_tab_btn = tk.Button(self.control_frame, text="+ Add Tab", command=self.add_tab, bg='#4CAF50', fg='white', relief='flat', font=('Arial', 10, 'bold'))
        add_tab_btn.pack(side='left', padx=5)

        # Close Tab Button
        close_tab_btn = tk.Button(self.control_frame, text="- Close Tab", command=self.close_tab, bg='#ff4444', fg='white', relief='flat', font=('Arial', 10, 'bold'))
        close_tab_btn.pack(side='left', padx=5)

        # Add the first tab
        self.add_tab()
        
        # Key bindings
        self.master.bind('<Control-t>', lambda event: self.add_tab())
        self.master.bind('<Control-w>', lambda event: self.close_tab())
        self.master.bind('<Control-Tab>', self.cycle_tabs)
        self.master.bind('<Control-r>', self.rename_current_tab)
        self.master.bind('<Control-q>', self.toggle_control_frame)
        self.master.bind('<Control-s>', self.toggle_title_bar)
        self.master.bind('<Control-h>', lambda event: self.show_history_window())
        self.master.bind("<Map>", self.on_map)

        # Bind events for resizing
        self.master.bind('<Motion>', self.on_mouse_motion)
        self.master.bind('<ButtonPress-1>', self.start_resize)
        self.master.bind('<B1-Motion>', self.do_resize)
        self.master.bind('<ButtonRelease-1>', lambda e: setattr(self, '_is_resizing', False))

    def add_to_history(self, expression, result):
        """Adds a calculation to the history list."""
        self.calculation_history.append(f"{expression} = {result}")
        if self.history_window and self.history_window.winfo_exists():
            self.history_listbox.insert(tk.END, f"{expression} = {result}")
            self.history_listbox.yview(tk.END)

    def clear_history(self):
        """Clears the calculation history."""
        self.calculation_history.clear()
        if self.history_window and self.history_window.winfo_exists():
            self.history_listbox.delete(0, tk.END)
        self.show_notification("History cleared")

    def show_history_window(self, event=None):
        """Creates and shows the history window."""
        if self.history_window and self.history_window.winfo_exists():
            self.history_window.lift()
            return

        self.history_window = tk.Toplevel(self.master)
        self.history_window.title("Calculation History")
        self.history_window.geometry("300x400")
        self.history_window.configure(bg=self.dark_bg)

        list_frame = tk.Frame(self.history_window, bg=self.dark_bg)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        self.history_listbox = tk.Listbox(list_frame, bg=self.entry_bg, fg=self.entry_fg,
                                          selectbackground=self.active_bg, relief='flat',
                                          font=('Arial', 11), yscrollcommand=scrollbar.set)
        for item in self.calculation_history:
            self.history_listbox.insert(tk.END, item)
        self.history_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        clear_btn = tk.Button(self.history_window, text="Clear History", command=self.clear_history,
                                bg=self.clear_button_bg, fg='white', relief='flat',
                                font=('Arial', 10, 'bold'))
        clear_btn.pack(fill='x', padx=10, pady=(0, 10))

    def create_title_bar_button(self, text, command, hover_color='#505050'):
        """Helper to create styled buttons for the title bar."""
        button = tk.Button(self.title_bar, text=text, bg='#1e1e1e', fg='white', relief='flat', command=command, font=('Arial', 12), activebackground=hover_color, activeforeground='white', borderwidth=0)
        button.bind("<Enter>", lambda e, c=hover_color: e.widget.config(bg=c))
        button.bind("<Leave>", lambda e: e.widget.config(bg='#1e1e1e'))
        return button

    def start_move(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def do_move(self, event):
        x = self.master.winfo_pointerx() - self._drag_start_x
        y = self.master.winfo_pointery() - self._drag_start_y
        self.master.geometry(f"+{x}+{y}")
        
    def on_mouse_motion(self, event):
        """Change cursor when hovering over edges."""
        x, y = event.x, event.y
        w, h = self.master.winfo_width(), self.master.winfo_height()
        grip = self._resize_grip_size

        if x > w - grip and y > h - grip:
            self.master.config(cursor="bottom_right_corner")
        elif x > w - grip:
            self.master.config(cursor="sb_h_double_arrow")
        elif y > h - grip:
            self.master.config(cursor="sb_v_double_arrow")
        else:
            self.master.config(cursor="")

    def start_resize(self, event):
        """Called when a resize drag starts."""
        cursor = self.master.cget("cursor")
        if cursor != "" and cursor != "arrow":
            self._is_resizing = True

    def do_resize(self, event):
        """Called when the mouse is dragged to resize."""
        if not self._is_resizing: return
        w, h = self.master.winfo_width(), self.master.winfo_height()
        dx = event.x_root - self.master.winfo_rootx() - w
        dy = event.y_root - self.master.winfo_rooty() - h
        cursor = self.master.cget("cursor")
        if cursor == "sb_h_double_arrow": self.master.geometry(f"{w+dx}x{h}")
        elif cursor == "sb_v_double_arrow": self.master.geometry(f"{w}x{h+dy}")
        elif cursor == "bottom_right_corner": self.master.geometry(f"{w+dx}x{h+dy}")

    def toggle_title_bar(self, event=None):
        if self.title_bar.winfo_ismapped():
            self.title_bar.pack_forget()
        else:
            self.title_bar.pack(side='top', fill='x', before=self.main_frame)

    def minimize_window(self, event=None):
        self.master.overrideredirect(False)
        self.master.iconify()

    def on_map(self, event=None):
        if self.master.state() == "normal":
            self.master.overrideredirect(True)

    def toggle_fullscreen(self, event=None):
        self._is_fullscreen = not self._is_fullscreen
        self.master.overrideredirect(False)
        self.master.attributes("-fullscreen", self._is_fullscreen)
        if not self._is_fullscreen:
            self.master.overrideredirect(True)

    def toggle_control_frame(self, event=None):
        if self.control_frame.winfo_ismapped():
            self.control_frame.pack_forget()
        else:
            self.control_frame.pack(side='bottom', pady=(5,0))

    def schedule_sidebar_close(self, event=None):
        """Schedules the sidebar to close after a delay."""
        if self.sidebar_window and self.sidebar_window.winfo_exists():
            self._sidebar_close_job = self.master.after(1500, self.toggle_sidebar)

    def cancel_sidebar_close(self, event=None):
        """Cancels the scheduled sidebar closing."""
        if self._sidebar_close_job:
            self.master.after_cancel(self._sidebar_close_job)
            self._sidebar_close_job = None

    def toggle_sidebar(self, event=None):
        """Toggles the visibility of the sidebar with an animation."""
        self.cancel_sidebar_close()

        if self._sidebar_job:
            self.master.after_cancel(self._sidebar_job)

        # If sidebar exists, we are closing it. Otherwise, we are opening it.
        if self.sidebar_window and self.sidebar_window.winfo_exists():
            self.animate_sidebar(direction='out')
        else:
            self.create_sidebar_window()
            self.animate_sidebar(direction='in')

    # MODIFICATION START: Create a separate method to build the sidebar window
    def create_sidebar_window(self):
        """Creates the transparent, borderless Toplevel window for the sidebar."""
        self.sidebar_window = tk.Toplevel(self.master)
        self.sidebar_window.overrideredirect(True)
        self.sidebar_window.attributes('-alpha', 0.9) # Set transparency here

        # Position and size it relative to the main window
        main_x = self.master.winfo_x()
        main_y = self.master.winfo_y()
        main_h = self.master.winfo_height()
        self.sidebar_window.geometry(f"200x{main_h}+{main_x-200}+{main_y}")

        # Add content to the sidebar
        sidebar_content = tk.Frame(self.sidebar_window, bg='#1e1e1e')
        sidebar_content.pack(fill='both', expand=True)

        history_btn = tk.Button(sidebar_content, text="History", command=self.show_history_window, bg='#3d3d3d', fg='white', relief='flat', font=('Arial', 10, 'bold'))
        history_btn.pack(fill='x', padx=10, pady=10)

        # Bind events for auto-closing
        self.sidebar_window.bind("<Enter>", self.cancel_sidebar_close)
        self.sidebar_window.bind("<Leave>", self.schedule_sidebar_close)
    # MODIFICATION END

    def animate_sidebar(self, direction='in'):
        """Animates the sidebar sliding in or out."""
        if not self.sidebar_window: return

        main_x = self.master.winfo_x()
        main_y = self.master.winfo_y()
        main_h = self.master.winfo_height()
        
        start_x = main_x - 200 if direction == 'in' else main_x
        end_x = main_x if direction == 'in' else main_x - 200
        
        animation_duration = 200
        animation_steps = 20
        sleep_interval = animation_duration // animation_steps

        def animate(step=0):
            try:
                if step <= animation_steps:
                    fraction = 1 - (1 - (step / 20)) ** 3 # Ease-out
                    current_x = int(start_x + (end_x - start_x) * fraction)
                    
                    self.sidebar_window.geometry(f"200x{main_h}+{current_x}+{main_y}")
                    self._sidebar_job = self.master.after(sleep_interval, animate, step + 1)
                elif direction == 'out':
                    self.sidebar_window.destroy()
                    self.sidebar_window = None
            except tk.TclError:
                pass

        animate()

    def configure_styles(self):
        """Configures the ttk styles for the dark theme."""
        style = ttk.Style()
        style.theme_use('clam') 
        
        style.configure('Dark.TFrame', background=self.dark_bg)

        style.configure('Dark.TNotebook', background=self.dark_bg, borderwidth=0, tabposition='ne')
        style.configure('Dark.TNotebook.Tab', background='#3d3d3d', foreground='white', borderwidth=0, padding=[10, 5])
        style.map('Dark.TNotebook.Tab',
            background=[('selected', '#505050'), ('active', '#454545')],
            foreground=[('selected', 'white')]
        )

    def add_tab(self):
        """Creates a new calculator tab and adds it to the notebook."""
        tab_count = len(self.notebook.tabs()) + 1
        new_tab = CalculatorTab(self.notebook, self)
        self.notebook.add(new_tab, text=f'Calc {tab_count}')
        self.notebook.select(new_tab) 

    def close_tab(self):
        """Closes the currently selected tab."""
        if not self.notebook.tabs(): return
        selected_tab_index = self.notebook.index('current')
        self.notebook.forget(selected_tab_index)

    def cycle_tabs(self, event=None):
        """Cycles to the next tab in the notebook."""
        if len(self.notebook.tabs()) < 2: return
        current_index = self.notebook.index('current')
        next_index = (current_index + 1) % len(self.notebook.tabs())
        self.notebook.select(next_index)

    def rename_current_tab(self, event=None):
        """Opens a dialog to rename the currently selected tab."""
        if not self.notebook.tabs(): return
        current_tab_id = self.notebook.select()
        current_name = self.notebook.tab(current_tab_id, "text")
        dialog = CustomRenameDialog(self.master, "Rename Tab", initialvalue=current_name)
        new_name = dialog.result
        if new_name and new_name.strip():
            self.notebook.tab(current_tab_id, text=new_name.strip())

    def show_notification(self, message, duration=1200):
        """Shows a temporary, animated notification at the bottom of the window."""
        if self._toast_job: self.master.after_cancel(self._toast_job)
        if self._toast_label: self._toast_label.destroy()

        self._toast_label = tk.Label(self.master, text=message, bg='#303030', fg='white', font=('Arial', 10), padx=15, pady=8, highlightbackground='#606060', highlightthickness=1)
        
        end_rely, start_rely = 0.95, 1.1
        animation_duration, animation_steps = 250, 25
        sleep_interval = animation_duration // animation_steps
        
        def animate(step=0, direction='in'):
            try:
                if direction == 'in':
                    if step <= animation_steps:
                        fraction = 1 - (1 - (step / animation_steps)) ** 3
                        current_rely = start_rely - (start_rely - end_rely) * fraction
                        self._toast_label.place(relx=0.5, rely=current_rely, anchor='center')
                        self._toast_job = self.master.after(sleep_interval, animate, step + 1, 'in')
                    else:
                        self._toast_job = self.master.after(duration, animate, 0, 'out')
                elif direction == 'out':
                    if step <= animation_steps:
                        fraction = (step / animation_steps) ** 3
                        current_rely = end_rely + (start_rely - end_rely) * fraction
                        self._toast_label.place(relx=0.5, rely=current_rely, anchor='center')
                        self._toast_job = self.master.after(sleep_interval, animate, step + 1, 'out')
                    else:
                        self._toast_label.destroy()
                        self._toast_label = None
            except tk.TclError: pass
        animate()

if __name__ == "__main__":
    root = tk.Tk()
    app = TabbedCalculatorApp(root)
    root.mainloop()
