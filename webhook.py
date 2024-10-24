
from flask import Flask, request, jsonify
from Conversational_Bot.db_store import Database
from date import format_ms, current_time

db = Database()

app = Flask(__name__)

@app.route('/')
def home():
    return 'The webhook is working fine.'

@app.route('/user_store',methods={'POST'})
def store_user():
    data = request.json
    print(data)

    if data['entry'][0]['changes'][0]['value']['messages'][0]['type'] == 'text':
        id = data['entry'][0]['id']
        name = data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
        phone = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        wa_id = data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        time = data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']

        doc_ref = db.init_user(wa_id, id, phone, name)
        msg_info = db.payload(name, msg, format_ms(time))
        db.add_convo(doc_ref, msg_info)

    return jsonify(status='success'), 200

@app.route('/',methods=['POST'])
def store_reply():
    data = request.json
    wa_id = data    #JSON path for wa_id in Express Request Body
    msg = data  #JSON path for LLM response

    doc_ref = db.init_user(wa_id=wa_id)
    msg_info = db.payload("Bot", msg, current_time())
    db.add_convo(doc_ref, msg_info)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)