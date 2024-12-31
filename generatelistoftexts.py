from main import level_of_user, reason_of_user
from flask import Flask, render_template, request, redirect, url_for, make_response, session
import random
import deepl
app = Flask(__name__)
 = 'randomsecretkeyforlara'
import subprocess
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0
from lists import grammar_words
from lists import variations
from lists import topics
import spacy
from translatetogerman import translate_to_german
import json
from datetime import datetime, timedelta



def generate_english_text():
    if reason_of_user in topics:
        prompt = f"""
    Write a text in English with 100-150 words with the level '{level_of_user}' and the topic '{random.choice(topics[reason_of_user])}. Respond with the text and just the text and NOTHING else."""    
    else:
        prompt = f"""
    Write a realistic story or a text in English in first or third person with 100-150 words with the level '{level_of_user}' and the topic '{reason_of_user}'. Respond with the text and just the text and NOTHING else."""    
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2:1b", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        text = result.stdout.strip()
        return text
    except subprocess.CalledProcessError as e:
        print(f"Error generating text: {e}")
        return None


def generate_multiple_texts(n=5):
    texts = []
    for _ in range(n):
        text = generate_english_text()
        if text:
            texts.append(text)
    return texts


@app.route('/store_texts', methods=['GET'])
def store_texts():
    generated_texts = generate_multiple_texts()

    # Serialize the list of texts into a JSON string
    texts_json = json.dumps(generated_texts)

    # Store the texts as a cookie with expiration of 1 day
    resp = make_response(redirect(url_for('show_texts')))
    expires = datetime.now() + timedelta(days=1)  # 1-day expiration
    resp.set_cookie('generated_texts', texts_json, expires=expires)

    return resp


@app.route('/show_texts', methods=['GET'])
def show_texts():
    # Retrieve the texts from the cookie
    texts_json = request.cookies.get('generated_texts')

    if texts_json:
        texts = json.loads(texts_json)  # Deserialize the JSON string into a Python list
    else:
        texts = []

    return render_template('show_texts.html', texts=texts)


if __name__ == '__main__':
    app.run(debug=True)