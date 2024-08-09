import aiml
from flask import Flask, render_template, request
from glob import glob


myBot = aiml.Kernel()
app = Flask(__name__)
aiml_files = glob("aiml files/*.aiml")


for file in aiml_files:
    myBot.learn(file)


@app.route("/")
def home():
    return render_template("home.html")
'''

@app.route("/")
def another_home():
    return "This is another home page"
'''

@app.route("/get")
def get_bot_response():

    query = request.args.get('msg')

    response = myBot.respond(query)

    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000')

'''
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
