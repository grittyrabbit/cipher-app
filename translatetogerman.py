from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0
import deepl

translator = deepl.Translator(***REMOVED***)

def translate_to_german(text):
    try:
        result = translator.translate_text(text, target_lang="DE")
        return result.text
    except Exception as e:
        return f"An error occurred: {e}"
