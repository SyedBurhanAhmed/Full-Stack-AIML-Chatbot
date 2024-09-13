import aiml
from flask import Flask, render_template, request, redirect,url_for,session
from glob import glob
from nltk.corpus import wordnet as wn
from nltk import pos_tag, ne_chunk
from nltk.tree import Tree
from nltk.sentiment import SentimentIntensityAnalyzer
from py2neo import Graph
import hashlib
import re
import dns.resolver

URL = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Staticroad321@"

graph = Graph(URL, auth=(USERNAME, PASSWORD))

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
        description += str(i+1) + ". " + sn[i].definition()
        if i+1 != length:
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
    query = """
 MATCH (u:User{email:$email, password:$password})
 RETURN u
 """
    password = hash_password(password)
    user = graph.run(query, email=email, password=password).data()
    if user:
        return True

    return False


def check_email(email):
    query = """
    MATCH (u:User{email:$email})
    RETURN u
    """
    user = graph.run(query, email=email).data()
    if user:
        print(user)
        return True
    return False


def is_valid_domain(email):
    domain = email.split("@")[1]
    try:
        dns.resolver.resolve(domain,'MX')
        return True
    except (dns.resolver.NXDOMAIN,dns.resolver.NoAnswer):
        return False


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
        

def validate_email(email):
    if is_valid_email(email) and is_valid_email(email):
        return True
    return False


def get_username(email):
    query = """
    MATCH (u:User{email: $email}) RETURN u.name
    """
    username = graph.run(query,email=email).data()[0]['u.name']
    return username


def store_credentials(name, email, password):
    password = hash_password(password)
    query = """
    MERGE (u:User{name:$name, email:$email, password:$password})
    """
    graph.run(query, name=name, email=email, password=password)
    return


def store_query(prompt,response):
    query = """
    MERGE (q:Query{prompt:$prompt, response:$response})
    """
    graph.run(query,prompt=prompt,response=response)
    return


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
        return render_template("home.html",username=session['username'])
    else:
        return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        
        if validate_data(email,password):
            username = get_username(email)
            return redirect(url_for('home') + '?success=login')
        else:
            return redirect(url_for('login') + '?error=invalid')

    return render_template('login.html')


@app.route('/signup',methods=['GET','POST'])
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


@app.route("/get")
def get_bot_response():

    query = request.args.get('msg')
    myBot.respond(query)
    prompt_check()
    response = myBot.respond(query)
    set_sentiment()
    store_query(query,response)
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port = '5001')


# myBot.learn('aiml files/conversation.aiml')
# while True:
#     query = input("Yes: ")
#     myBot.respond(query)
#     prompt_check()
#     response = myBot.respond(query)
#     set_sentiment()
#     print("Bot:", myBot.respond(query))



'''
# @app.route("/")
# def another_home():
#     return "This is another home page"

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/get")
def get_bot_response():

    query = request.args.get('msg')  # {"msg":"hello there"}

    response = myBot.respond(query)

    return response


if __name__ == "__main__":
    # app.run()
    app.run(host='0.0.0.0', port='5000')




while True:
    prompt = input("Human: ")
    response = myBot.respond(prompt)
    if response == "":
        break
    else:
        print("Bot: ",response)
'''
