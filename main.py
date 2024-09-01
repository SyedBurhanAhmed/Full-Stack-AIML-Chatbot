import aiml
from flask import Flask, render_template, request
from glob import glob
from nltk.corpus import wordnet as wn
from nltk import pos_tag, ne_chunk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tree import Tree


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
        description += str(i+1) + "." + sn[i].definition()
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


myBot = aiml.Kernel()
app = Flask(__name__)
aiml_files = glob("aiml files/*.aiml")


for file in aiml_files:
    myBot.learn(file)
# myBot.learn('aiml files/conversation.aiml')
# myBot.learn('aiml files/jokes.aiml')


@app.route("/")
def home():
    return render_template("home.html")


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route("/get")
def get_bot_response():

    query = request.args.get('msg')
    myBot.respond(query)
    prompt_check()
    response = myBot.respond(query)
    set_sentiment()
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port = '5000')


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
