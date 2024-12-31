from flask import Flask, render_template, request, jsonify
import spacy
import random
from PyMultiDictionary import MultiDictionary
from translatetogerman import translate_to_german
from lists import common_nouns
import re

app = Flask(__name__)
 = 'randomsecretkeyforlara'

# Load spaCy German model
nlp = spacy.load("de_core_news_sm")

# Function to parse the generated text into words
def parse_text(text):
    return text.split()

def get_def(word: str):
    # Initialize the dictionary
    dictionary = MultiDictionary()

    # Fetch the meaning for the word
    meaning = dictionary.meaning('de', word)

    if meaning:
        # Assuming the definition is in the second part of the result (index 1)
        definition_text = meaning[1]
        definition_after_cutoff = definition_text

        # Find the first period, semicolon, '©' symbol, and "Short form for:" and determine where to cut off
        first_period_pos = definition_after_cutoff.find('.')
        semicolon_pos = definition_after_cutoff.find(';')
        copyright_pos = definition_after_cutoff.find('©')
        short_form_pos = definition_after_cutoff.find("Short form for:")

        # Regular expression to match the pattern where a lowercase letter is followed by a capital letter
        capital_after_lowercase = re.search(r'[a-z]+ [A-Z]', definition_after_cutoff)

        # Determine the position where to cut off
        cutoff_pos = len(definition_after_cutoff)  # Default to the end of the string
        
        # If a period, semicolon, or "Short form for:" exists, cut at the first occurrence
        if first_period_pos != -1:
            cutoff_pos = min(cutoff_pos, first_period_pos + 1)
        if semicolon_pos != -1:
            cutoff_pos = min(cutoff_pos, semicolon_pos)
        if short_form_pos != -1:
            cutoff_pos = min(cutoff_pos, short_form_pos)
        
        # If a lowercase letter is followed by a capital letter, cut at that point
        if capital_after_lowercase:
            cutoff_pos = min(cutoff_pos, capital_after_lowercase.start())

        # Cut off at '©' if it appears before the first period or semicolon or "Short form for:"
        if copyright_pos != -1 and copyright_pos < cutoff_pos:
            cutoff_pos = copyright_pos

        # Slice the definition up to the cutoff position
        definition_until_cutoff = definition_after_cutoff[:cutoff_pos]

        return translate_to_german(definition_until_cutoff.strip())
    else:
        return None

def extract_nouns(text):
    doc = nlp(text)
    return [token.text for token in doc if token.pos_ == 'NOUN']

def create_question(noun):
    correct_definition = get_def(noun)
    if not correct_definition:
        return None  # Skip if no definition was found
    
    if len(correct_definition.split()) < 5:
        return None  # Skip if the definition is less than 5 words long

    filtered_nouns = [word for word in common_nouns if word != noun]
    
    # Pick two random nouns for distractors
    distractors = random.sample(filtered_nouns, 2)
    
    # Filter distractors to ensure they have valid definitions
    distractor_definitions = [get_def(d) for d in distractors]
    distractor_definitions = [d for d in distractor_definitions if d]  # Remove None values

    # If we don't have at least two distractors with definitions, skip this question
    if len(distractor_definitions) < 2:
        return None
    
    # Shuffle the options to randomize the order
    options = [correct_definition] + distractor_definitions
    random.shuffle(options)

    return {
        'question': f"Was ist die Definition von '{noun}'?",
        'options': options,
        'answer': correct_definition
    }

def generate_questions_from_text(text):
    nouns = extract_nouns(text)
    questions = []

    for noun in nouns:
        question = create_question(noun)
        if question:
            questions.append(question)

        if len(questions) >= 10:
            break
    
    return questions

# Sample English text to translate and generate questions from
engtext = "Hallo! Ich heiße Anna und ich möchte dir von meinem Tag erzählen. Jeden Morgen wache ich um 7 Uhr auf. Ich stehe auf, wasche mein Gesicht und ziehe mich an. Dann frühstücke ich. Zum Frühstück esse ich gerne Brot mit Marmelade und trinke Tee. Um 8 Uhr gehe ich zur Arbeit. Ich arbeite in einem Büro und meine Kolleginnen sind sehr nett. Die Arbeit macht mir Spaß. Um 12 Uhr habe ich Mittagspause. Ich esse meistens einen Salat oder ein Sandwich."

@app.route('/vocab', methods=['GET', 'POST'])
def vocab():
    text = translate_to_german(engtext)
    questions = generate_questions_from_text(text)
    
    if request.method == 'POST':
        answers = request.form  # Retrieve the form data (selected answers)
        score = 0

        # Calculate the score
        for question in questions:
            correct_answer = question['answer']
            # Check the selected answer for the question
            selected_answer = answers.get(f'answer_{questions.index(question)}')
            if selected_answer == correct_answer:
                score += 1

        return render_template('vocab.html', questions=questions, score=score, show_score=True, text=text)

    return render_template('vocab.html', questions=questions, show_score=False)

if __name__ == '__main__':
    app.run(debug=True)
