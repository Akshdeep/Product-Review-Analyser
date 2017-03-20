from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    print request
    url = request.form['url']
    return url

if __name__ == "__main__":
    app.run()