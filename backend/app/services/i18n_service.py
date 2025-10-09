"""
Internationalization Service
Loads and provides translations for multiple languages
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Cache for loaded translations
_translations_cache: Dict[str, Dict[str, str]] = {}

def load_translations(language: str) -> Dict[str, str]:
    """
    Load translations for a specific language
    
    Args:
        language: Language code (en, hi, rj)
        
    Returns:
        Dictionary of translation keys to values
    """
    if language in _translations_cache:
        return _translations_cache[language]
    
    try:
        i18n_dir = Path(__file__).parent.parent / "i18n"
        file_path = i18n_dir / f"{language}.json"
        
        if not file_path.exists():
            logger.warning(f"Translation file not found: {file_path}, falling back to English")
            language = "en"
            file_path = i18n_dir / "en.json"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        _translations_cache[language] = translations
        logger.info(f"Loaded {len(translations)} translations for {language}")
        return translations
        
    except Exception as e:
        logger.error(f"Error loading translations for {language}: {e}")
        return {}


def get_translation(key: str, language: str = "en", **kwargs) -> str:
    """
    Get a translated string for a key
    
    Args:
        key: Translation key
        language: Language code
        **kwargs: Variables to substitute in template
        
    Returns:
        Translated string with substitutions
    """
    translations = load_translations(language)
    text = translations.get(key, key)
    
    # Substitute variables
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing variable {e} for translation key {key}")
    
    return text


def get_supported_languages() -> list:
    """Get list of supported language codes"""
    return ["en", "hi", "rj"]


def clear_cache():
    """Clear the translations cache"""
    global _translations_cache
    _translations_cache = {}
    logger.info("Translations cache cleared")
