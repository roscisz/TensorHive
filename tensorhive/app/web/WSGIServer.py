from flask import Flask, render_template, jsonify
from flask_vue import Vue

app = Flask(__name__,
            static_folder = "./dev/dist/static",
            template_folder = "./dev/dist")
Vue(app)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")
    
if __name__ == "__main__":
    app.run()
