import json
import os

class LanguageManager:
    """Manages application translations"""
    
    def __init__(self):
        self.current_language = "en"
        self.translations = {}
        self.languages_dir = os.path.join(os.path.dirname(__file__), "languages")
        self.load_language("en")
    
    def load_language(self, lang_code):
        """Load language file"""
        lang_file = os.path.join(self.languages_dir, f"{lang_code}.json")
        
        if os.path.exists(lang_file):
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
                    self.current_language = lang_code
                    return True
            except Exception as e:
                print(f"Error loading language {lang_code}: {e}")
        
        return False
    
    def get(self, key, default=""):
        """Get translation by key (supports nested keys like 'sidebar.dashboard')"""
        keys = key.split('.')
        value = self.translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value if isinstance(value, str) else default
    
    def get_available_languages(self):
        """Get list of available languages"""
        languages = []
        if os.path.exists(self.languages_dir):
            for file in os.listdir(self.languages_dir):
                if file.endswith('.json'):
                    lang_code = file[:-5]
                    languages.append({
                        "code": lang_code,
                        "name": self._get_language_name(lang_code)
                    })
        return languages
    
    def _get_language_name(self, code):
        """Get language display name"""
        names = {
            "en": "English",
            "ar": "العربية",
            "fr": "Français"
        }
        return names.get(code, code.upper())


# Global instance
_language_manager = None

def get_language_manager():
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager