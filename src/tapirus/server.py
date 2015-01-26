__author__ = 'guilherme'


from flask import Flask, Response
import json


app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello():

    data = {
        "message": "{0}".format("Greetings")
    }

    return Response(json.dumps(data), status=200, mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)