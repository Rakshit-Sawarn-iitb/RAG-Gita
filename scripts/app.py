import flask_cors
import flask
from chat import GetAnswer

app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.route('/api/qa', methods=['POST'])
def GetAnswerAPI():
    data = flask.request.json
    query = data['query']
    response = GetAnswer(query)
    return flask.jsonify({'response': response})

if __name__ == '__main__':
    app.run(port=5000)
    debug=True