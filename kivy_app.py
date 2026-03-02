import kivy
from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
import threading
import requests
import json
import time

# Set window size for mobile-like aspect ratio
Window.size = (480, 800)

class ExceligradeKivy(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.port = 5000
        self.url = f'http://127.0.0.1:{self.port}'
        self.classes = []
        
    def build(self):
        # Start Flask server in background
        from app import app
        def run_server():
            app.run(host='127.0.0.1', port=self.port, threaded=True, use_reloader=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(1)  # Give server time to start
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(text='Exceligrade', size_hint_y=None, height=60, font_size='28sp')
        main_layout.add_widget(title)
        
        # Controls
        ctrl_layout = BoxLayout(size_hint_y=None, height=50, spacing=5)
        ctrl_layout.add_widget(Button(text='+ Class', on_press=self.add_class, size_hint_x=0.25))
        ctrl_layout.add_widget(Button(text='Extract', on_press=self.extract, size_hint_x=0.25))
        ctrl_layout.add_widget(Button(text='Load JSON', on_press=self.load_json, size_hint_x=0.25))
        ctrl_layout.add_widget(Button(text='Generate', on_press=self.generate_excel, size_hint_x=0.25))
        main_layout.add_widget(ctrl_layout)
        
        # More controls
        ctrl_layout2 = BoxLayout(size_hint_y=None, height=50, spacing=5)
        ctrl_layout2.add_widget(Button(text='Save JSON', on_press=self.save_json, size_hint_x=0.5))
        main_layout.add_widget(ctrl_layout2)
        
        # Scrollable classes area
        scroll = ScrollView()
        self.classes_box = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.classes_box.bind(minimum_height=self.classes_box.setter('height'))
        scroll.add_widget(self.classes_box)
        main_layout.add_widget(scroll)
        
        # Add default class
        self.add_class_data({'name': 'Example Class', 'assignments': [
            {'name': 'HW', 'weight': 20, 'count': 4},
            {'name': 'Exam', 'weight': 80, 'count': 2}
        ]})
        
        return main_layout
    
    def add_class(self, instance):
        self.add_class_data()
    
    def add_class_data(self, prefill=None):
        class_data = {
            'name': '',
            'assignments': [],
            'name_input': None,
            'assign_box': None
        }
        
        # Create class card
        class_box = BoxLayout(orientation='vertical', size_hint_y=None, height=300, spacing=5)
        
        # Class name input
        class_data['name_input'] = TextInput(text=prefill.get('name', '') if prefill else '', 
                                             multiline=False, size_hint_y=None, height=40)
        class_box.add_widget(Label(text='Class Name:', size_hint_y=None, height=30, font_size='12sp'))
        class_box.add_widget(class_data['name_input'])
        
        # Assignments section
        class_box.add_widget(Label(text='Assignments:', size_hint_y=None, height=30, font_size='12sp'))
        
        assign_scroll = ScrollView(size_hint_y=0.8)
        class_data['assign_box'] = GridLayout(cols=1, spacing=5, size_hint_y=None)
        class_data['assign_box'].bind(minimum_height=class_data['assign_box'].setter('height'))
        assign_scroll.add_widget(class_data['assign_box'])
        class_box.add_widget(assign_scroll)
        
        # Add assignment button
        class_box.add_widget(Button(text='+ Assignment', size_hint_y=None, height=40,
                                     on_press=lambda x: self.add_assignment(class_data)))
        
        # Remove class button
        class_box.add_widget(Button(text='Remove Class', size_hint_y=None, height=40,
                                     on_press=lambda x: (self.classes_box.remove_widget(class_box), 
                                                         self.classes.remove(class_data))))
        
        self.classes_box.add_widget(class_box)
        self.classes.append(class_data)
        
        # Pre-fill assignments if provided
        if prefill and prefill.get('assignments'):
            for a in prefill['assignments']:
                self.add_assignment(class_data, a)
    
    def add_assignment(self, class_data, data=None):
        assign_layout = BoxLayout(size_hint_y=None, height=150, orientation='vertical', spacing=3)
        
        # Name
        name_input = TextInput(text=data.get('name', '') if data else '', 
                               multiline=False, size_hint_y=None, height=35, hint_text='Name')
        assign_layout.add_widget(name_input)
        
        # Weight
        weight_input = TextInput(text=str(data.get('weight', 0)) if data else '0',
                                 multiline=False, size_hint_y=None, height=35, hint_text='Weight (%)',
                                 input_filter='float')
        assign_layout.add_widget(weight_input)
        
        # Count
        count_input = TextInput(text=str(data.get('count', 1)) if data else '1',
                               multiline=False, size_hint_y=None, height=35, hint_text='Count',
                               input_filter='int')
        assign_layout.add_widget(count_input)
        
        # Remove button
        assign_layout.add_widget(Button(text='Remove', size_hint_y=None, height=35,
                                        on_press=lambda x: class_data['assign_box'].remove_widget(assign_layout)))
        
        assign = {'layout': assign_layout, 'name': name_input, 'weight': weight_input, 'count': count_input}
        class_data['assignments'].append(assign)
        class_data['assign_box'].add_widget(assign_layout)
    
    def build_data(self):
        """Build JSON data from UI"""
        classes = []
        for cls in self.classes:
            assigns = []
            for row in cls['assignments']:
                nm = row['name'].text.strip()
                try:
                    wt = float(row['weight'].text)
                except:
                    wt = 0
                try:
                    cnt = int(row['count'].text)
                except:
                    cnt = 1
                if nm and wt > 0:
                    assigns.append({'name': nm, 'weight': wt, 'count': cnt})
            classes.append({'name': cls['name_input'].text or 'Class', 'assignments': assigns})
        return {'classes': classes}
    
    def extract(self, instance):
        # File chooser popup
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(filters=['*.pdf', '*.docx', '*.txt'])
        content.add_widget(filechooser)
        
        def do_extract(path):
            if not filechooser.selection:
                print('No file selected')
                popup.dismiss()
                return
            
            file_path = filechooser.selection[0]
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (file_path.split('/')[-1], f, 'application/octet-stream')}
                    resp = requests.post(f'{self.url}/extract', files=files)
                    if resp.status_code == 200:
                        result = resp.json()
                        assigns = result.get('assignments', [])
                        if assigns and self.classes:
                            for a in assigns:
                                self.add_assignment(self.classes[-1], a)
                            print(f'Extracted {len(assigns)} assignments')
                        popup.dismiss()
            except Exception as e:
                print(f'Error: {str(e)}')
        
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        btn_layout.add_widget(Button(text='Extract', on_press=lambda x: do_extract(None)))
        btn_layout.add_widget(Button(text='Cancel', on_press=lambda x: popup.dismiss()))
        content.add_widget(btn_layout)
        
        popup = Popup(title='Select Syllabus File', content=content, size_hint=(0.9, 0.9))
        popup.open()
    
    def generate_excel(self, instance):
        data = self.build_data()
        try:
            resp = requests.post(f'{self.url}/generate', json=data)
            if resp.status_code == 200:
                # Save to Downloads folder (Android)
                import os
                download_path = os.path.expanduser('~/Downloads/gradebook.xlsx')
                with open(download_path, 'wb') as f:
                    f.write(resp.content)
                print(f'Saved to {download_path}')
            else:
                print(f'Error: {resp.text[:200]}')
        except Exception as e:
            print(f'Error: {str(e)}')
    
    def save_json(self, instance):
        data = self.build_data()
        try:
            import os
            download_path = os.path.expanduser('~/Downloads/syllabus.json')
            with open(download_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f'Saved JSON to {download_path}')
        except Exception as e:
            print(f'Error: {str(e)}')
    
    def load_json(self, instance):
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(filters=['*.json'])
        content.add_widget(filechooser)
        
        def do_load(x):
            if not filechooser.selection:
                popup.dismiss()
                return
            
            try:
                with open(filechooser.selection[0], 'r') as f:
                    data = json.load(f)
                    # Clear existing
                    self.classes_box.clear_widgets()
                    self.classes = []
                    # Load new
                    for c in data.get('classes', []):
                        self.add_class_data(c)
                    popup.dismiss()
            except Exception as e:
                print(f'Error: {str(e)}')
        
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        btn_layout.add_widget(Button(text='Load', on_press=do_load))
        btn_layout.add_widget(Button(text='Cancel', on_press=lambda x: popup.dismiss()))
        content.add_widget(btn_layout)
        
        popup = Popup(title='Load JSON', content=content, size_hint=(0.9, 0.9))
        popup.open()

if __name__ == '__main__':
    ExceligradeKivy().run()
