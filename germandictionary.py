from PyMultiDictionary import MultiDictionary
from translatetogerman import translate_to_german





def get_def(word: str):
    dictionary = MultiDictionary()

    meaning = dictionary.meaning('de', word)

    if meaning:
        definition_text = meaning[1]

        definition_after_cutoff = definition_text[0:]

        first_period_pos = definition_after_cutoff.find('.')
        copyright_pos = definition_after_cutoff.find('©')

        if first_period_pos != -1:
            cutoff_pos = first_period_pos + 1
        else:
            cutoff_pos = len(definition_after_cutoff)

        if copyright_pos != -1 and copyright_pos < cutoff_pos:
            cutoff_pos = copyright_pos

        definition_until_cutoff = definition_after_cutoff[:cutoff_pos]

        return translate_to_german(f"{definition_until_cutoff.strip()}")
    else:
        print(f"No meaning found for '{word}'.")

def get_def_bad(word: str):
    dictionary = MultiDictionary()

    meaning = dictionary.meaning('de', word)

    print(meaning)

get_def_bad("katze")