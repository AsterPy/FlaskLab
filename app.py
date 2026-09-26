from flask import Flask

app = Flask(__name__)

@app.route("/")
def main():
    return "Hellow World!"

if __name__ == "__main__":
    app.run(debug=True)