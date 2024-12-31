from flask import Flask, render_template, request, redirect, url_for, session
import random
import spacy
import re
from datetime import datetime, timedelta
from PyMultiDictionary import MultiDictionary
from translatetogerman import translate_to_german
from lists import common_nouns
from main import generate_english_text


# Register the filter with Flask's Jinja environment

# Load spaCy German model
nlp = spacy.load("de_core_news_sm")

app = Flask(__name__)
 = 'randomsecretkey'
import random
import spacy
from PyMultiDictionary import MultiDictionary
from translatetogerman import translate_to_german
from lists import common_nouns
from main import generate_english_text

# Load spaCy German model
nlp = spacy.load("de_core_news_sm")

def get_def(word: str):
    """
    Fetches the definition for a given word, returns None if there is an error or invalid response.
    """
    dictionary = MultiDictionary()
    meaning = dictionary.meaning('de', word)

    if meaning:
        definition_text = meaning[1]

        # If the definition text is empty, skip this noun
        if not definition_text or definition_text.strip() == "":
            return None
        
        # Find cutoff positions to trim the definition
        first_period_pos = definition_text.find('.')
        semicolon_pos = definition_text.find(';')
        cutoff_pos = len(definition_text)
        
        if first_period_pos != -1:
            cutoff_pos = min(cutoff_pos, first_period_pos + 1)
        if semicolon_pos != -1:
            cutoff_pos = min(cutoff_pos, semicolon_pos)

        # Cut at the cutoff position
        definition_until_cutoff = definition_text[:cutoff_pos]
        return translate_to_german(definition_until_cutoff.strip())
    else:
        return None

def extract_nouns(text):
    """
    Extracts nouns from the given text using spaCy.
    """
    doc = nlp(text)
    return [token.text for token in doc if token.pos_ == 'NOUN']

def create_question(noun, question_id):
    """
    Creates a multiple-choice question for a given noun.
    """
    # Get the definition for the singular form of the noun
    singular_noun = nlp(noun)[0].lemma_  # Convert to singular form if plural
    correct_definition = get_def(singular_noun)
    
    if not correct_definition or len(correct_definition.split()) < 5:
        return None

    # Generate distractors (other nouns) for the question
    filtered_nouns = [word for word in common_nouns if word != noun]
    distractors = random.sample(filtered_nouns, 2)

    distractor_definitions = [get_def(d) for d in distractors]
    distractor_definitions = [d for d in distractor_definitions if d]

    if len(distractor_definitions) < 2:
        return None

    options = [correct_definition] + distractor_definitions
    random.shuffle(options)

    return {
        'id': question_id,  # Assign unique id to each question
        'noun': noun,
        'question': f"Was ist die Definition von '{noun}'?",
        'options': options,
        'answer': correct_definition
    }

def generate_questions_from_text(text):
    """
    Generates a list of questions from a text.
    """
    nouns = extract_nouns(text)
    questions = []

    for idx, noun in enumerate(nouns):  # Use idx as a unique question id
        question = create_question(noun, idx)
        if question:
            questions.append(question)

        if len(questions) >= 10:  # Limit to 10 questions
            break
    
    return questions

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """
    Displays and handles the quiz page.
    """
    if 'questions' not in session:
        # Sample text to generate questions from
        engtext = translate_to_german(generate_english_text())

        # Generate questions based on the text
        questions = generate_questions_from_text(engtext)
        
        # Store the questions and the correct answers in the session
        session['questions'] = questions
        session['engtext'] = engtext
        session['correct_answers'] = {question['id']: question['answer'] for question in questions}

        # Preprocess the text to make vocabulary words bold
        for question in questions:
            word = question['noun']
            engtext = engtext.replace(word, f'<strong>{word}</strong>')

        # Store the processed text with bold vocabulary words in session
        session['engtext'] = engtext

    else:
        questions = session['questions']
        engtext = session['engtext']

    if request.method == 'POST':
        # When the user submits the form, get their answers
        user_answers = request.form.to_dict()
        score = 0
        mistakes = []

        # Check the user's answers against the correct answers
        for question in questions:
            user_answer = user_answers.get(f'answer_{question["id"]}')
            if user_answer == question['answer']:
                score += 1
            else:
                mistakes.append({'question': question, 'user_answer': user_answer})

        # Store score and mistakes in the session
        session['score'] = score
        session['mistakes'] = mistakes

        return redirect(url_for('score'))

    # If the page is being loaded (GET request), display the quiz
    return render_template('quiz.html', questions=questions, engtext=engtext)

@app.route('/score', methods=['GET'])
def score():
    """
    Displays the score page.
    """
    score = session.get('score', 0)
    total = len(session.get('questions', []))
    mistakes = session.get('mistakes', [])
    return render_template('score.html', score=score, total=total, mistakes=mistakes)

@app.route('/reset_quiz')
def reset_quiz():
    """
    Resets the quiz session data.
    """
    # Clear quiz-related session data
    session.pop('questions', None)
    session.pop('correct_answers', None)
    session.pop('engtext', None)
    session.pop('score', None)
    session.pop('mistakes', None)

    # Redirect back to the quiz page to generate a new quiz
    return redirect(url_for('quiz'))

@app.route('/mistakesvoci', methods=['GET'])
def mistakes():
    """
    Displays a page showing the mistakes made during the quiz.
    """
    mistakes = session.get('mistakes', [])
    return render_template('mistakes_voci.html', mistakes=mistakes)

if __name__ == '__main__':
    app.run(debug=True)
