import firebase_admin
from firebase_admin import credentials, firestore

class Database:
    def __init__(self):
        self.cred = credentials.Certificate("whatsapp-api-93771-firebase-adminsdk.json")
        firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()

    def init_user(self,chat_id, phone: str, name):
        doc_ref = self.db.collection("testing").document(chat_id)
        if doc_ref.get().exists == False:
            data = {
                "id": chat_id,
                "phone": phone,
                "name": name,
                "messages": [],
            }
            self.db.collection("testing").document(chat_id).set(data)

        return self.db.collection("testing").document(chat_id)

    def payload(self, name, text, time):
        msg = {
            f"{name}": str(text),
            "timestamp": time
        }
        return msg

    def add_convo(self, ref, msg):
        ref.update({"messages": firestore.ArrayUnion([msg])})