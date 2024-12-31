from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0
import deepl

***REMOVED*** = 'c41e3483-1b4c-411f-ad34-e2063f3bfe1d'
translator = deepl.Translator(***REMOVED***)

def translate_to_german(text):
    try:
        result = translator.translate_text(text, target_lang="DE")
        return result.text
    except Exception as e:
        return f"An error occurred: {e}"