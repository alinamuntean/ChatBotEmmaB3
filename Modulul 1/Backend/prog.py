from flask import Flask
from flask_cors import CORS, cross_origin
import MySQLdb, aiml,os
from memory_check import Memory
import threading
from mood import Mood
from personBD import *
from personality import *
from randomAnswer import RandomAnswer
import random
import isEnglishOrJibberish
from time import *
from split_sentences import *
import timeit #linia 1

app = Flask(__name__)

db = MySQLdb.connect(host="ppdatabase.ccvycmsqlp8u.eu-central-1.rds.amazonaws.com",    # your host, usually localhost
                     user="mariusdonici",         # your username
                     passwd="carrymeteodorescu",  # your password
                     db="ia")        # name of the data base

cur = db.cursor()

# Use all the SQL you like

# for row in cur.fetchall():
#     print row[0]
cur.execute("SELECT * FROM Users")

table= cur.fetchall()
cur.execute("SELECT * FROM questions")
questions = cur.fetchall()

db.close()

rnd = RandomAnswer()
sessionId=12345
# Create the kernel and learn AIML files
kernel = aiml.Kernel()
kernel.learn("std-startup.xml")
kernel.respond("load aiml b")

initialize_bot(kernel,sessionId)

botMood = Mood()

attr=getPeopleAttributes()
iKnowOp=2

start = 0
# Press CTRL-C to break this loop
@app.route('/<question>')
def main(question):
    stop = timeit.default_timer()
    global attr
    global iKnowOp
    global start
    print botMood.get_current_mood(question)
    #users=table
    bootMemory= Memory()
    res=kernel.respond(question,sessionId)
    responses_incase_nonenglish = open('jibberish_responses.json', 'r').read()
    jibberish_array = json.loads(responses_incase_nonenglish)
    if not (isEnglishOrJibberish.is_english_sentence(question)):
        return random.choice(jibberish_array)
    res=synonymCheck("resources/synonyms.json",question)
    if bootMemory.checkQuestionRepetition(question)==1:
        bootMemory.addQuestion(question)
        response=bootMemory.getRandomForRepetition()
        bootMemory.addResponse(response)
        return response
    bootMemory.addQuestion(question)

    if len(attr)>1:
        attr=verifyExistence(kernel,sessionId,attr)
    if len(attr)==1:
        iKnowOp=1
    if len(attr)==0:
        iKnowOp=0
        decideToMemorate(kernel,sessionId)
    if res=='':
        res = rnd.answer(questions)
    time = stop - start
    if time > 20:
        time_obj = Time_answer()
        res = time_obj.time_answer(time)

    bootMemory.addResponse(res)
    print stop - start
    start = timeit.default_timer()
    return res


def deleteContent(fName):
    with open(fName, "w"):
        pass


def synonymCheck(filePath, question):
    res=kernel.respond(question,sessionId)
    if res is not None:
        return res
    with open(filePath) as data_file:
        data = json.load(data_file)
    for i in data:
        aux = question
        for j in data[i]:
            aux = aux.replace(i, data[i][j])
            res=kernel.respond(aux,sessionId)
            if res is not None:
                return res
            aux = question
    return "No answer found"


if __name__ == '__main__':
    CORS(app)
    deleteContent('question.txt')
    app.run();