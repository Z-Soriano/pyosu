#run python server.py to start server, then open html file
#TODO: allow deployment rather than just local testing
from flask import Flask, request, jsonify
from flask_cors import CORS

from osu_runner import run_osu_program

app = Flask(__name__)
CORS(app)

@app.route("/run", methods=["POST"])
def run():
    data = request.get_json()
    osu_text = data["content"]

    output = run_osu_program(osu_text)

    return jsonify({"output": output})

if __name__ == "__main__":
    app.run(debug=True)