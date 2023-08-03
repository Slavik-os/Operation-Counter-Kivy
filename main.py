from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.image import Image
import json
import datetime
import requests
import getpass
import kivy


class SearchableDropDown(BoxLayout):
    def __init__(self, **kwargs):
        super(SearchableDropDown, self).__init__(**kwargs)

        # Initialize the data
        self.options = []
        self.filtered_options = []

        # Create the TextInput for search
        self.search_input = TextInput(hint_text='Search par numero de dossier...', multiline=False, size_hint=(1, None), height=30, font_size=15)
        self.search_input.bind(text=self.filter_options)
        self.add_widget(self.search_input)

        # Create the Popup for displaying suggestions
        self.popup = Popup(title='Select an option', size_hint=(0.8, 0.8), auto_dismiss=False)
        self.popup.content = BoxLayout(orientation='vertical', spacing=10, padding=10)



    def filter_options(self, instance, value):
        # Filter the options based on the search query
        self.filtered_options = [option for option in self.options if value.lower() in option.lower()]

        # Update the Popup content with filtered options
        self.popup.content.clear_widgets()
        for option in self.filtered_options:
            btn = Button(text=option, size_hint_y=None, height=30, font_size=15)
            btn.bind(on_release=self.select_option)
            self.popup.content.add_widget(btn)

        # Show the Popup if the search query is not empty
        if value.strip():
            self.popup.open()
        else:
            self.popup.dismiss()
    def select_option(self, instance):
        # Update the TextInput with the selected option, store the value, and close the Popup
        self.search_input.text = instance.text
        self.selected_value = instance.text
        self.popup.dismiss()


class FolderApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        icon = Image(source='icon.png', size_hint=(None, None), size=(60, 60))
        layout.add_widget(icon)
        # Label
        label = Label(text="Puerto Folder Counter", font_size=20, size_hint=(1, None), height=40)
        layout.add_widget(label)

        # Folder input field
        self.folder_input = TextInput(hint_text='Numero de dossier', multiline=False, size_hint=(1, None), height=30, font_size=15)
        layout.add_widget(self.folder_input)

        # Custom Searchable Dropdown
        self.search_dropdown = SearchableDropDown()
        layout.add_widget(self.search_dropdown)


        # Dum input field
        self.dum_input = TextInput(hint_text='Numero de DUM', multiline=False, size_hint=(1, None), height=30, font_size=15)
        layout.add_widget(self.dum_input)

        # Message label
        self.message_label = Label(text="", font_size=15, color=(0, 1, 0, 1))
        layout.add_widget(self.message_label)

        # Button
        button = Button(text='Submit', size_hint=(1, None), height=30, font_size=15)
        button.bind(on_press=self.on_submit)
        layout.add_widget(button)
        # Start updating data every 1 seconds (adjust the interval as needed)
        Clock.schedule_interval(self.update_data, 1)


        return layout

    def update_data(self, dt=None):
        def on_success(req, result):
            try:
                # Parse the JSON data and extract the "folderNumber" values
                folders = json.loads(result)
                options = [folder["folderNumber"] for folder in folders]

                # Update the SearchableDropDown's options
                self.search_dropdown.options = options

            except json.JSONDecodeError:
                print("Failed to parse JSON data.")
            except KeyError:
                print("Malformed JSON data. 'folderNumber' key not found.")
            except Exception as e:
                print(f"Error: {e}")

        def on_failure(req, result):
            print("Failed to fetch data.")

        url = "http://10.0.0.245:8080/folders.php"
        UrlRequest(url, on_success, on_failure)

    def on_submit(self, instance):
        folder_path = self.folder_input.text.upper()
        try :
            selected_option = self.search_dropdown.selected_value
        except :
            selected_option = ''
        # User info
        session_name = getpass.getuser()
        current_submit_date = datetime.datetime.now()
        url = "http://10.0.0.245:8080/app.php"


        if (selected_option.strip() == '' and folder_path.strip() == '') :
            self.show_notification("Must Enter a value")

        def insert_dum():
            data = {"username":session_name,"date":current_submit_date,"folder_number":selected_option.upper(),"type":"dum","dum":self.dum_input.text.upper()}
            print(data)
            print("-> DUM")

            req = requests.post(url, data = data)
            print(req.text)
            message = "Inserted"
            self.message_label.text = f"{message}"

        def insert_folder():
            data = {"username":session_name,"date":current_submit_date,"folder_number":folder_path,"type":"folder"}
            print("-> FOLDER")
            print(data)
            # Returns Check

            req = requests.post(url, data = data)
            print(req.text)
            message = "Inserted !"
            if 'Exists' in req.text :
                print("dum already exist")
                message = "Folder Arleady exists"

            self.message_label.text = f"{message}"

        if folder_path != '':
            insert_folder()

        dum = self.dum_input.text
        if (dum.strip() != '' and selected_option.strip() != ''):
            insert_dum()

    def show_notification(self, message):
        content = Label(text=message)
        popup = Popup(title='Notification', content=content, size_hint=(None, None), size=(200, 100))
        popup.open()

if __name__ == '__main__':
    Window.size = (500, 350)
    FolderApp().run()