import aiml
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from glob import glob
from nltk.corpus import wordnet as wn
from nltk import pos_tag, ne_chunk
from nltk.tree import Tree
from nltk.sentiment import SentimentIntensityAnalyzer
import hashlib
import re
import dns.resolver
from speech_recognition import Recognizer, Microphone, UnknownValueError, RequestError, WaitTimeoutError
import pyttsx3
from neo4j import GraphDatabase


def connect_neo4j():
    # Define the Neo4j connection details
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "Staticroad321@"
    # Create a Neo4j driver instance
    driver = GraphDatabase.driver(uri, auth=(username, password))
    return driver


# graph = Graph(URL, auth=(USERNAME, PASSWORD))


mood = ""


def sentiment_analysis(text):
    global mood
    sia = SentimentIntensityAnalyzer()
    results = sia.polarity_scores(text)
    if results['pos'] > results['neg']:
        myBot.setPredicate("sentiment", "positive")
        mood = "positive"
        return
    elif results['neg'] > results['pos']:
        myBot.setPredicate("sentiment", "negative")
        mood = "negative"
        return

    return


def check_sentiment(sentiment):
    pos = pos_tag([sentiment])
    entity = ne_chunk(pos)
    if isinstance(entity[0], Tree):  # Ensure it's a tree (named entity)
        entity_label = entity[0].label()
        if pos[0][1] == "NNP" and (entity_label == 'GPE' or entity_label == 'PERSON'):
            myBot.setPredicate("username", sentiment)
            myBot.setPredicate("sentiment", "")
            return  # Exit the function since the name is recognized

    sentiment_analysis(sentiment)
    return


def set_sentiment():
    global mood
    sentiment = myBot.getPredicate("sentiment")
    if sentiment == "":
        myBot.setPredicate("sentiment", mood)
        return
    return


def get_description(word):
    description = '\n'
    sn = wn.synsets(word)
    length = len(sn)
    for i in range(length):
        # description += str(i+1)
        description += str(i + 1) + ". " + sn[i].definition()
        if i + 1 != length:
            description += '\n'

    return description


def check_meanings(word):
    if word == "":
        myBot.setPredicate("description", "I don't know.")
        return
    else:
        myBot.setPredicate("description", get_description(word))
        word = word.capitalize()
        myBot.setPredicate("word", word)
        return


def prompt_check():
    sentiment = myBot.getPredicate("mood")
    word = myBot.getPredicate("word")
    if word != "":
        check_meanings(word)
    if sentiment != "":
        check_sentiment(sentiment)

    return


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def validate_data(email, password):
    driver = connect_neo4j()
    neo4j_session = driver.session()

    query = """
 MATCH (u:User{email:$email, password:$password})
 RETURN u
 """
    password = hash_password(password)
    user = neo4j_session.run(query, email=email, password=password).data()
    neo4j_session.close()
    driver.close()
    if user:
        return True

    return False


def check_email(email):
    driver = connect_neo4j()
    neo4j_session = driver.session()
    query = """
    MATCH (u:User{email:$email})
    RETURN u
    """
    user = neo4j_session.run(query, email=email).data()
    neo4j_session.close()
    driver.close()
    if user:
        print(user)
        return True
    return False


def is_valid_domain(email):
    domain = email.split("@")[1]
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return False


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_email(email):
    if is_valid_email(email) and is_valid_email(email):
        return True
    return False


def get_username(email):
    driver = connect_neo4j()
    neo4j_session = driver.session()
    query = """
    MATCH (u:User{email: $email}) RETURN u.name
    """
    username = neo4j_session.run(query, email=email).data()[0]['u.name']
    neo4j_session.close()
    driver.close()
    return username


def store_credentials(name, email, password):
    password = hash_password(password)
    driver = connect_neo4j()
    neo4j_session = driver.session()

    query = """
    MERGE (u:User{name:$name, email:$email, password:$password})
    """
    neo4j_session.run(query, name=name, email=email, password=password)
    neo4j_session.close()
    driver.close()
    return


def store_query(prompt, response):
    driver = connect_neo4j()
    neo4j_session = driver.session()
    query = """
    MERGE (q:Query{prompt:$prompt, response:$response})
    """
    neo4j_session.run(query, prompt=prompt, response=response)
    neo4j_session.close()
    driver.close()
    return


recognizer = Recognizer()


def recognize_speech():
    with Microphone() as source:
        print("Listening for speech...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=5)  # Listen with a 5-second timeout

        try:
            text = recognizer.recognize_google(audio)
            print(f"Recognized text: {text}")
            return text
        except WaitTimeoutError:
            print("Listening timed out while waiting for speech.")
            return "timeout"  # Special return to indicate timeout
        except UnknownValueError:
            return None
        except RequestError:
            return None


engine = pyttsx3.init()

myBot = aiml.Kernel()
app = Flask(__name__)
app.secret_key = 'your-secret-key'
aiml_files = glob("aiml files/*.aiml")

for file in aiml_files:
    myBot.learn(file)


# myBot.learn('aiml files/conversation.aiml')
# myBot.learn('aiml files/jokes.aiml')


@app.route("/")
def home():
    if 'username' in session:
        return render_template("home.html", username=session['username'])
    else:
        return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        if validate_data(email, password):
            username = get_username(email)
            return redirect(url_for('home') + '?success=login')
        else:
            return redirect(url_for('login') + '?error=invalid')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Check if the passwords match
        if password != confirm_password:
            return redirect(url_for('signup') + '?error=password_mismatch')

        if check_email(email):
            print(check_email(email))
            return redirect(url_for('signup') + '?error=email_exists')
        if not validate_email(email):
            return redirect(url_for('signup') + '?error=invalid_email')
        store_credentials(name, email, password)
        return redirect(url_for('login') + '?success=signup')

    return render_template('signup.html')


@app.route('/transcribe', methods=['GET'])
def transcribe_speech():
    try:
        query = recognize_speech()

        if query == "timeout":
            # Return message indicating a timeout
            return jsonify({"error": "Listening timed out. Please try again."}), 408  # 408 Request Timeout status
        elif not query:
            # Indicate that speech was not understood
            return jsonify({"error": "Could not understand speech"}), 400

        # Return recognized speech as JSON
        return jsonify({"query": query}), 200

    except Exception as e:
        # Catch any unexpected errors and log for debugging
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


# @app.route('/speak', methods=['POST'])
# def speak():
#     data = request.json
#     text = data.get('text', '')
#     voices = engine.getProperty('voices')
#     engine.setProperty('voice', voices[1].id)
#     if text:
#         engine.say(text)
#         engine.runAndWait()
#         return jsonify({"status": "success", "message": "Speech completed"}), 200
#     return jsonify({"status": "error", "message": "No text provided"}), 400


@app.route("/get")
def get_bot_response():
    query = request.args.get('msg')
    myBot.respond(query)
    prompt_check()
    response = myBot.respond(query)
    set_sentiment()
    store_query(query, response)
    return response


# @app.route("/get")
# def get_bot_response():
#     query = request.args.get('msg')
#
#     if not query:  # If 'msg' is empty, try speech recognition
#         query = recognize_speech()
#         if not query:  # Handle case where speech recognition fails
#             return jsonify({"error": "I couldn't understand the speech input."}), 400  # Return with a 400 Bad Request
#
#     # Ensure 'query' is a string before sending to bot
#     query = str(query)
#     response = myBot.respond(query)
#
#     # Check if the bot's response is empty or None
#     if not response:
#         response = "I'm sorry, I couldn't find an answer for that."
#
#     # Log the response and store it
#     prompt_check()  # Assuming this function is used to modify the prompt in some way
#     set_sentiment()
#     store_query(query, response)
#
#     return jsonify({"response": response})  # Return as JSON object for consistency


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5001')

# #import speech_recognition as sr
#
# from speech_recognition import Microphone, Recognizer, UnknownValueError, RequestError
# recognizer = Recognizer()
#
# with Microphone() as mic:
#     print("Say something!")
#     audio = recognizer.listen(mic)
#
# try:
#     text = recognizer.recognize_google(audio)
#     print("You said: " + text)
#
# except UnknownValueError:
#     print("Could not understand audio")
# except RequestError as e:
#     print(f"Could not request results from Google Speech Recognition service; {e}")
