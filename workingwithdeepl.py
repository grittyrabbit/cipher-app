import deepl

# Replace 'YOUR_API_KEY' with your actual DeepL API key
***REMOVED*** = '8ef68d0f-aeac-47b8-820a-9da50b71e2c1:fx'
translator = deepl.Translator(***REMOVED***)

# Function to translate text
def translate_text(text, target_language):
    try:
        # Translate text
        result = translator.translate_text(text, target_lang=target_language)
        return result.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    text_to_translate = "Hello, how are you?"
    target_language = "DE"  # German

    translated_text = translate_text(text_to_translate, target_language)
    if translated_text:
        print("Original text:", text_to_translate)
        print("Translated text:", translated_text)
