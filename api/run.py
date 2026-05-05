# # from flask import Flask, request, jsonify
# # from osu_runner import run_osu_program

# # app = Flask(__name__)

# # # @app.route("/api/run", methods=["POST"])
# # # def run():
# # #     data = request.get_json()
# # #     output = run_osu_program(data.get("content", ""))
# # #     return jsonify({"output": output})
# # # @app.route("/api/run", methods=["POST"])
# # def run():
# #     try:
# #         data = request.get_json()
# #         osu_text = data.get("content", "")

# #         output = run_osu_program(osu_text)

# #         return jsonify({"output": output})
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# from flask import Flask, request, jsonify
# from osu_runner import run_osu_program

# app = Flask(__name__)

# @app.route("/", methods=["POST"])
# def run():
#     try:
#         data = request.get_json()
#         osu_text = data.get("content", "")
#         output = run_osu_program(osu_text)
#         return jsonify({"output": output})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
from http.server import BaseHTTPRequestHandler
import json

from osu_runner import run_osu_program


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("content-length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            output = run_osu_program(data.get("content", ""))

            response = json.dumps({"output": output}).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response)

        except Exception as e:
            response = json.dumps({"error": str(e)}).encode("utf-8")

            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response)