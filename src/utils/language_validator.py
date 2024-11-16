from typing import Optional
import pycountry
import logging

logger = logging.getLogger(__name__)

class LanguageValidator:
    """
    Validates and normalizes language codes.
    Supports all ISO 639-1 (2-letter) and ISO 639-2 (3-letter) codes via pycountry.
    """
    
    FALLBACK_LANG = 'en'

    @classmethod
    def validate_language(cls, lang_code: str) -> str:
        """
        Validates and normalizes a language code.
        
        Args:
            lang_code: Language code to validate
            
        Returns:
            str: Normalized language code or fallback language if invalid
        """
        if not lang_code:
            logger.warning(f"Empty language code provided. Using fallback: {cls.FALLBACK_LANG}")
            return cls.FALLBACK_LANG

        # Normalize to lowercase and strip whitespace
        normalized_code = lang_code.lower().strip()

        try:
            # Check ISO 639-1 (2-letter) codes
            lang = pycountry.languages.get(alpha_2=normalized_code)
            if lang:
                return lang.alpha_2

            # Check ISO 639-2 (3-letter) codes
            lang = pycountry.languages.get(alpha_3=normalized_code)
            if lang and hasattr(lang, 'alpha_2'):
                return lang.alpha_2

        except (AttributeError, KeyError) as e:
            logger.warning(f"Error validating language code: {e}")

        logger.warning(
            f"Unsupported language code: {lang_code}. Using fallback: {cls.FALLBACK_LANG}"
        )
        return cls.FALLBACK_LANG

    @classmethod
    def get_supported_languages(cls) -> set:
        """
        Returns the set of all ISO 639-1 language codes supported by pycountry.
        
        Returns:
            set: A set of 2-letter ISO 639-1 codes.
        """
        supported_languages = {
            lang.alpha_2 for lang in pycountry.languages if hasattr(lang, 'alpha_2')
        }
        return supported_languages
