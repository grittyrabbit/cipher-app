from flask import Flask, render_template, request, redirect, url_for, make_response, session
import random
import deepl
import subprocess
from langdetect import detect, DetectorFactory
import spacy
from datetime import datetime, timedelta
from PyMultiDictionary import MultiDictionary
from translatetogerman import translate_to_german
from lists import grammar_words, variations, topics, common_nouns

# Set up Flask app
app = Flask(__name__)
 = 'randomsecretkey'


# Load spacy model for German
nlp = spacy.load("de_core_news_sm")

# Fix random seed for consistency
DetectorFactory.seed = 0

# Global variables
level_of_user = None
reason_of_user = None

@app.route('/about')
def about():
    return render_template('about.html')  # About page

# Helper functions
def generate_english_text():
    if reason_of_user in topics:
        prompt = f"Write a text in English with 100-150 words with the level '{level_of_user}' and the topic '{random.choice(topics[reason_of_user])}'. Respond with the text and NOTHING else."
    else:
        prompt = f"Write a realistic story or a text in English in first or third person with 100-150 words with the level '{level_of_user}' and the topic '{reason_of_user}'. Respond with the text and NOTHING else."
    
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2:1b", prompt],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error generating text: {e}")
        return None

def create_quiz():
    german_text = translate_to_german(generate_english_text())
    words = german_text.split()
    blanks, correct_answers = [], {}
    max_blanks, number_of_blank, i = 10, 1, 0

    while i < len(words) and len(blanks) < max_blanks:
        if words[i].lower() in grammar_words:
            blank_word = f"___{number_of_blank}___"  # Correctly using number_of_blank
            blanks.append(blank_word)
            correct_answers[blank_word] = words[i]  # Track the correct answer for the blank
            words[i] = blank_word  # Replace word with blank placeholder
            number_of_blank += 1
            skip_count = random.randint(1, 10)
            i += skip_count
        else:
            i += 1

    options = {}
    for blank in blanks:
        correct_answer = correct_answers[blank]
        wrong_options = variations.get(correct_answer.lower(), ["war", "ist"])
        random.shuffle(wrong_options)
        options[blank] = {
            "correct": correct_answer,
            "options": wrong_options[:2] + [correct_answer]
        }
        random.shuffle(options[blank]["options"])

    return ' '.join(words), blanks, options, correct_answers

def evaluate_quiz(user_answers, correct_answers):
    score = 0
    for blank, user_answer in user_answers.items():
        correct_answer = correct_answers.get(blank)
        # Case insensitive comparison
        if user_answer.lower() == correct_answer.lower():
            score += 1
    return score, len(user_answers)

def get_def(word: str):
    dictionary = MultiDictionary()
    meaning = dictionary.meaning('de', word)
    if meaning:
        definition_text = meaning[1]
        if not definition_text.strip():
            return None
        cutoff_pos = min(definition_text.find('.'), definition_text.find(';')) or len(definition_text)
        return translate_to_german(definition_text[:cutoff_pos].strip())
    return None

def extract_nouns(text):
    doc = nlp(text)
    return [token.text for token in doc if token.pos_ == 'NOUN']

def create_question(noun, question_id):
    singular_noun = nlp(noun)[0].lemma_
    correct_definition = get_def(singular_noun)
    if not correct_definition or len(correct_definition.split()) < 5:
        return None
    distractors = random.sample([word for word in common_nouns if word != noun], 2)
    distractor_definitions = [get_def(d) for d in distractors if get_def(d)]
    if len(distractor_definitions) < 2:
        return None
    options = random.sample([correct_definition] + distractor_definitions, 3)
    return {
        'id': question_id, 'noun': noun,
        'question': f"Was ist die Definition von '{noun}'?", 'options': options, 'answer': correct_definition
    }

def generate_questions_from_text(text):
    nouns = extract_nouns(text)
    questions = [create_question(noun, idx) for idx, noun in enumerate(nouns) if create_question(noun, idx)]
    return questions[:10]

# Routes
@app.route('/landing1')
def landing1():
    return render_template('landing1.html')

@app.route('/landing2', methods=['GET', 'POST'])
def landing2():
    if request.method == 'POST':
        level_of_user = request.form['level']
        resp = make_response(redirect(url_for('landing3')))
        resp.set_cookie('level', level_of_user)
        return resp
    return render_template('landing2.html')

@app.route('/landing3', methods=['GET', 'POST'])
def landing3():
    level_of_user = request.cookies.get('level')
    if request.method == 'POST':
        reason_of_user = request.form['reason']
        resp = make_response(redirect(url_for('home')))
        resp.set_cookie('reason', reason_of_user)
        return resp
    return render_template('landing3.html', level=level_of_user)

@app.route('/otherReason', methods=['GET', 'POST'])
def otherReason():
    level_of_user = request.cookies.get('level')
    if request.method == 'POST':
        custom_reason = request.form['reason']
        resp = make_response(redirect(url_for('home')))
        resp.set_cookie('reason', custom_reason)
        return resp
    return render_template('otherReason.html', level=level_of_user)

@app.route("/", methods=["GET"])
def home():
    global level_of_user, reason_of_user
    level_of_user = request.cookies.get('level')
    reason_of_user = request.cookies.get('reason')
    if level_of_user is None or reason_of_user is None:
        return redirect(url_for('landing1'))
    return render_template('index.html', level_of_user=level_of_user, reason_of_user=reason_of_user)

@app.route('/grammar', methods=['GET', 'POST'])
def grammarquiz():
    if request.method == 'POST':
        # Get user answers from the form
        user_answers = request.form.to_dict()
        
        # Retrieve correct answers from session
        correct_answers = session.get('correct_answers', {})
        
        # Calculate the score based on the user's answers
        score, total_questions = evaluate_quiz(user_answers, correct_answers)
        session['score'] = score
        
        # Collect mistakes: include blank number, user answer, and correct answer
        mistakes = []
        for blank, user_answer in user_answers.items():
            # Get the correct answer for the blank
            correct_answer = correct_answers.get(blank)
            
            # Check if the user answer is incorrect
            if user_answer.lower() != correct_answer.lower():
                # Extract the blank number (e.g., ___6___ -> 6)
                blank_number = int(blank.strip('___'))  # Strip out '___' to get the number
                mistakes.append({
                    'blank_number': blank_number,
                    'blank': blank,
                    'user_answer': user_answer,
                    'correct_answer': correct_answer
                })
        
        # Store mistakes in the session
        session['mistakes'] = mistakes
        
        # Redirect to the score page
        return redirect(url_for('score'))

    # Generate the German quiz text and related data
    german_text, blanks, options, correct_answers = create_quiz()
    
    # Store the quiz data in the session
    session['correct_answers'] = correct_answers
    session['german_text'] = german_text
    session['blanks'] = blanks
    
    # Handle the case if the German text wasn't generated properly
    if not german_text:
        return "Error generating quiz."
    
    # Render the grammar quiz page, passing the necessary data to the template
    return render_template('grammar.html', text=" ".join(german_text.split()), blanks=blanks, options=options)

@app.route('/score', methods=['GET'])
def score():
    score = session.get('score', 0)
    total = len(session.get('blanks', []))
    mistakes = session.get('mistakes', [])
    german_text = session.get('german_text', '')  # Retrieve the German text from session
    message = "No mistakes! Well done!" if not mistakes else None
    return render_template('score.html', score=score, total=total, mistakes=mistakes, message=message, german_text=german_text)

@app.route("/submit", methods=["POST"])
def submit_quiz():
    user_answers = request.form.to_dict()
    correct_answers = session.get('correct_answers', {})
    score, total_questions = evaluate_quiz(user_answers, correct_answers)
    session['score'] = score
    return render_template('quiz_result.html', score=score, total=total_questions)

@app.route("/mistakes", methods=["GET"])
def getmistakes():
    user_answers = session.get('user_answers', {})
    correct_answers = session.get('correct_answers', {})
    german_text = session.get('german_text', '')
    if not user_answers or not correct_answers or not german_text:
        return redirect(url_for('grammarquiz'))
    mistakes = [{'blank': blank, 'user_answer': user_answer, 'correct_answer': correct_answers.get(blank)} for blank, user_answer in user_answers.items() if user_answer.lower() != correct_answers.get(blank).lower()]
    if not mistakes:
        return "No mistakes! Well done!"
    return render_template('mistakes.html', mistakes=mistakes, german_text=german_text)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'questions' not in session:
        engtext = translate_to_german(generate_english_text())
        questions = generate_questions_from_text(engtext)
        session['questions'] = questions
        session['engtext'] = engtext
        session['correct_answers'] = {question['id']: question['answer'] for question in questions}
        for question in questions:
            word = question['noun']
            engtext = engtext.replace(word, f'<strong>{word}</strong>')
        session['engtext'] = engtext
    else:
        questions = session['questions']
        engtext = session['engtext']

    if request.method == 'POST':
        user_answers = request.form.to_dict()
        score = sum(1 for question in questions if user_answers.get(f'answer_{question["id"]}') == question['answer'])
        session['score'] = score
        session['mistakes'] = [{'question': question, 'user_answer': user_answers.get(f'answer_{question["id"]}') } for question in questions if user_answers.get(f'answer_{question["id"]}') != question['answer']]
        return redirect(url_for('score'))

    return render_template('quiz.html', questions=questions, engtext=engtext)

@app.route('/reset_quiz')
def reset_quiz():
    session.clear()
    return redirect(url_for('quiz'))

@app.route('/mistakesvoci', methods=['GET'])
def vocimistakes():
    mistakes = session.get('mistakes', [])
    return render_template('mistakes_voci.html', mistakes=mistakes)

if __name__ == '__main__':
    app.run(debug=True)
