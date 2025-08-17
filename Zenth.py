import tkinter as tk
from tkinter import ttk, simpledialog
import math
import decimal
import re
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class CustomToplevel(tk.Toplevel):
    """A custom Toplevel window with a draggable title bar."""
    def __init__(self, parent, title, **kwargs):
        super().__init__(parent, **kwargs)
        
        # These lines ensure the pop-up stays on top of and moves with the parent window.
        self.transient(parent)
        self.grab_set()
        
        self.overrideredirect(True)
        self.parent = parent
        self.title_text = title
        
        # Style
        self.bg = '#2d2d2d'
        self.title_bar_bg = '#1e1e1e'
        self.fg = 'white'
        self.configure(bg=self.bg)

        # Title Bar
        self.title_bar = tk.Frame(self, bg=self.title_bar_bg, height=30)
        self.title_bar.pack(fill='x', side='top')
        
        close_button = self.create_title_bar_button('✕', self.on_close, hover_color='#ff4444')
        close_button.pack(side='right', padx=5, pady=2)
        
        title_label = tk.Label(self.title_bar, text=self.title_text, bg=self.title_bar_bg, fg=self.fg)
        title_label.pack(side='left', padx=10)

        # Main content frame
        self.main_content_frame = tk.Frame(self, bg=self.bg)
        self.main_content_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Dragging logic
        self._drag_start_x = 0
        self._drag_start_y = 0
        self.title_bar.bind("<ButtonPress-1>", self._start_move)
        self.title_bar.bind("<B1-Motion>", self._do_move)
        title_label.bind("<ButtonPress-1>", self._start_move)
        title_label.bind("<B1-Motion>", self._do_move)

    def on_close(self):
        self.grab_release()
        self.destroy()

    def create_title_bar_button(self, text, command, hover_color='#505050'):
        button = tk.Button(self.title_bar, text=text, bg=self.title_bar_bg, fg=self.fg, relief='flat', command=command, font=('Arial', 12), activebackground=hover_color, activeforeground='white', borderwidth=0)
        button.bind("<Enter>", lambda e, c=hover_color: e.widget.config(bg=c))
        button.bind("<Leave>", lambda e: e.widget.config(bg=self.title_bar_bg))
        return button

    def _start_move(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _do_move(self, event):
        x = self.winfo_pointerx() - self._drag_start_x
        y = self.winfo_pointery() - self._drag_start_y
        self.geometry(f"+{x}+{y}")

class CustomRenameDialog(tk.Toplevel):
    """A custom dark-mode dialog for renaming tabs."""
    def __init__(self, parent, title, initialvalue=""):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result = None
        self.configure(bg='#2d2d2d')
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
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.grab_set()
        self.wait_window(self)

    def on_ok(self):
        self.result = self.entry.get()
        self.destroy()

    def on_cancel(self):
        self.destroy()

class RoundedButton(tk.Canvas):
    """A custom button with rounded corners."""
    def __init__(self, parent, text, command, **kwargs):
        self.radius = kwargs.pop('radius', 12)
        self.bg = kwargs.pop('bg', '#3d3d3d')
        self.fg = kwargs.pop('fg', 'white')
        self.hover_bg = kwargs.pop('hover_bg', '#505050')
        height = kwargs.pop('height', 30)
        super().__init__(parent, borderwidth=0, relief="flat", highlightthickness=0, bg=parent.cget('bg'), height=height)
        self.command = command
        self.text = text
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", self._on_resize)
        self._text_id = None

    def _on_resize(self, event):
        self.draw()

    def draw(self, is_hover=False):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 2 * self.radius or height < 2 * self.radius: return
        bg_color = self.hover_bg if is_hover else self.bg
        self.create_oval((0, 0, self.radius*2, self.radius*2), fill=bg_color, outline=bg_color)
        self.create_oval((width-self.radius*2, 0, width, self.radius*2), fill=bg_color, outline=bg_color)
        self.create_oval((0, height-self.radius*2, self.radius*2, height), fill=bg_color, outline=bg_color)
        self.create_oval((width-self.radius*2, height-self.radius*2, width, height), fill=bg_color, outline=bg_color)
        self.create_rectangle((self.radius, 0, width-self.radius, height), fill=bg_color, outline=bg_color)
        self.create_rectangle((0, self.radius, width, height-self.radius), fill=bg_color, outline=bg_color)
        self._text_id = self.create_text(width/2, height/2, text=self.text, fill=self.fg, font=('Arial', 10, 'bold'))

    def _on_enter(self, event): self.draw(is_hover=True)
    def _on_leave(self, event): self.draw(is_hover=False)
    def _on_press(self, event): pass
    def _on_release(self, event):
        self.draw(is_hover=True)
        if self.command: self.command()

class CalculatorTab(ttk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.configure(style='Dark.TFrame')
        self.result_var = tk.StringVar()
        self.previous_result_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        self.display_frame = tk.Frame(self, bg=self.app.dark_bg)
        self.display_frame.grid(row=0, column=0, columnspan=6, padx=10, pady=(10, 5), sticky='nsew')

        self.previous_result_label = tk.Label(self.display_frame, textvariable=self.previous_result_var, font=('Arial', 12), bg=self.app.dark_bg, fg='#888888', anchor='e')
        self.previous_result_label.pack(fill='x', padx=5)
        
        entry_frame = tk.Frame(self.display_frame, bg=self.app.dark_bg)
        entry_frame.pack(fill='both', expand=True)

        self.entry = tk.Entry(entry_frame, textvariable=self.result_var, font=('Arial', 20, 'bold'), bd=0, insertwidth=2, width=14, borderwidth=0, bg=self.app.entry_bg, fg=self.app.entry_fg, justify='right', relief='flat')
        self.entry.pack(side='left', fill='both', expand=True)
        self.entry.bind("<Return>", lambda event: self.calculate_result())
        self.entry.bind("<Button-3>", lambda event: self.paste_from_clipboard())
        
        self.copy_btn = tk.Button(entry_frame, text='Copy', padx=12, pady=5, font=('Arial', 10, 'bold'), bg=self.app.copy_button_bg, fg=self.app.button_fg, activebackground=self.app.active_bg, activeforeground=self.app.button_fg, relief='flat', borderwidth=0, command=self.copy_to_clipboard)
        self.copy_btn.pack(side='right', fill='y', padx=(5,0))
        
        self.buttons_map = {}
        buttons_layout = [('C', 1, 0), ('(', 1, 1), (')', 1, 2), ('/', 1, 3), ('DEL', 1, 4), ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('*', 2, 3), ('^', 2, 4), ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3), ('sqrt', 3, 4), ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3), ('%', 4, 4), ('0', 5, 0), ('.', 5, 1), ('±', 5, 2), ('=', 5, 3), ('π', 5, 4), ('sin', 6, 0), ('cos', 6, 1), ('tan', 6, 2), ('log', 6, 3), ('ln', 6, 4), ('x!', 1, 5)]
        for text, row, col in buttons_layout:
            button = tk.Button(self, text=text, padx=10, pady=10, font=('Arial', 12, 'bold'), relief='flat', borderwidth=0, command=lambda t=text: self.on_button_click(t))
            button.grid(row=row, column=col, padx=3, pady=3, sticky=tk.NSEW)
            self.buttons_map[text] = button
        for i in range(7): self.grid_rowconfigure(i, weight=1)
        for i in range(6): self.grid_columnconfigure(i, weight=1)
        self.update_colors()

    def update_colors(self):
        self.display_frame.config(bg=self.app.dark_bg)
        self.previous_result_label.config(bg=self.app.dark_bg, fg='#888888')
        self.entry.config(bg=self.app.entry_bg, fg=self.app.entry_fg)
        self.copy_btn.config(bg=self.app.copy_button_bg, fg=self.app.button_fg, activebackground=self.app.active_bg, activeforeground=self.app.button_fg)
        for text, button in self.buttons_map.items():
            if text == '=': bg = self.app.equals_button_bg
            elif text == 'C': bg = self.app.clear_button_bg
            elif text in ['sin', 'cos', 'tan', 'log', 'ln', 'sqrt', 'π', 'DEL', '^', '%', 'x!']: bg = self.app.special_button_bg
            else: bg = self.app.button_bg
            button.config(bg=bg, fg=self.app.button_fg, activebackground=self.app.active_bg, activeforeground=self.app.button_fg)
            button.bind("<Enter>", lambda e, b=button, c=self.app.active_bg: b.config(bg=c))
            button.bind("<Leave>", lambda e, b=button, c=bg: b.config(bg=c))

    def show_notification(self, message, duration=1500): self.app.show_notification(message, duration)
    def copy_to_clipboard(self):
        result = self.result_var.get()
        if result: self.master.clipboard_clear(); self.master.clipboard_append(result); self.show_notification("Copied to clipboard")
        else: self.show_notification("Nothing to copy", 2000)
    def paste_from_clipboard(self):
        try:
            clipboard_content = self.master.clipboard_get()
            if clipboard_content: self.result_var.set(self.result_var.get() + clipboard_content); self.show_notification("Pasted from clipboard")
            else: self.show_notification("Clipboard is empty", 2000)
        except tk.TclError: self.show_notification("No content in clipboard", 2000)
        return "break"
    def on_button_click(self, char):
        current_text = self.result_var.get()
        if char == 'C': 
            self.result_var.set('')
            self.previous_result_var.set('')
        elif char == 'DEL': self.result_var.set(current_text[:-1])
        elif char == '±':
            if current_text and current_text.startswith('-'): self.result_var.set(current_text[1:])
            else: self.result_var.set('-' + current_text)
        elif char == 'π': self.result_var.set(current_text + str(self.app.pi_decimal))
        elif char == '=': self.calculate_result()
        elif char == 'sqrt':
            try:
                self.result_var.set(str(decimal.Decimal(current_text).sqrt()))
            except (ValueError, TypeError, decimal.InvalidOperation): self.result_var.set('Error')
        elif char == 'x!':
            try:
                num = int(current_text)
                if num < 0:
                    self.result_var.set("Error")
                else:
                    # Pure Python factorial implementation to handle large numbers
                    res = 1
                    for i in range(2, num + 1):
                        res *= i
                    self.result_var.set(f"{res:,}")
            except (ValueError, TypeError, OverflowError):
                self.result_var.set("Error")
        elif char in ['sin', 'cos', 'tan', 'log', 'ln']:
            try:
                if char in ['log', 'ln']:
                    value = decimal.Decimal(current_text)
                    if char == 'log': result = value.log10()
                    elif char == 'ln': result = value.ln()
                else:
                    value = float(current_text)
                    if char == 'sin': result = math.sin(math.radians(value))
                    elif char == 'cos': result = math.cos(math.radians(value))
                    elif char == 'tan': result = math.tan(math.radians(value))
                self.result_var.set(str(result))
            except (ValueError, TypeError, decimal.InvalidOperation):
                self.result_var.set('Error')
        else:
            self.result_var.set(current_text + char)

    def calculate_result(self):
        try:
            expression = self.result_var.get().replace(',', '')
            
            clean_expression = expression.replace('^', '**').replace('%', '/100')
            clean_expression = clean_expression.replace('π', str(self.app.pi_decimal))

            transformed_expression = re.sub(r'(\d+(\.\d*)?|\.\d+)', r"decimal.Decimal('\1')", clean_expression)

            result = eval(transformed_expression, {"__builtins__": None}, {"decimal": decimal})

            final_result = result.normalize()
            
            if final_result == final_result.to_integral_value():
                formatted_result = f"{int(final_result):,}"
            else:
                formatted_result = str(final_result)

            self.app.add_to_history(expression, formatted_result)
            self.previous_result_var.set(f"{expression} =")
            self.result_var.set(formatted_result)
        except Exception:
            self.result_var.set('Error')

# --- Global list and function for managing multiple windows ---
running_apps = []

def open_new_instance(event=None):
    """Creates a new calculator window as a Toplevel instance."""
    root = running_apps[0].root
    new_window = tk.Toplevel(root)
    app = TabbedCalculatorApp(new_window, root)
    running_apps.append(app)

class UnitConverterWindow(CustomToplevel):
    def __init__(self, parent, app_theme):
        super().__init__(parent, "Unit Converter")
        self.geometry("400x300")
        self.app_theme = app_theme
        
        # This is the key to styling the dropdown list
        self.option_add('*TCombobox*Listbox.background', self.app_theme['entry_bg'])
        self.option_add('*TCombobox*Listbox.foreground', self.app_theme['entry_fg'])
        self.option_add('*TCombobox*Listbox.selectBackground', self.app_theme['active_bg'])
        self.option_add('*TCombobox*Listbox.selectForeground', self.app_theme['entry_fg'])

        self.conversions = {
            "Length": {
                "Meters": 1, "Kilometers": 1000, "Centimeters": 0.01,
                "Miles": 1609.34, "Feet": 0.3048, "Inches": 0.0254
            },
            "Mass": {
                "Grams": 1, "Kilograms": 1000, "Milligrams": 0.001,
                "Pounds": 453.592, "Ounces": 28.3495
            },
            "Temperature": {
                "Celsius": 0, "Fahrenheit": 0, "Kelvin": 0
            }
        }
        
        self.create_widgets()
        self.update_unit_dropdowns()

    def create_widgets(self):
        content = self.main_content_frame
        
        # Style for Combobox
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TCombobox', 
                        fieldbackground=self.app_theme['entry_bg'], 
                        background=self.app_theme['button_bg'], 
                        foreground=self.app_theme['entry_fg'],
                        arrowcolor=self.app_theme['entry_fg'],
                        bordercolor=self.app_theme['bg'],
                        lightcolor=self.app_theme['bg'],
                        darkcolor=self.app_theme['bg'])
        style.map('TCombobox',
                  fieldbackground=[('readonly', self.app_theme['entry_bg'])],
                  selectbackground=[('readonly', self.app_theme['entry_bg'])],
                  selectforeground=[('readonly', self.app_theme['entry_fg'])],
                  foreground=[('readonly', self.app_theme['entry_fg'])])


        # Conversion Type
        tk.Label(content, text="Conversion Type:", bg=self.bg, fg=self.fg).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.type_var = tk.StringVar(value=list(self.conversions.keys())[0])
        self.type_combo = ttk.Combobox(content, textvariable=self.type_var, values=list(self.conversions.keys()), state='readonly')
        self.type_combo.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky='ew')
        self.type_combo.bind("<<ComboboxSelected>>", self.update_unit_dropdowns)

        # Input Value
        tk.Label(content, text="Value:", bg=self.bg, fg=self.fg).grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(content, textvariable=self.input_var, bg=self.app_theme['entry_bg'], fg=self.app_theme['entry_fg'], relief='flat')
        self.input_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky='ew')

        # From Unit
        tk.Label(content, text="From:", bg=self.bg, fg=self.fg).grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.from_unit_var = tk.StringVar()
        self.from_unit_combo = ttk.Combobox(content, textvariable=self.from_unit_var, state='readonly')
        self.from_unit_combo.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky='ew')

        # To Unit
        tk.Label(content, text="To:", bg=self.bg, fg=self.fg).grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.to_unit_var = tk.StringVar()
        self.to_unit_combo = ttk.Combobox(content, textvariable=self.to_unit_var, state='readonly')
        self.to_unit_combo.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky='ew')

        # Convert Button
        convert_btn = RoundedButton(content, text="Convert", command=self.perform_conversion, bg=self.app_theme['equals_button_bg'], hover_bg='#57D85B', height=35)
        convert_btn.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

        # Result
        self.result_label = tk.Label(content, text="Result: -", font=('Arial', 12, 'bold'), bg=self.bg, fg=self.fg)
        self.result_label.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    def update_unit_dropdowns(self, event=None):
        conv_type = self.type_var.get()
        units = list(self.conversions[conv_type].keys())
        self.from_unit_combo['values'] = units
        self.to_unit_combo['values'] = units
        self.from_unit_var.set(units[0])
        self.to_unit_var.set(units[1] if len(units) > 1 else units[0])

    def perform_conversion(self):
        try:
            value = float(self.input_var.get())
            conv_type = self.type_var.get()
            from_unit = self.from_unit_var.get()
            to_unit = self.to_unit_var.get()
            
            if conv_type == "Temperature":
                # Handle temperature separately
                if from_unit == "Celsius":
                    if to_unit == "Fahrenheit": result = (value * 9/5) + 32
                    elif to_unit == "Kelvin": result = value + 273.15
                    else: result = value
                elif from_unit == "Fahrenheit":
                    if to_unit == "Celsius": result = (value - 32) * 5/9
                    elif to_unit == "Kelvin": result = (value - 32) * 5/9 + 273.15
                    else: result = value
                elif from_unit == "Kelvin":
                    if to_unit == "Celsius": result = value - 273.15
                    elif to_unit == "Fahrenheit": result = (value - 273.15) * 9/5 + 32
                    else: result = value
            else:
                # Standard conversion using base unit
                base_value = value * self.conversions[conv_type][from_unit]
                result = base_value / self.conversions[conv_type][to_unit]
            
            self.result_label.config(text=f"Result: {result:.4f}")
        except (ValueError, ZeroDivisionError):
            self.result_label.config(text="Result: Invalid Input")

class TabbedCalculatorApp:
    def __init__(self, master, root):
        self.master = master # This is now the Toplevel window
        self.root = root # This is the hidden main Tk() window
        
        self.master.overrideredirect(True)
        
        # We don't set the title on the hidden root, but on the visible window's label
        try:
            icon_path = resource_path("icon.ico")
            # Set the icon on the hidden root, which controls the taskbar icon
            self.root.iconbitmap(icon_path) 
        except tk.TclError:
            print("icon.ico not found, skipping icon.")

        decimal.getcontext().prec = 100
        self.pi_decimal = decimal.Decimal(math.pi)
        
        master.geometry("480x600+200+200")
        self.set_dark_theme()
        self._drag_start_x, self._drag_start_y = 0, 0
        self._is_fullscreen, self._is_resizing = False, False
        self._resize_grip_size = 8
        self._sidebar_job, self._toast_job = None, None
        self._toast_label = None
        self.calculation_history, self.history_window = [], None
        self._sidebar_close_job = None
        self.sidebar_visible = False
        self.settings_window = None
        self.keybind_window = None
        self.unit_converter_window = None
        self.closed_tabs = []
        
        # --- State variables for tab cycling ---
        self.tab_preview_window = None
        self.preview_index = 0
        self.is_ctrl_pressed = False
        
        self.keybinds = {
            "Add Tab": ("<Control-t>", self.add_tab), 
            "Close Tab": ("<Control-w>", self.close_tab),
            "New Window": ("<Control-n>", open_new_instance),
            "Reopen Tab": ("<Control-Shift-T>", self.reopen_closed_tab),
            "Rename Tab": ("<Control-r>", self.rename_current_tab),
            "Toggle Controls": ("<Control-q>", self.toggle_control_frame), 
            "Toggle Title Bar": ("<Control-s>", self.toggle_title_bar),
            "Show History": ("<Control-h>", self.show_history_window), 
            "Show Settings": ("<F2>", self.show_settings_window),
            "Show Help": ("<F1>", self.show_help_window),
        }
        self.container = tk.Frame(master, bg=self.dark_bg)
        self.container.pack(fill='both', expand=True)
        self.title_bar = tk.Frame(self.container, bg='#1e1e1e', height=30)
        
        # The close button now destroys the hidden root to exit the app
        close_button = self.create_title_bar_button('✕', self.close_window, hover_color='#ff4444')
        close_button.pack(side='right', padx=5, pady=2)

        self.fullscreen_canvas = tk.Canvas(self.title_bar, width=20, height=20, bg='#1e1e1e', bd=0, highlightthickness=0)
        self.fullscreen_canvas.create_rectangle(5, 5, 15, 15, outline='white', width=1)
        self.fullscreen_canvas.pack(side='right', padx=5, pady=5)
        self.fullscreen_canvas.bind("<Button-1>", self.toggle_fullscreen)
        
        # The minimize button now controls the hidden root window
        self.minimize_canvas = tk.Canvas(self.title_bar, width=20, height=20, bg='#1e1e1e', bd=0, highlightthickness=0)
        self.minimize_canvas.create_line(5, 10, 15, 10, fill='white', width=1)
        self.minimize_canvas.pack(side='right', padx=5, pady=5)
        self.minimize_canvas.bind("<Button-1>", self.minimize_window)
        
        self.title_label = tk.Label(self.title_bar, text="Zenth", bg='#1e1e1e', fg='white')
        self.title_label.pack(side='left', padx=10)
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)
        self.fullscreen_canvas.bind("<Enter>", lambda e: e.widget.config(bg='#505050'))
        self.fullscreen_canvas.bind("<Leave>", lambda e: e.widget.config(bg='#1e1e1e'))
        self.minimize_canvas.bind("<Enter>", lambda e: e.widget.config(bg='#505050'))
        self.minimize_canvas.bind("<Leave>", lambda e: e.widget.config(bg='#1e1e1e'))
        self.main_frame = tk.Frame(self.container, bg=self.dark_bg)
        self.main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.configure_styles()
        top_container = tk.Frame(self.main_frame, bg=self.dark_bg)
        top_container.pack(fill='both', expand=True)
        top_container.grid_rowconfigure(0, weight=1)
        top_container.grid_columnconfigure(1, weight=1)
        self.menu_button = tk.Canvas(top_container, width=30, height=30, bg=self.dark_bg, bd=0, highlightthickness=0, cursor="hand2")
        self.menu_button.create_line(8, 10, 22, 10, fill='white', width=2)
        self.menu_button.create_line(8, 15, 22, 15, fill='white', width=2)
        self.menu_button.create_line(8, 20, 22, 20, fill='white', width=2)
        self.menu_button.grid(row=0, column=0, sticky='nw', pady=0, padx=(0, 5))
        self.menu_button.bind("<Button-1>", self.toggle_sidebar)
        self.menu_button.bind("<Enter>", lambda e: e.widget.config(bg=self.active_bg))
        self.menu_button.bind("<Leave>", lambda e: e.widget.config(bg=self.dark_bg))
        
        self.notebook = ttk.Notebook(top_container, style='Dark.TNotebook')
        self.notebook.grid(row=0, column=1, sticky='nsew')
        
        self.control_frame = tk.Frame(self.main_frame, bg=self.dark_bg)
        self.add_tab_btn = tk.Button(self.control_frame, text="+ Add Tab", command=self.add_tab, bg='#4CAF50', fg='white', relief='flat', font=('Arial', 10, 'bold'))
        self.add_tab_btn.pack(side='left', padx=5)
        self.close_tab_btn = tk.Button(self.control_frame, text="- Close Tab", command=self.close_tab, bg='#ff4444', fg='white', relief='flat', font=('Arial', 10, 'bold'))
        self.close_tab_btn.pack(side='left', padx=5)
        
        self.sidebar = tk.Frame(self.master, bg='#1e1e1e')
        
        top_frame = tk.Frame(self.sidebar, bg='#1e1e1e')
        top_frame.pack(fill='both', expand=True)
        
        bottom_frame = tk.Frame(self.sidebar, bg='#1e1e1e')
        bottom_frame.pack(fill='x', side='bottom')

        self.converter_btn = RoundedButton(bottom_frame, text="Unit Converter", command=self.show_unit_converter_window, bg='#3d3d3d', hover_bg='#505050', height=30)
        self.converter_btn.pack(fill='x', padx=10, pady=5)
        self.history_btn = RoundedButton(bottom_frame, text="History", command=self.show_history_window, bg='#3d3d3d', hover_bg='#505050', height=30)
        self.history_btn.pack(fill='x', padx=10, pady=5)
        self.settings_btn = RoundedButton(bottom_frame, text="Settings", command=self.show_settings_window, bg='#3d3d3d', hover_bg='#505050', height=30)
        self.settings_btn.pack(fill='x', padx=10, pady=5)
        self.help_btn = RoundedButton(bottom_frame, text="Help", command=self.show_help_window, bg='#3d3d3d', hover_bg='#505050', height=30)
        self.help_btn.pack(fill='x', padx=10, pady=(5, 10))
        
        self.sidebar.bind("<Enter>", self.cancel_sidebar_close)
        self.sidebar.bind("<Leave>", self.schedule_sidebar_close)

        self.add_tab()
        self.apply_keybinds()
        
        self.master.bind('<Motion>', self.on_mouse_motion)
        self.master.bind('<ButtonPress-1>', self.start_resize)
        self.master.bind('<B1-Motion>', self.do_resize)
        self.master.bind('<ButtonRelease-1>', lambda e: setattr(self, '_is_resizing', False))
        
        # --- Bind events directly to this specific window ---
        self.master.bind("<KeyPress-Control_L>", self.on_ctrl_press)
        self.master.bind("<KeyRelease-Control_L>", self.on_ctrl_release)
        self.master.bind("<Control-Tab>", self.cycle_tabs)

    def close_window(self):
        """This function now destroys the hidden root, which closes the entire application."""
        self.root.destroy()

    def minimize_window(self, event=None):
        """This function now hides the main window and iconifies the hidden root."""
        self.master.withdraw()
        self.root.iconify()

    def set_dark_theme(self):
        self.dark_bg, self.button_bg, self.button_fg, self.active_bg, self.entry_bg, self.entry_fg, self.special_button_bg, self.equals_button_bg, self.clear_button_bg, self.copy_button_bg = '#2d2d2d', '#3d3d3d', '#ffffff', '#505050', '#1a1a1a', '#ffffff', '#404040', '#4CAF50', '#ff4444', '#5d5d5d'
        self.update_all_colors()

    def set_light_theme(self):
        self.dark_bg, self.button_bg, self.button_fg, self.active_bg, self.entry_bg, self.entry_fg, self.special_button_bg, self.equals_button_bg, self.clear_button_bg, self.copy_button_bg = '#f0f0f0', '#ffffff', '#000000', '#e0e0e0', '#ffffff', '#000000', '#d0d0d0', '#4CAF50', '#ff4444', '#c0c0c0'
        self.update_all_colors()

    def update_all_colors(self):
        if not hasattr(self, 'container'): return
        self.master.config(bg=self.dark_bg)
        self.container.config(bg=self.dark_bg)
        self.main_frame.config(bg=self.dark_bg)
        self.control_frame.config(bg=self.dark_bg)
        self.menu_button.config(bg=self.dark_bg)
        self.configure_styles()
        for tab_id in self.notebook.tabs():
            try:
                tab_widget = self.master.nametowidget(tab_id)
                if isinstance(tab_widget, CalculatorTab): tab_widget.update_colors()
            except tk.TclError:
                continue

    def add_to_history(self, expression, result):
        self.calculation_history.append(f"{expression} = {result}")
        if self.history_window and self.history_window.winfo_exists(): self.history_listbox.insert(tk.END, f"{expression} = {result}"); self.history_listbox.yview(tk.END)
    def clear_history(self):
        self.calculation_history.clear()
        if self.history_window and self.history_window.winfo_exists(): self.history_listbox.delete(0, tk.END)
        self.show_notification("History cleared")
    def show_history_window(self, event=None):
        if self.history_window and self.history_window.winfo_exists(): self.history_window.lift(); return
        self.history_window = CustomToplevel(self.master, "Calculation History"); self.history_window.geometry("300x400")
        list_frame = tk.Frame(self.history_window.main_content_frame, bg=self.dark_bg); list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar = tk.Scrollbar(list_frame, relief='flat', troughcolor=self.dark_bg, bg=self.button_bg, activebackground=self.active_bg); scrollbar.pack(side='right', fill='y')
        self.history_listbox = tk.Listbox(list_frame, bg=self.entry_bg, fg=self.entry_fg, selectbackground=self.active_bg, relief='flat', font=('Arial', 11), yscrollcommand=scrollbar.set, highlightthickness=0)
        for item in self.calculation_history: self.history_listbox.insert(tk.END, item)
        self.history_listbox.pack(side='left', fill='both', expand=True); scrollbar.config(command=self.history_listbox.yview)
        clear_btn = RoundedButton(self.history_window.main_content_frame, text="Clear History", command=self.clear_history, bg=self.clear_button_bg, hover_bg='#ff6666', height=30); clear_btn.pack(fill='x', padx=5, pady=(0, 5))

    def show_settings_window(self, event=None):
        if self.settings_window and self.settings_window.winfo_exists(): self.settings_window.lift(); return
        self.settings_window = CustomToplevel(self.master, "Settings"); self.settings_window.geometry("350x550")
        
        content = self.settings_window.main_content_frame
        theme_label = tk.Label(content, text="Theme", bg=self.dark_bg, fg=self.button_fg, font=('Arial', 12, 'bold')); theme_label.pack(pady=(10,5))
        dark_btn = tk.Button(content, text="Dark Mode", command=self.set_dark_theme, bg=self.button_bg, fg=self.button_fg, relief='flat', font=('Arial', 10)); dark_btn.pack(fill='x', padx=20, pady=5)
        light_btn = tk.Button(content, text="Light Mode", command=self.set_light_theme, bg=self.button_bg, fg=self.button_fg, relief='flat', font=('Arial', 10)); light_btn.pack(fill='x', padx=20, pady=5)
        
        ttk.Separator(content, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        keybind_label = tk.Label(content, text="Keybinds", bg=self.dark_bg, fg=self.button_fg, font=('Arial', 12, 'bold')); keybind_label.pack(pady=(10,5))
        entries = {}
        for action, (key, _) in self.keybinds.items():
            frame = tk.Frame(content, bg=self.dark_bg); frame.pack(fill='x', padx=20, pady=2)
            label = tk.Label(frame, text=f"{action}:", bg=self.dark_bg, fg=self.button_fg, width=15, anchor='w'); label.pack(side='left')
            entry = tk.Entry(frame, bg=self.entry_bg, fg=self.entry_fg, relief='flat', width=20); entry.insert(0, key); entry.pack(side='left', fill='x', expand=True)
            entries[action] = entry
        
        def save_settings():
            self.unbind_all_keybinds()
            for action, entry in entries.items():
                new_key, command = entry.get(), self.keybinds[action][1]
                self.keybinds[action] = (new_key, command)
            self.apply_keybinds(); self.settings_window.destroy(); self.show_notification("Settings updated!")
        
        save_btn = tk.Button(content, text="Save Settings", command=save_settings, bg=self.equals_button_bg, fg='white', relief='flat'); save_btn.pack(pady=15)

    def show_help_window(self, event=None):
        help_win = CustomToplevel(self.master, "Keybinds Help")
        for action, (key, _) in self.keybinds.items():
            frame = tk.Frame(help_win.main_content_frame, bg=self.dark_bg)
            frame.pack(fill='x', padx=10, pady=5)
            action_label = tk.Label(frame, text=f"{action}:", bg=self.dark_bg, fg=self.button_fg, width=15, anchor='w')
            action_label.pack(side='left')
            key_label = tk.Label(frame, text=key, bg=self.entry_bg, fg=self.entry_fg, relief='flat', width=20)
            key_label.pack(side='left', fill='x', expand=True)
    
    def show_unit_converter_window(self, event=None):
        if self.unit_converter_window and self.unit_converter_window.winfo_exists():
            self.unit_converter_window.lift()
            return
        theme = {
            'bg': self.dark_bg, 'fg': self.button_fg, 'entry_bg': self.entry_bg,
            'entry_fg': self.entry_fg, 'button_bg': self.button_bg,
            'equals_button_bg': self.equals_button_bg, 'active_bg': self.active_bg
        }
        self.unit_converter_window = UnitConverterWindow(self.master, theme)

    def apply_keybinds(self):
        root = self.master.winfo_toplevel()
        for key, command in self.keybinds.values():
            if key == "<Control-n>": 
                self.root.bind_all(key, command)
            else: 
                self.master.bind(key, command)

    def unbind_all_keybinds(self):
        root = self.master.winfo_toplevel()
        for key, _ in self.keybinds.values():
            if key == "<Control-n>":
                self.root.unbind_all(key)
            else:
                self.master.unbind(key)

    def create_title_bar_button(self, text, command, hover_color='#505050'):
        button = tk.Button(self.title_bar, text=text, bg='#1e1e1e', fg='white', relief='flat', command=command, font=('Arial', 12), activebackground=hover_color, activeforeground='white', borderwidth=0)
        button.bind("<Enter>", lambda e, c=hover_color: e.widget.config(bg=c)); button.bind("<Leave>", lambda e: e.widget.config(bg='#1e1e1e')); return button
    def start_move(self, event): self._drag_start_x, self._drag_start_y = event.x, event.y
    def do_move(self, event): x, y = self.master.winfo_pointerx() - self._drag_start_x, self.master.winfo_pointery() - self._drag_start_y; self.master.geometry(f"+{x}+{y}")
    def on_mouse_motion(self, event):
        x, y, w, h, grip = event.x, event.y, self.master.winfo_width(), self.master.winfo_height(), self._resize_grip_size
        if x > w - grip and y > h - grip: self.master.config(cursor="bottom_right_corner")
        elif x > w - grip: self.master.config(cursor="sb_h_double_arrow")
        elif y > h - grip: self.master.config(cursor="sb_v_double_arrow")
        else: self.master.config(cursor="")
    def start_resize(self, event):
        cursor = self.master.cget("cursor")
        if cursor != "" and cursor != "arrow": self._is_resizing = True
    def do_resize(self, event):
        if not self._is_resizing: return
        w, h = self.master.winfo_width(), self.master.winfo_height()
        dx, dy = event.x_root - self.master.winfo_rootx() - w, event.y_root - self.master.winfo_rooty() - h
        cursor = self.master.cget("cursor")
        if cursor == "sb_h_double_arrow": self.master.geometry(f"{w+dx}x{h}")
        elif cursor == "sb_v_double_arrow": self.master.geometry(f"{w}x{h+dy}")
        elif cursor == "bottom_right_corner": self.master.geometry(f"{w+dx}x{h+dy}")
    def toggle_title_bar(self, event=None):
        if self.title_bar.winfo_ismapped(): self.title_bar.pack_forget()
        else: self.title_bar.pack(side='top', fill='x', before=self.main_frame)
    
    def toggle_fullscreen(self, event=None):
        self._is_fullscreen = not self._is_fullscreen
        self.master.attributes("-fullscreen", self._is_fullscreen)
        
    def toggle_control_frame(self, event=None):
        if self.control_frame.winfo_ismapped(): self.control_frame.pack_forget()
        else: self.control_frame.pack(side='bottom', pady=(5,0))
    def schedule_sidebar_close(self, event=None):
        if self.sidebar_visible: self._sidebar_close_job = self.master.after(1500, self.toggle_sidebar)
    def cancel_sidebar_close(self, event=None):
        if self._sidebar_close_job: self.master.after_cancel(self._sidebar_close_job); self._sidebar_close_job = None
    def toggle_sidebar(self, event=None):
        self.cancel_sidebar_close()
        if self._sidebar_job: self.master.after_cancel(self._sidebar_job)
        if self.sidebar_visible: self.animate_sidebar(direction='out')
        else: self.sidebar.place(x=-200, y=0, relheight=1.0, width=200); self.animate_sidebar(direction='in')
        self.sidebar_visible = not self.sidebar_visible
    def animate_sidebar(self, direction='in'):
        start_x, end_x = (-200, 0) if direction == 'in' else (0, -200)
        animation_duration, animation_steps, sleep_interval = 200, 20, 10
        def animate(step=0):
            try:
                if step <= animation_steps:
                    fraction = 1 - pow(1 - (step / animation_steps), 3)
                    current_x = int(start_x + (end_x - start_x) * fraction)
                    self.sidebar.place(x=current_x, y=0, relheight=1.0, width=200)
                    self._sidebar_job = self.master.after(sleep_interval, animate, step + 1)
                elif direction == 'out': self.sidebar.place_forget()
            except tk.TclError: pass
        animate()
    def configure_styles(self):
        style = ttk.Style(); style.theme_use('clam'); style.configure('Dark.TFrame', background=self.dark_bg)
        style.configure('Dark.TNotebook', background=self.dark_bg, borderwidth=0, tabposition='ne')
        style.configure('Dark.TNotebook.Tab', background=self.button_bg, foreground=self.button_fg, borderwidth=0, padding=[10, 5])
        style.map('Dark.TNotebook.Tab', background=[('selected', self.active_bg), ('active', '#454545')], foreground=[('selected', self.button_fg)])
    def add_tab(self, event=None):
        tab_count = len(self.notebook.tabs()) + 1; new_tab = CalculatorTab(self.notebook, self)
        self.notebook.add(new_tab, text=f'Calc {tab_count}'); self.notebook.select(new_tab) 
    def close_tab(self, event=None):
        if not self.notebook.tabs(): return
        selected_tab = self.master.nametowidget(self.notebook.select())
        tab_text = self.notebook.tab(selected_tab, "text")
        self.closed_tabs.append((tab_text, selected_tab))
        self.notebook.forget(selected_tab)
    
    def reopen_closed_tab(self, event=None):
        if not self.closed_tabs:
            self.show_notification("No tabs to reopen")
            return
        tab_text, tab_widget = self.closed_tabs.pop()
        self.notebook.add(tab_widget, text=tab_text)
        self.notebook.select(tab_widget)
        self.show_notification("Tab reopened")

    def on_ctrl_press(self, event):
        self.is_ctrl_pressed = True
        try:
            self.preview_index = self.notebook.index('current')
        except tk.TclError:
            self.is_ctrl_pressed = False

    def on_ctrl_release(self, event):
        self.is_ctrl_pressed = False
        if self.tab_preview_window and self.tab_preview_window.winfo_exists():
            self.notebook.select(self.preview_index)
            self.tab_preview_window.destroy()
            self.tab_preview_window = None

    def cycle_tabs(self, event):
        if not self.is_ctrl_pressed or len(self.notebook.tabs()) < 2:
            return "break"

        if not self.tab_preview_window or not self.tab_preview_window.winfo_exists():
            self.show_tab_preview()
        
        num_tabs = len(self.notebook.tabs())
        self.preview_index = (self.preview_index + 1) % num_tabs
        
        self.update_tab_preview()
        return "break"

    def show_tab_preview(self):
        self.tab_preview_window = tk.Toplevel(self.master)
        self.tab_preview_window.overrideredirect(True)
        self.tab_preview_window.attributes('-alpha', 0.9)
        self.tab_preview_window.attributes('-topmost', True)

        self.preview_label = tk.Label(self.tab_preview_window, text="", bg=self.entry_bg, fg=self.entry_fg, font=('Arial', 14), padx=20, pady=10)
        self.preview_label.pack()
        self.update_tab_preview()

    def update_tab_preview(self):
        if self.tab_preview_window and self.tab_preview_window.winfo_exists():
            tab_widget = self.master.nametowidget(self.notebook.tabs()[self.preview_index])
            tab_text = self.notebook.tab(tab_widget, "text")
            result_preview = tab_widget.result_var.get() or "0"
            preview_text = f"{tab_text}: {result_preview}"
            self.preview_label.config(text=preview_text)
            
            self.tab_preview_window.update_idletasks()
            x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (self.tab_preview_window.winfo_width() // 2)
            y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (self.tab_preview_window.winfo_height() // 2)
            self.tab_preview_window.geometry(f"+{x}+{y}")

    def rename_current_tab(self, event=None):
        if not self.notebook.tabs(): return
        current_tab_id = self.notebook.select(); current_name = self.notebook.tab(current_tab_id, "text")
        dialog = CustomRenameDialog(self.master, "Rename Tab", initialvalue=current_name); new_name = dialog.result
        if new_name and new_name.strip(): self.notebook.tab(current_tab_id, text=new_name.strip())
    def show_notification(self, message, duration=1200):
        if self._toast_job: self.master.after_cancel(self._toast_job)
        if self._toast_label: self._toast_label.destroy()
        self._toast_label = tk.Label(self.master, text=message, bg='#303030', fg='white', font=('Arial', 10), padx=15, pady=8, highlightbackground='#606060', highlightthickness=1)
        end_rely, start_rely, animation_duration, animation_steps, sleep_interval = 0.95, 1.1, 250, 25, 10
        def animate(step=0, direction='in'):
            try:
                if direction == 'in':
                    if step <= animation_steps:
                        fraction = 1 - (1 - (step / 20)) ** 3; current_rely = start_rely - (start_rely - end_rely) * fraction
                        self._toast_label.place(relx=0.5, rely=current_rely, anchor='center')
                        self._toast_job = self.master.after(sleep_interval, animate, step + 1, 'in')
                    else: self._toast_job = self.master.after(duration, animate, 0, 'out')
                elif direction == 'out':
                    if step <= animation_steps:
                        fraction = (step / animation_steps) ** 3; current_rely = end_rely + (start_rely - end_rely) * fraction
                        self._toast_label.place(relx=0.5, rely=current_rely, anchor='center')
                        self._toast_job = self.master.after(sleep_interval, animate, step + 1, 'out')
                    else: self._toast_label.destroy(); self._toast_label = None
            except tk.TclError: pass
        animate()

if __name__ == "__main__":
    # This is the hidden parent window that handles the taskbar icon
    root = tk.Tk()
    root.title("Zenth") # The title for the taskbar
    
    # This is the visible, custom-framed calculator window
    app_window = tk.Toplevel(root)
    app = TabbedCalculatorApp(app_window, root)
    running_apps.append(app)

    # This function shows the calculator window when the taskbar icon is clicked
    def on_map(event):
        # When the hidden root is restored, show the main app window
        app_window.deiconify()
    
    # Hide the hidden window itself, but keep it running for the taskbar icon
    root.withdraw()
    root.bind("<Map>", on_map)
    
    root.mainloop()

