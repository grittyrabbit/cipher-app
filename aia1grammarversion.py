
import subprocess
import deepl
import random


***REMOVED*** = '8ef68d0f-aeac-47b8-820a-9da50b71e2c1:fx'
translator = deepl.Translator(***REMOVED***)

levels = [
    "A1",
    "A2",
    "B1",
    "B2",
    "C1",
    "C2",
]

level_of_user = str(input("what is your German level?"))
if level_of_user not in levels:
    level_of_user = str(input("please pick a level that is among these: A1, A2, B1, B2, C1, C2"))
reason_of_user = str(input("what is your main reason for learning German?"))

topics = {
    'primary_school': [
        "My favorite subject",
        "The school day",
        "My school friend",
        "The class trip",
        "My teacher",
        "The school library",
        "My school project",
        "The snack in the break",
        "The school uniform",
        "A school day in my life",
        "The classroom",
        "My favorite game during recess",
        "The school rules",
        "The best friends",
        "My favorite book",
        "The hobbies of my friends",
        "A day in physical education class",
        "My favorite toy",
        "The art classes",
        "The school food",
        "My favorite song",
        "The natural sciences",
        "The math classes",
        "The school events",
        "My pet",
        "The music room",
        "The history of the school",
        "My dream job",
        "The best holidays",
        "An excursion to the museum",
        "The theater play",
        "My favorite game at the playground",
        "The school computers",
        "My diary",
        "The school sports day",
        "The gifts for the teachers",
        "The school news",
        "A letter to my friend",
        "The class tests",
        "The school library",
        "My favorite movie",
        "The seasons",
        "The festivals at school",
        "The school concerts",
        "The school newspaper",
        "A day in the life of a teacher",
        "My favorite sport",
        "The excursions",
        "The school assignments",
        "My best friend at school",
        "The environmental projects",
        "The experimenting in the lab",
        "The school subjects",
        "My first school year",
        "The opening ceremony",
        "The school bus",
        "The school friends",
        "The school clothes",
        "My favorite food at school",
        "The class trip to the zoo",
        "The favorite activities during recess",
        "The drawings from the art class",
        "Learning with friends",
        "The importance of friendship",
        "A day in the school garden",
        "The school mobile phone",
        "The sports offered at school",
        "The school time",
        "The holiday activities",
        "My favorite place in school",
        "The weather today",
        "A poem about school",
        "The computer workstations",
        "The first days of school",
        "My favorite game in class",
        "The subjects I like",
        "My dream house",
        "The school graduation party",
        "Creating the school newspaper",
        "Collaboration in the group",
        "Learning in nature",
        "My best moment in school",
        "The after-school care",
        "The school visit",
        "The many languages",
        "The school projects",
        "Dressing up for class",
        "The school assignments in German",
        "The best stories at school",
        "The school anthem",
        "My favorite outing",
        "The school holidays",
        "The best gifts for the teachers",
        "My friend from another class",
        "The school clothes in winter",
        "Drawing at school",
        "The importance of teamwork",
        "The school bus schedule",
        "My favorite game in physical education class",
        "The best memories",
        "The assignments during school time",
        "The next school activities"
    ]
}



def generate_english_text():
    prompt = f"""
Write a text in English with at least 100 words with the level '{level_of_user}' and the topic '{random.choice(topics[reason_of_user])}. Respond with the text and just the text and NOTHING else."""    
    try:
        result = subprocess.run(
            ["ollama", "run", "llama2", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        text = result.stdout.strip()
        
        return text
    except subprocess.CalledProcessError as e:
        print(f"Error generating text: {e}")
        return None

def translate_to_german(text):
    try:
        result = translator.translate_text(text, target_lang="DE")
        return result.text
    except Exception as e:
        return f"An error occurred: {e}"

def parse_text(text):
    words = text.split()
    return words

german_text = translate_to_german(generate_english_text())
global list_from_text
list_from_text = parse_text(german_text)

if list_from_text[0] == "klar!" or list_from_text[0] == "sicher!":
    list_from_text.pop(0)

for i in range(10):
    while '.' not in list_from_text[i] and ':' not in list_from_text[i]:
        i = i + 1
    else:
        list_from_text = list_from_text[i+1:]
        break

def main():
    if german_text:
        print("Generated German Text:")
        print(german_text)
    else:
        print("Failed to generate German text.")

blanks = []
grammar_words = [
    "ich", "du", "er", "sie", "es", "wir", "ihr", "sie", "Sie", "mir", "dir", 
    "mich", "dich", "ihn", "uns", "euch", "ihnen", "meine", "deine", "sein", 
    "ihr", "sein", "unser", "euer", "mein", "dein", "seine", "ihre", "das", 
    "der", "die", "ein", "eine", "einen", "einem", "einer", "des", "dem", 
    "den", "im", "am", "vom", "zum", "zur", "war", "ist", "sind", "bin", 
    "bist", "warst", "waren", "war", "hat", "habe", "hatte", "haben", 
    "sein", "wird", "werden", "wurde", "kann", "können", "konnte", "will", 
    "wollen", "muss", "müssen", "dürfen", "soll", "sollen", "möchte", 
    "hätte", "wäre", "ist", "von", "vom", "bis", "zum", "zu"
]

max_blanks = 10
numberofblank = 1


for i in range(len(list_from_text)):
    if len(blanks) < max_blanks and list_from_text[i] in grammar_words: 
        blanks.append(list_from_text[i])
        list_from_text[i] = f"___{numberofblank}___"
        numberofblank += 1
        i += random.randint(6, 12)


def generate_variations(word):
    similar_words = {
        "ich": ["mein", "mir"],
        "du": ["dein", "dir"],
        "er": ["sie", "es"],
        "sie": ["er", "es"],
        "Sie": ["er", "es"],
        "es": ["das", "es"],
        "wir": ["ihr", "sie"],
        "ihr": ["wir", "sie"],
        "mir": ["mich", "dir"],
        "dir": ["dich", "mir"],
        "mich": ["dich", "mir"],
        "dich": ["mich", "dir"],
        "ihn": ["ihm", "sie"],
        "uns": ["euch", "wir"],
        "euch": ["uns", "sie"],
        "ihnen": ["ihm", "sie"],
        "meine": ["deine", "seine"],
        "deine": ["meine", "seine"],
        "sein": ["ihr", "seine"],
        "ihr": ["sein", "dein"],
        "unser": ["euer", "dein"],
        "euer": ["unser", "mein"],
        "mein": ["dein", "sein"],
        "dein": ["mein", "sein"],
        "seine": ["ihre", "meine"],
        "ihre": ["seine", "deine"],
        "das": ["der", "die"],
        "der": ["die", "das"],
        "die": ["der", "das"],
        "ein": ["eine", "einen"],
        "eine": ["ein", "einen"],
        "einen": ["ein", "eine"],
        "einem": ["einer", "ein"],
        "einer": ["einem", "eine"],
        "des": ["dem", "den"],
        "dem": ["des", "den"],
        "den": ["dem", "des"],
        "im": ["am", "zum"],
        "am": ["im", "vom"],
        "vom": ["zum", "im"],
        "zum": ["bei", "im"],
        "zur": ["bei", "zu"],
        "war": ["ist", "sind"],
        "ist": ["war", "sind"],
        "sind": ["war", "ist"],
        "bin": ["bist", "war"],
        "bist": ["bin", "war"],
        "warst": ["waren", "bin"],
        "waren": ["war", "sind"],
        "hat": ["habe", "hatte"],
        "habe": ["hat", "hatte"],
        "hatte": ["habe", "hat"],
        "haben": ["sein", "habe"],
        "wird": ["werden", "war"],
        "werden": ["wird", "war"],
        "wurde": ["wird", "war"],
        "kann": ["können", "konnte"],
        "können": ["kann", "konnte"],
        "konnte": ["kann", "können"],
        "will": ["wollen", "kann"],
        "wollen": ["will", "konnte"],
        "muss": ["müssen", "soll"],
        "müssen": ["muss", "sollen"],
        "dürfen": ["sollen", "müssen"],
        "soll": ["sollen", "muss"],
        "sollen": ["soll", "müssen"],
        "möchte": ["will", "kann"],
        "hätte": ["wäre", "kann"],
        "wäre": ["hätte", "ist"],
        "von": ["zu", "bei"],
        "bis": ["von", "zu"],
        "zu": ["von", "bei"]
    }
    return similar_words.get(word, [])

options = {}

for word in blanks:
    correct_answer = word
    wrong_options = generate_variations(correct_answer)
    random.shuffle(wrong_options)
    
    wrong_options = wrong_options[:2] if len(wrong_options) >= 2 else wrong_options
    
    options[word] = {
        "correct": correct_answer,
        "options": wrong_options
    }

def quiz_user(options):
    score = 0
    total_questions = len(options)
    text_with_blanks = " ".join(list_from_text)
    print(text_with_blanks)

    for blank, data in options.items():
        correct_answer = data["correct"]
        wrong_options = data["options"]
        all_options = [correct_answer] + wrong_options
        random.shuffle(all_options)
        
        print(f"\nFill in the blank:")
        print("Options:")
        for idx, option in enumerate(all_options, 1):
            print(f"{idx}. {option}")

        while True:
            try:
                user_answer_index = int(input("Choose the correct option (1-3): ")) - 1
                if user_answer_index < 0 or user_answer_index >= len(all_options):
                    raise ValueError("Invalid option.")
                break
            except ValueError as e:
                print(e)
        
        user_answer = all_options[user_answer_index]

        if user_answer == correct_answer:
            print("Correct!")
            score += 1
        else:
            print(f"Wrong! The correct answer is: {correct_answer}")

    print(f"\nYour score: {score}/{total_questions}")

quiz_user(options)
