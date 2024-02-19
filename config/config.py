import os
import threading
import yaml
import sys

class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class Config(metaclass=SingletonMeta):
    def __init__(self):
        self.data = None
        self.initialized = False
        # config_files_path=os.path.join(os.path.dirname(__file__))
        self.config_files_path = self.get_config_path()

    def get_config_path(self):
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app 
            # path into variable _MEIPASS'.
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.dirname(__file__))

        return os.path.join(application_path, 'config_files')

    # config_path = get_config_path()
    # # Now you can use config_path to load your configuration file


    def initialize(self):
        if not self.initialized:
            env = os.getenv("ENVIRONMENT", "production")            
            file_name = 'config.yaml' if env == "production" else 'config_dev.yaml'
            file_path = os.path.join(self.config_files_path, file_name)
            with open(file_path) as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
            self.initialized = True

    def get(self, key, default=None):
        if not self.initialized:
            raise Exception("Config not initialized. Call initialize() first.")

        key_parts = key.split('.')
        current_data = self.data

        for part in key_parts:
            if isinstance(current_data, dict) and part in current_data:
                current_data = current_data[part]
            else:
                return default  # Return default value if key part is not found

        return current_data if current_data is not None else default
        