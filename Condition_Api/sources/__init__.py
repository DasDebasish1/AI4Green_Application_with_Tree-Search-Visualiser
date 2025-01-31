from flask import Flask

app = Flask(__name__)

from sources.condition_prediction import condition_prediction_bp
app.register_blueprint(condition_prediction_bp)
print("app made")

if __name__ == "__main__":
    app.run()  # to run the app in PyCharm
