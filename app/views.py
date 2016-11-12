#!/bin/python

from app import app
from flask import request
import sqlite3
from flask import jsonify


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        # Check if game is in session
        # Make sure all preset values are accounted for
        data = request.get_data()
        data = dict(x.split("=") for x in data.split("&"))
        player1 = data["user_name"]
        player2 = ""
        # Decides if the next move is valie
        move = 0
        # Only set if a user cancels
        cancel = 0
        # Only set if someone wants to see the game without making a move
        display = 0

        # Interpret the syntax

        # Set the help text
        if(data["text"] == "" or data["text"] == "help"):
            # Intro text
            response = {"response_type": "ephemeral"}
            response["text"] = '''Welcome to TicTacToe!\nIn order to start a game,
                  please challenge someone in the channel. /ttt @john
                  \n /ttt # makes a move at the slot defined by the numbers
                  1 through 9, but only if you're in the game.\n
                  /ttt display \n displays the game board only to the user that
                  requested it as well as the current user whose turn it is.\n
                  /ttt cancel \n cancels the game. Use this if you accidentally
                   challenge yourself.'''
            return jsonify(response)

        elif(len(data["text"].split(" ")) == 1):
            # Select the challenger
            if(data["text"][0:3] == "%40"):
                player2 = data["text"][3:len(data["text"])]
            elif(len(data["text"]) == 1):
                if(data["text"].isdigit()):
                    move = int(data["text"])
                else:
                    responseMessage = {"response_type": "in_channel",
                                       "text": "Sorry I do recognize that" +
                                       " action. To start a game, please" +
                                       " type /ttt @user"}
                    return jsonify(responseMessage)
            elif(data["text"] == "cancel"):
                # Set the cancel mark and cancel the game
                cancel = 1
            elif(data["text"] == "display"):
                # Display the board
                response = {"response_type": "ephemeral"}
                display = 1
            else:
                responseMessage = {"response_type": "in_channel",
                                   "text": "Sorry I don't recognize that" +
                                   " action. To start a game, please type" +
                                   " /ttt @user"}
                return jsonify(responseMessage)

        # Establish connection to database
        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()

        # Try to create the table
        t = (data["channel_name"],)

        try:
            # Select the game if it exists and if it doesn't create it
            table = cursor.execute("select * from game where channel=?", t)

        except:

            cursor.execute('''create table game (channel varchar(256),
                            inSession integer(4), player1 varchar(256), player2
                            varchar(256), topLeft integer(4),
                           topMiddle integer(4), topRight integer(4),
                           middleLeft integer(4), center integer(4),
                            middleRight integer(4), bottomLeft integer(4),
                          bottomMiddle integer(4), bottomRight integer(4));''')

        # Check to see if the game should be cancelled or displayed
        if(cancel):
            cancelGame(cursor, t)
            connection.commit()
            returnMessage = {"response_type": "in_channel",
                             "text": "Game has been cancelled!"}
            return jsonify(returnMessage)

        if(display):
            # Figure out whose turn it is
            player = ""
            playerNum = cursor.execute("SELECT * FROM game WHERE channel=?", t).fetchone()
            if(playerNum[1] == 1):
                player = playerNum[3]
            else:
                player = playerNum[2]

            board = displayBoard(cursor, t)
            response = {"response_type": "ephemeral"}
            response["text"] = "The board is currently: \n" + board + "\nIt's "
            + player + "'s turn!\n"
            return jsonify(response)

        currentGame = cursor.execute("select * from game where channel=?", t)

        if(len(currentGame.fetchall()) == 0 and player2 != ""):
            # No game has been made
            currentGame = cursor.execute("INSERT INTO game VALUES(?, ?, ?, ?" +
                                         ", ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                         [data["channel_name"],
                                          1, player1, player2, 0, 0, 0, 0,
                                          0, 0, 0, 0, 0])
            connection.commit()
            # Create New Game
            responseMessage = {"response_type": "in_channel", "text":
                               "You've challenged " + player2 + "!" +
                               "The board is currently:\n|1|2|3|\n" +
                               "|4|5|6|\n" +
                               "|7|8|9|\n"}
            return jsonify(responseMessage)
        else:
            # Check to see if the player is making correct move
            if(isAPlayer(data["text"])):
                returnMessage = {"response_type": "in_channel",
                                 "text": "Only one game at a time!"}
                return jsonify(returnMessage)

            else:
                # Check to see if board is in play
                try:
                    currentBoard = displayBoard(cursor, t)
                except TypeError:
                    returnMessage = {"response_type": "ephemeral",
                                     "text": "*No game in session*"}
                    return jsonify(returnMessage)

                # Update the table and determine a winner if there is one
                updateGameTable(cursor, t, move, player1)
                connection.commit()
                winner = gameOver(cursor, t)
                updatedBoard = displayBoard(cursor, t)
                if(winner != ""):
                    cancelGame(cursor, t)
                    connection.commit()
                    if(winner == "tie"):
                        returnMessage = {"response_type": "in_channel",
                                         "text": "It's a tie!"}
                    else:
                        returnMessage = {"response_type": "in_channel",
                                         "text": winner + " won!\n" +
                                         updatedBoard}
                    return jsonify(returnMessage)

                if(currentBoard != updatedBoard):
                    # Figure out whose turn it is
                    player = ""
                    playerNum = cursor.execute("SELECT * FROM game WHERE channel=?", t).fetchone()
                    if(playerNum[1] == 1):
                        player = playerNum[3]
                    else:
                        player = playerNum[2]

                    returnMessage = {"response_type": "in_channel", "text":
                                     "The board is currently:\n" +
                                     displayBoard(cursor, t) + "\nIt's " +
                                     player + "'s turn!\n "}
                    return jsonify(returnMessage)
                else:
                    returnMessage = {"response_type": "ephemeral", "text":
                                     '''*Sorry, its either not your turn, or 
                                     you're not in the game or you made an
                                     illegal move*'''}
                    return jsonify(returnMessage)

    elif request.method == "GET":
        return "Welcome to the webpage"
    else:
        return table


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
        cursor.execute("UPDATE game SET topLeft=?, inSession=?" +
                       " WHERE channel=? AND topLeft=0 AND inSession!=?",
                       (tableValue, tableValue, data[0], tableValue))
    elif(move == 2):
        cursor.execute("UPDATE game SET topMiddle=?, inSession=?" +
                       " WHERE channel=? AND topMiddle=0 AND inSession!=?",
                       [tableValue, tableValue, data[0], tableValue])
    elif (move == 3):
        cursor.execute("UPDATE game SET topRight=?, inSession=?" +
                       " WHERE channel=? AND topRight=0 AND inSession!=?",
                       [tableValue, tableValue, data[0], tableValue])
    elif(move == 4):
        cursor.execute("UPDATE game SET middleLeft=?, inSession=?" +
                       " WHERE channel=? AND middleLeft=0 AND inSession!=?",
                       [tableValue, tableValue, data[0], tableValue])
    elif(move == 5):
        cursor.execute("UPDATE game SET center=?, inSession=?" +
                       " WHERE channel=? AND center=0 AND inSession!=?",
                       [tableValue, tableValue, data[0], tableValue])
    elif(move == 6):
        cursor.execute("UPDATE game SET middleRight=?, inSession=?" +
                       " WHERE channel=? AND middleRight=0 AND inSession!=?",
                       [tableValue, tableValue, data[0], tableValue])
    elif(move == 7):
        cursor.execute("UPDATE game SET bottomLeft=?, inSession=?" +
                       " WHERE channel=? AND bottomLeft=0 AND inSession!=?",
                       [tableValue, tableValue, data[0], tableValue])
    elif(move == 8):
        cursor.execute("UPDATE game SET bottomMiddle=?, inSession=?" +
                       " WHERE channel=? AND bottomMiddle=0 AND inSession!=?",
                       [tableValue, tableValue, data[0], tableValue])
    elif(move == 9):
        cursor.execute("UPDATE game SET bottomRight=?, inSession=?" +
                       " WHERE channel=? AND bottomRight=0 AND inSession!=?",
                       [tableValue, tableValue, data[0], tableValue])


def cancelGame(cursor, data):
    cursor.execute("DELETE FROM game WHERE channel=?", data)


def displayBoard(cursor, data):

    boardSlots = cursor.execute("SELECT * FROM game WHERE channel=?", data).fetchone()[4:]

    board = ""

    choices = ["*|*       *|*", "*|*:heavy_multiplication_x:*|*",
               "*|*:radio_button:*|*"]

    for i in range(len(boardSlots)):
        if(i % 3 == 2):
            board += choices[boardSlots[i]] + "\n"
        else:
            board += choices[boardSlots[i]] + " "

    return board


def gameOver(cursor, data):

    boardSlots = cursor.execute("SELECT * FROM game" +
                                " WHERE channel=?", data).fetchone()[4:]

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
                winner = cursor.execute("SELECT player1 FROM game" +
                                        " WHERE channel=?", data).fetchone()[0]
                return winner
            else:
                winner = cursor.execute("SELECT player2 FROM game" +
                                        " WHERE channel=?", data).fetchone()[0]
                return winner

    if(0 not in boardSlots):
            return "tie"

    return ""
