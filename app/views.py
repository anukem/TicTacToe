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

        if(data["text"] == ""):
            response = {"response_type": "ephemeral"}
            response["text"] = "Welcome to TicTacToe!\nIn order to start a game, please challenge someone in the channel.\nEx. /tictactoe @john"
            return jsonify(response)

        print(data)
        # Establish connection to database
        connection = sqlite3.connect("db/database.db")
        cursor = connection.cursor()

        t = (data["channel_name"],)

        try:
            table = cursor.execute("select * from game where channel=?", t)

        except:
            cursor.execute("create table game (channel varchar(256)," +
                           "inSession integer(4), player1 varchar(256), player2"
                           + " varchar(256));")

        table = cursor.execute("select * from game where channel=?", t)

        if(len(table.fetchall()) == 0):
            table = cursor.execute("INSERT INTO game VALUES(?, ?, ?, ?)",
                                   [data["channel_name"], 1, data["user_name"], "0"])

        connection.commit()

        game = cursor.execute("select * from game;")

        connection.commit()
        # if it is, then check the params to see which user made a move
        # Update the table
        # return table
        data["response-type"] = "in_channel"
        return jsonify(table.fetchall())
    elif request.method == "GET":
        return "Welcome to the webpage"
    else:
        return "This shouldn't happen"
