import json
import os
from typing import Dict, Any

# Supported languages with their codes and names
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'हिन्दी',
    'bn': 'বাংলা',
    'ta': 'தமிழ்',
    'te': 'తెలుగు',
    'mr': 'मराठी',
    'gu': 'ગુજરાતી',
    'pa': 'ਪੰਜਾਬੀ',
    'kn': 'ಕನ್ನಡ',
    'ml': 'മലയാളം',
    'ur': 'اردو',
    'ne': 'नेपाली',
    'id': 'Indonesia',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'ru': 'Русский',
    'tr': 'Türkçe',
    'pt': 'Português',
    'ar': 'العربية',
    'ja': '日本語',
    'ko': '한국어',
    'zh': '中文'
}

class TranslationManager:
    _instance = None
    _translations: Dict[str, Dict[str, str]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_translations()
        return cls._instance
    
    def _load_translations(self):
        """Load all translation files"""
        locales_dir = os.path.join(os.path.dirname(__file__))
        
        for lang_code in SUPPORTED_LANGUAGES.keys():
            file_path = os.path.join(locales_dir, f"{lang_code}.json")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._translations[lang_code] = json.load(f)
            except FileNotFoundError:
                # Use empty dict and fallback to English
                self._translations[lang_code] = {}
    
    def get(self, key: str, lang_code: str = 'en', **kwargs) -> str:
        """Get translation for a key with optional formatting"""
        # Get translation from requested language
        translations = self._translations.get(lang_code, {})
        text = translations.get(key)
        
        # Fallback to English if not found
        if text is None and lang_code != 'en':
            translations = self._translations.get('en', {})
            text = translations.get(key, key)
        elif text is None:
            text = key
        
        # Format with kwargs
        if kwargs:
            try:
                text = text.format(**kwargs)
            except:
                # If formatting fails, return unformatted text
                pass
        
        return text

# Global translation manager
translations = TranslationManager()

def get_translation(key: str, lang_code: str = 'en', **kwargs) -> str:
    """Helper function to get translations"""
    return translations.get(key, lang_code, **kwargs)
