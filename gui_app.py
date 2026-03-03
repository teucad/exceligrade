import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import requests
from app import app
import time
import os


# Start Flask server in background
def run_server(port):
    app.run(host='127.0.0.1', port=port, threaded=True, use_reloader=False)


class ExceligradeGUI:
    def __init__(self, root, port=5000):
        self.root = root
        self.port = port
        self.url = f'http://127.0.0.1:{port}'
        self.root.title('Exceligrade')
        self.root.geometry('1000x800')

        self.theme_file = os.path.join(os.path.expanduser('~'), '.exceligrade_theme.json')
        self.current_theme = self._load_theme_preference()
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            pass

        # Start Flask in background
        self.server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
        self.server_thread.start()
        time.sleep(1)  # Give server time to start

        self.create_ui()
        self.apply_theme(self.current_theme)

    def create_ui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header with title and theme toggle
        header = ttk.Frame(self.main_frame)
        header.pack(fill=tk.X)

        title_block = ttk.Frame(header)
        title_block.pack(side=tk.LEFT, fill=tk.X, expand=True)

        title = ttk.Label(title_block, text='Exceligrade', font=('Segoe UI', 18, 'bold'))
        title.pack(anchor='w')
        subtitle = ttk.Label(title_block, text='Turn your class syllabi into an editable Excel gradebook.')
        subtitle.pack(anchor='w')

        self.theme_btn = ttk.Button(header, text='', command=self.toggle_theme)
        self.theme_btn.pack(side=tk.RIGHT)

        # Controls frame
        self.ctrl_frame = ttk.Frame(self.main_frame)
        self.ctrl_frame.pack(fill=tk.X, pady=10)

        ttk.Button(self.ctrl_frame, text='+ Add Class', command=self.add_class).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.ctrl_frame, text='Extract Weights', command=self.extract_weights).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.ctrl_frame, text='Load JSON', command=self.load_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.ctrl_frame, text='Download JSON', command=self.download_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.ctrl_frame, text='Generate Excel', command=self.generate_excel).pack(side=tk.RIGHT, padx=5)

        # Classes container (scrollable)
        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.classes = []

        # Load default class
        self.add_class(prefill={'name': 'Example Class', 'assignments': [
            {'name': 'HW', 'weight': 20, 'count': 4},
            {'name': 'Exam', 'weight': 80, 'count': 2}
        ]})

    def _load_theme_preference(self):
        try:
            with open(self.theme_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('theme') in ('light', 'dark'):
                    return data['theme']
        except Exception:
            pass
        return 'light'

    def _save_theme_preference(self):
        try:
            with open(self.theme_file, 'w', encoding='utf-8') as f:
                json.dump({'theme': self.current_theme}, f)
        except Exception:
            pass

    def apply_theme(self, theme):
        palettes = {
            'light': {
                'bg': '#f7f9fc',
                'card': '#ffffff',
                'text': '#0f172a',
                'muted': '#6b7280',
                'border': '#e6e9ee',
                'entry_bg': '#ffffff',
                'button_bg': '#ffffff',
                'accent_bg': '#2563eb',
                'accent_fg': '#ffffff',
            },
            'dark': {
                'bg': '#0b1220',
                'card': '#172033',
                'text': '#e2e8f0',
                'muted': '#94a3b8',
                'border': '#334155',
                'entry_bg': '#0f172a',
                'button_bg': '#1e293b',
                'accent_bg': '#60a5fa',
                'accent_fg': '#0b1220',
            },
        }

        colors = palettes.get(theme, palettes['light'])
        self.current_theme = theme

        self.root.configure(bg=colors['bg'])
        self.canvas.configure(bg=colors['bg'])

        self.style.configure('.', background=colors['bg'], foreground=colors['text'])
        self.style.configure('TFrame', background=colors['bg'])
        self.style.configure('Card.TLabelframe', background=colors['card'], bordercolor=colors['border'])
        self.style.configure('Card.TLabelframe.Label', background=colors['card'], foreground=colors['text'])
        self.style.configure('TLabel', background=colors['bg'], foreground=colors['text'])
        self.style.configure('Muted.TLabel', background=colors['bg'], foreground=colors['muted'])
        self.style.configure('TButton', background=colors['button_bg'], foreground=colors['text'], bordercolor=colors['border'])
        self.style.map('TButton', background=[('active', colors['card'])])
        self.style.configure('Primary.TButton', background=colors['accent_bg'], foreground=colors['accent_fg'])
        self.style.map('Primary.TButton', background=[('active', colors['accent_bg'])])
        self.style.configure('TEntry', fieldbackground=colors['entry_bg'], foreground=colors['text'])

        # Refresh card/canvas colors
        for cls in self.classes:
            cls['frame'].configure(style='Card.TLabelframe')
            cls['assigns_frame'].configure(style='Card.TLabelframe')

        label = '☀️ Light mode' if theme == 'dark' else '🌙 Dark mode'
        self.theme_btn.configure(text=label)
        self._save_theme_preference()

    def toggle_theme(self):
        next_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme(next_theme)

    def add_class(self, prefill=None):
        class_frame = ttk.LabelFrame(self.scrollable_frame, text='Class', padding=10, style='Card.TLabelframe')
        class_frame.pack(fill=tk.X, padx=5, pady=5)

        # Class name
        ttk.Label(class_frame, text='Class Name:').pack(anchor='w')
        name_var = tk.StringVar(value=prefill.get('name', '') if prefill else '')
        ttk.Entry(class_frame, textvariable=name_var).pack(fill=tk.X, pady=(0, 10))

        # Assignments
        assigns_frame = ttk.LabelFrame(class_frame, text='Assignments', padding=5, style='Card.TLabelframe')
        assigns_frame.pack(fill=tk.X, pady=5)

        # Header
        header_frame = ttk.Frame(assigns_frame)
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text='Assignment', width=30).pack(side=tk.LEFT)
        ttk.Label(header_frame, text='Weight', width=10).pack(side=tk.LEFT)
        ttk.Label(header_frame, text='Count', width=8).pack(side=tk.LEFT)

        assign_rows = []

        def add_assignment(data=None):
            row_frame = ttk.Frame(assigns_frame)
            row_frame.pack(fill=tk.X, pady=2)

            name_var = tk.StringVar(value=data.get('name', '') if data else '')
            # Use StringVar so partially-typed numeric input doesn't crash when read.
            weight_var = tk.StringVar(value=str(data.get('weight', 0) if data else 0))
            count_var = tk.StringVar(value=str(data.get('count', 1) if data else 1))

            ttk.Entry(row_frame, textvariable=name_var, width=30).pack(side=tk.LEFT, padx=2)
            ttk.Entry(row_frame, textvariable=weight_var, width=10).pack(side=tk.LEFT, padx=2)
            ttk.Entry(row_frame, textvariable=count_var, width=8).pack(side=tk.LEFT, padx=2)
            ttk.Button(row_frame, text='Remove', command=lambda: (row_frame.destroy(), assign_rows.remove(row))).pack(side=tk.LEFT, padx=2)

            row = {'frame': row_frame, 'name': name_var, 'weight': weight_var, 'count': count_var}
            assign_rows.append(row)

        if prefill and prefill.get('assignments'):
            for a in prefill['assignments']:
                add_assignment(a)

        ttk.Button(assigns_frame, text='+ Add Assignment', command=add_assignment).pack(anchor='w', pady=5)

        # Remove class button
        ttk.Button(class_frame, text='Remove Class', command=lambda: (class_frame.destroy(), self.classes.remove(cls_data))).pack(anchor='w', pady=5)

        cls_data = {
            'frame': class_frame,
            'name': name_var,
            'assignments': assign_rows,
            'add_assignment': add_assignment,
            'assigns_frame': assigns_frame,
        }
        self.classes.append(cls_data)

    def build_data(self):
        """Build JSON data from UI"""
        classes = []
        for cls in self.classes:
            assigns = []
            for row in cls['assignments']:
                nm = row['name'].get().strip()
                wt_raw = row['weight'].get().strip()
                cnt_raw = row['count'].get().strip()

                try:
                    wt = float(wt_raw) if wt_raw else 0
                except ValueError:
                    wt = 0

                try:
                    cnt = int(cnt_raw) if cnt_raw else 1
                except ValueError:
                    cnt = 1

                if cnt < 1:
                    cnt = 1

                if nm and wt > 0:  # Skip empty/zero rows
                    assigns.append({'name': nm, 'weight': wt, 'count': cnt})
            classes.append({'name': cls['name'].get() or 'Class', 'assignments': assigns})
        return {'classes': classes}

    def download_json(self):
        data = self.build_data()
        file = filedialog.asksaveasfile(mode='w', defaultextension='.json', filetypes=[('JSON files', '*.json'), ('All files', '*.*')])
        if file:
            json.dump(data, file, indent=2)
            file.close()
            messagebox.showinfo('Success', 'JSON saved')

    def load_json(self):
        file = filedialog.askopenfile(mode='r', filetypes=[('JSON files', '*.json'), ('All files', '*.*')])
        if file:
            try:
                data = json.load(file)
                if not data or not isinstance(data.get('classes'), list):
                    messagebox.showerror('Error', 'Invalid JSON format')
                    return
                # Clear existing classes
                for cls in self.classes[:]:
                    cls['frame'].destroy()
                self.classes = []
                # Load new classes
                for c in data['classes']:
                    self.add_class(c)
                messagebox.showinfo('Success', f'Loaded {len(data["classes"])} classes')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to load JSON: {str(e)}')

    def extract_weights(self):
        file = filedialog.askopenfile(filetypes=[('All', '*.*'), ('PDF', '*.pdf'), ('DOCX', '*.docx'), ('TXT', '*.txt')])
        if not file:
            return

        try:
            files = {'file': (file.name, file, 'application/octet-stream')}
            resp = requests.post(f'{self.url}/extract', files=files)
            if resp.status_code != 200:
                messagebox.showerror('Error', resp.text[:500])
                return
            result = resp.json()
            assigns = result.get('assignments', [])
            if not assigns:
                messagebox.showwarning('No matches', 'No assignments found in file')
                return
            # Add to last class or create new
            if self.classes:
                cls = self.classes[-1]
            else:
                self.add_class()
                cls = self.classes[-1]

            # Use the add_assignment callback to add each extracted assignment
            for a in assigns:
                cls['add_assignment']({'name': a.get('name', ''), 'weight': a.get('weight', 0), 'count': 1})

            messagebox.showinfo('Success', f'Extracted {len(assigns)} assignments')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def generate_excel(self):
        data = self.build_data()
        try:
            resp = requests.post(f'{self.url}/generate', json=data)
            if resp.status_code != 200:
                messagebox.showerror('Error', resp.text[:500])
                return

            file = filedialog.asksaveasfile(mode='wb', defaultextension='.xlsx', filetypes=[('Excel Workbook', '*.xlsx'), ('All files', '*.*')])
            if file:
                file.write(resp.content)
                file.close()
                messagebox.showinfo('Success', 'Excel file created')
        except Exception as e:
            messagebox.showerror('Error', str(e))


if __name__ == '__main__':
    root = tk.Tk()
    app_gui = ExceligradeGUI(root)
    root.mainloop()
