import os
import yaml


def load_all_languages():
    """Load all language files"""
    _texts = {}
    _languages = []

    current_directory = os.path.dirname(os.path.realpath(__file__))
    language_directory = 'language'
    language_directory_path = os.path.join(current_directory, language_directory)

    for filename in os.listdir(language_directory_path):
        if filename.endswith(".yaml"):
            lang_id = filename.replace('.yaml', '')
            _languages.append(lang_id)
            file_path = os.path.join(language_directory_path, filename)
            with open(file=file_path, mode='r', encoding="utf-8") as data:
                _texts[lang_id] = yaml.load(data, Loader=yaml.FullLoader)
    
    return _languages, _texts

_languages, _texts = load_all_languages()

def _(key, language) -> str:
    
    if language in _texts and key in _texts[language]:
        return _texts[language][key]
    else: 
        return None

def get_all_languages():
    """Get list of supported languages"""

    return _languages


def get_translations_from_key(key):
    """Get the list of all translations for specific key"""
    
    translations = []
    for language in _languages:
        translations.append(_(key, language))

    return translations

def check_language_by_text(key, text):
    "Get language of given text"

    for language in _languages:
        if _(key, language) == text:
            return language

