from flask import Flask,render_template,send_file

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template("index.html")

@app.route('/code')
def home():
    return send_file('env_setup.py', as_attachment=True)
if __name__ == '__main__':
    app.run()
