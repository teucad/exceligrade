import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import webbrowser
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
        
        # Start Flask in background
        self.server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
        self.server_thread.start()
        time.sleep(1)  # Give server time to start
        
        self.create_ui()
        
    def create_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = ttk.Label(main_frame, text='Exceligrade', font=('Segoe UI', 18, 'bold'))
        title.pack(anchor='w')
        subtitle = ttk.Label(main_frame, text='Turn your class syllabi into an editable Excel gradebook.')
        subtitle.pack(anchor='w')
        
        # Controls frame
        ctrl_frame = ttk.Frame(main_frame)
        ctrl_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(ctrl_frame, text='+ Add Class', command=self.add_class).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(ctrl_frame, text='Extract Weights', command=self.extract_weights).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text='Load JSON', command=self.load_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text='Download JSON', command=self.download_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text='Generate Excel', command=self.generate_excel).pack(side=tk.RIGHT, padx=5)
        
        # Classes container (scrollable)
        self.canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.classes = []
        
        # Load default class
        self.add_class(prefill={'name': 'Example Class', 'assignments': [
            {'name': 'HW', 'weight': 20, 'count': 4},
            {'name': 'Exam', 'weight': 80, 'count': 2}
        ]})
        
    def add_class(self, prefill=None):
        class_frame = ttk.LabelFrame(self.scrollable_frame, text='Class', padding=10)
        class_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Class name
        ttk.Label(class_frame, text='Class Name:').pack(anchor='w')
        name_var = tk.StringVar(value=prefill.get('name', '') if prefill else '')
        ttk.Entry(class_frame, textvariable=name_var).pack(fill=tk.X, pady=(0, 10))
        
        # Assignments
        assigns_frame = ttk.LabelFrame(class_frame, text='Assignments', padding=5)
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
        
        cls_data = {'frame': class_frame, 'name': name_var, 'assignments': assign_rows, 'add_assignment': add_assignment}
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
        file = filedialog.asksaveasfile(mode='w', suffix='.json', defaultextension='.json')
        if file:
            json.dump(data, file, indent=2)
            file.close()
            messagebox.showinfo('Success', 'JSON saved')
    
    def load_json(self):
        file = filedialog.askopenfile(mode='r', suffix='.json')
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
            
            file = filedialog.asksaveasfile(mode='wb', suffix='.xlsx', defaultextension='.xlsx')
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
