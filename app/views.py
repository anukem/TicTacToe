from app import app
from flask import request
import sqlite3
from flask import jsonify


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        # Check if game is in session
        data = request.get_data()
        data = dict(x.split("=") for x in data.split("&"))
        player1 = data["user_name"]
        player2 = ""
        move = 0

        # Interpret the syntax

        if(data["text"] == ""):
            # Intro text
            response = {"response_type": "ephemeral"}
            response["text"] = "Welcome to TicTacToe!\nIn order to start a game, please challenge someone in the channel.\nEx. /ttt @john"
            return jsonify(response)

        elif(len(data["text"].split(" ")) == 1):
            # Select the challenger
            if(data["text"][0:3] == "%40"):
                player2 = data["text"][3:len(data["text"])]
            elif(len(data["text"]) == 1):
                if(data["text"].isdigit()):
                    move = int(data["text"])

        # Establish connection to database
        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()

        # Try to create the table
        t = (data["channel_name"],)

        try:
            table = cursor.execute("select * from game where channel=?", t)

        except:
            cursor.execute("create table game (channel varchar(256)," +
                           " inSession integer(4), player1 varchar(256), player2"
                           + " varchar(256), topLeft integer(4), " +
                           "topMiddle integer(4), topRight integer(4), " +
                           "middleLeft integer(4)," + " center integer(4), " +
                           " middleRight integer(4), bottomLeft integer(4)," +
                           " bottomMiddle integer(4), bottomRight integer(4));")

        # Get current game
        currentGame = cursor.execute("select * from game where channel=?", t)

        if(len(currentGame.fetchall()) == 0 and player2 != ""):
            # No game has been made
            print("making a game")
            currentGame = cursor.execute("INSERT INTO game VALUES(?, ?, ?, ?" +
                                         ", ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                         [data["channel_name"],
                                          1, player1, player2, 0, 0, 0, 0,
                                          0, 0, 0, 0, 0])
            connection.commit()
            # Create New Game
            responseMessage = {"response_type": "in_channel", "text": "You've challenged " + player2 + "!" +
                               "The board is currently:\n|1|2|3|\n" +
                               "|4|5|6|\n" +
                               "|7|8|9|\n"}
            return jsonify(responseMessage)
        else:
            # Check to see if the player is making correct move
            if(isAPlayer(data["text"])):
                returnMessage = {"response_type": "in_channel", "text":"Only one game at a time!" }
                return jsonify(returnMessage)

            else:

                if(player1 == cursor.execute("select player1 from game where" +
                                             " channel=?", t).fetchone()[0] or
                    player1 == cursor.execute("select player2 " +
                                              "from game where channel=?",
                                              t).fetchone()[0]):
                    updateGameTable(cursor, t, move, player1)
                    
                    winner = gameOver(cursor, t)
                    if(winner != ""):
                        cancelGame(cursor, t)
                        connection.commit()
                        returnMessage = {"response_type": "in_channel", "text": winner + " Won!"}
                        return jsonify(returnMessage)

                    displayBoard(cursor, t)
                    # cancelGame(cursor, t)
                    
                else:
                    returnMessage = {"response_type": "in_channel", "text": "Sorry, you're not in this game:("}
                    return jsonify(returnMessage)


                    connection.commit()

        currentGame = cursor.execute("select * from game where channel=?", t)

        connection.commit()
        # if it is, then check the params to see which user made a move
        # Update the table
        # return table
        data["response-type"] = "in_channel"
        return jsonify(currentGame.fetchall())
    elif request.method == "GET":
        return "Welcome to the webpage"
    else:
        return "This shouldn't happen"


def isAPlayer(s):

    if(len(s) < 3):
        return False

    if(s[0:3] == "%40"):
        return True
    else:
        return False


def updateGameTable(cursor, data, move, player):

    # Player 1 is X
    # Player 2 is O

    # Update table with this value
    tableValue = 0
    # Figure out which player is making a move
    if(player == cursor.execute("select player1 from game where channel=?",
                                data).fetchone()[0]):
        # Player 1
        tableValue = 1
    else:
        # Player 2
        tableValue = 2

    if(move == 1):
        cursor.execute("UPDATE game SET topLeft=? WHERE channel=? AND " +
                       "topLeft=0", (tableValue, data[0]))
    elif(move == 2):
        cursor.execute("UPDATE game SET topMiddle=? WHERE channel=? AND " +
                       "topMiddle=0", (tableValue, data[0]))
    elif (move == 3):
        cursor.execute("UPDATE game SET topRight=? WHERE channel=? AND " +
                       "topRight=0", (tableValue, data[0]))
    elif(move == 4):
        cursor.execute("UPDATE game SET middleLeft=? WHERE channel=? AND" +
                       " middleLeft=0", (tableValue, data[0]))
    elif(move == 5):
        cursor.execute("UPDATE game SET center=? WHERE channel=? AND center=0",
                       (tableValue, data[0]))
    elif(move == 6):
        cursor.execute("UPDATE game SET middleRight=? WHERE channel=? AND" +
                       " middleRight=0", (tableValue, data[0]))
    elif(move == 7):
        cursor.execute("UPDATE game SET bottomLeft=? WHERE channel=? AND" +
                       " bottomLeft=0", (tableValue, data[0]))
    elif(move == 8):
        cursor.execute("UPDATE game SET bottomMiddle=? WHERE channel=? AND" +
                       " bottomMiddle=0", (tableValue, data[0]))
    elif(move == 9):
        cursor.execute("UPDATE game SET bottomRight=? WHERE channel=? AND" +
                       " bottomRight=0", (tableValue, data[0]))


def cancelGame(cursor, data):
    cursor.execute("DELETE FROM game WHERE channel=?", data)

def displayBoard(cursor, data):
    boardSlots = cursor.execute("SELECT * FROM game WHERE channel=?", data).fetchone()[4:]

    board = ""

    choices = ["| |", "|X|", "|O|"]

    for i in range(len(boardSlots)):
        if(i % 3 == 2):
            board += choices[boardSlots[i]] + "\n"
        else:
            board += choices[boardSlots[i]]

    print(board)


def gameOver(cursor, data):


    boardSlots = cursor.execute("SELECT * FROM game WHERE channel=?", data).fetchone()[4:]

    winningCombos = [[0, 1, 2], [2, 5, 8], [0, 4, 8], [3, 4, 5], [6, 7, 8],
                     [0, 3, 6], [1, 4, 7], [2, 4, 6]]

    for combo in winningCombos:

        position1 = combo[0]
        position2 = combo[1]
        position3 = combo[2]

        if(boardSlots[position1] == boardSlots[position2] and
           boardSlots[position2] == boardSlots[position3] and
           boardSlots[position1] != 0):

            if(boardSlots[position1] == 1):
                winner = cursor.execute("SELECT player1 FROM game WHERE channel=?", data).fetchone()[0]
                return winner
            else:
                winner = cursor.execute("SELECT player2 FROM game WHERE channel=?", data).fetchone()[0]
                return winner

    return ""



