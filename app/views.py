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

        if(data["text"] == ""):
            response = {"response_type": "ephemeral"}
            response["text"] = "Welcome to TicTacToe!\nIn order to start a game, please challenge someone in the channel.\nEx. /tictactoe @john"
            return jsonify(response)

        elif(len(data["text"].split(" ")) == 1):
            if(data["text"][0:3] == "%40"):
                player2 = data["text"][3:len(data["text"])]

        # Establish connection to database
        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()

        # Try to create the table
        t = (data["channel_name"],)

        try:
            table = cursor.execute("select * from game where channel=?", t)

        except:
            cursor.execute("create table game (channel varchar(256)," +
                           "inSession integer(4), player1 varchar(256), player2"
                           + " varchar(256));")

        # Get current game
        currentGame = cursor.execute("select * from game where channel=?", t)

        if(len(currentGame.fetchall()) == 0):
            # No game has been made
            currentGame = cursor.execute("INSERT INTO game VALUES(?, ?, ?, ?)",
                                         [data["channel_name"],
                                          1, player1, player2])
            connection.commit()
            responseMessage = {"response_type": "in_channel", "text": "You've challenged " + player2 + "!"}
            return jsonify(responseMessage)
        else:
            # Check to see if the players are correct
            if(player2 != cursor.execute("select player2 from game where channel=?", t).fetchone()[0]):
                returnMessage = {"response_type": "ephemeral", "text": "Only one game per channel (:"}
                return jsonify(returnMessage)

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
